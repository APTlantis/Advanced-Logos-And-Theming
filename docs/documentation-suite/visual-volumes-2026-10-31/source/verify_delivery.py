"""Validate packages, palette paints, preservation, portable links, and PDFs."""
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote,urlsplit
from xml.etree import ElementTree as ET
from pypdf import PdfReader
from pptx import Presentation
import json,re,posixpath,subprocess,sys
from prepare import ROOT,DEST,sha,dump
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
def main():
    baseline=json.loads((DEST/'validation/input-inventory.json').read_text());changed=[rel for rel,h in baseline.items()if not (ROOT/rel).is_file() or sha(ROOT/rel)!=h]
    assert not changed,changed
    # Also reject additions to source-run trees.
    names={Path(r).parts[1]for r in baseline};current={p.relative_to(ROOT).as_posix()for n in names for p in (ROOT/'output'/n).rglob('*')if p.is_file()};assert current==set(baseline)
    inventory=json.loads((DEST/'validation/template-inventory.json').read_text());build=json.loads((DEST/'validation/build.json').read_text());records=[];links=[]
    for item,b in zip(inventory,build):
        directory=DEST/item['stem'];deck=DEST/b['file'];prs=Presentation(deck);assert len(prs.slides)==24
        assert (prs.slide_width,prs.slide_height)==(12192000,6858000)
        colors={v['hex'].lstrip('#').upper()for v in item['palette'].values()}
        for path in (directory/'artifacts').rglob('*-tokens.json'):
            t=json.loads(path.read_text());colors.update(c['hex'].lstrip('#').upper()for c in t['tokens'].values())
        with ZipFile(deck) as z,ZipFile(ROOT/item['powerpoint']['template']) as original:
            protected=[n for n in original.namelist()if n.startswith(('ppt/theme/','ppt/slideMasters/','ppt/slideLayouts/','ppt/media/'))]
            for name in protected:assert z.read(name)==original.read(name),name
            for name in z.namelist():
                if name.endswith('.xml'):ET.fromstring(z.read(name))
                if name.endswith('.rels'):
                    relroot=ET.fromstring(z.read(name));owner=posixpath.dirname(posixpath.dirname(name))
                    for rel in relroot:
                        if rel.get('TargetMode')=='External':continue
                        target=rel.get('Target');resolved=posixpath.normpath(posixpath.join(owner,target))if not target.startswith('/')else target[1:];assert resolved in z.namelist(),(name,resolved)
            for slide in prs.slides:
                assert slide.has_notes_slide and 'SHA-256' in slide.notes_slide.notes_text_frame.text
                paints=[c.get('val')for c in slide._element.findall('.//a:srgbClr',NS)]
                assert all(c.upper() in colors for c in paints),set(paints)-colors
                for sh in slide.shapes:
                    assert sh.left>=0 and sh.top>=0 and sh.left+sh.width<=prs.slide_width+10 and sh.top+sh.height<=prs.slide_height+10,(deck.name,sh.name)
        for manifest in (directory/'artifacts').rglob('*-files.json'):
            for e in json.loads(manifest.read_text())['files']:assert sha(manifest.parent/e['file'])==e['sha256']
        pdfs=sorted(directory.glob('*.pdf'));assert len(pdfs)==2
        pages={}
        for pdf in pdfs:
            reader=PdfReader(pdf);count=len(reader.pages);expected=15 if pdf.stem.endswith('-guide')else 24;assert count==expected,(pdf,count)
            assert all(len(p.extract_text().strip())>20 for p in reader.pages)
            pages[pdf.name]=count
            if '--render-pdfs' in sys.argv:
                prefix=directory/'pdf-previews'/(pdf.stem+'-page')
                p=subprocess.run(['pdftoppm','-scale-to','1280','-png',str(pdf),str(prefix)],capture_output=True,text=True)
                assert p.returncode==0,p.stderr
        records.append(dict(file=deck.relative_to(DEST).as_posix(),slides=24,notes=24,protected_design_parts=len(protected),native_tables=sum(sh.has_table for s in prs.slides for sh in s.shapes),editable_shapes=sum(not sh.shape_type==13 for s in prs.slides for sh in s.shapes),pdf_pages=pages,sha256=sha(deck)))
    # Check portable navigation and authored Markdown. Raw source snapshots retain original context.
    authored=[DEST/'index.html',DEST/'README.md']+list(DEST.glob('*/index.html'))+list(DEST.glob('*/*-guide.md'))
    for path in authored:
        if not path.exists():continue
        source=path.read_text(encoding='utf-8')
        refs=re.findall(r'(?:href|src)="([^"]+)"',source)if path.suffix=='.html'else re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',source)
        for ref in refs:
            parsed=urlsplit(ref)
            if parsed.scheme or ref.startswith('#'):continue
            target=(path.parent/unquote(parsed.path)).resolve();assert target.is_relative_to(DEST),target
            assert target.exists(),(path.relative_to(DEST),ref)
            links.append(dict(owner=path.relative_to(DEST).as_posix(),target=target.relative_to(DEST).as_posix()))
    native=json.loads((DEST/'validation/native.json').read_text(encoding='utf-8-sig'));assert len(native)==8 and all(not r['overflow'] and r['repair']==False and r['slides']==24 for r in native)
    browser=json.loads((DEST/'validation/specimen-browser.json').read_text());assert all(not r['errors'] and not r['externalRequests']for r in browser)
    tests=json.loads((DEST/'validation/focused-tests.json').read_text());assert tests['exit_code']==0
    dump(DEST/'validation/package-checks.json',dict(preserved_input_files=len(baseline),changed_inputs=changed,source_run_additions=[],volumes=records,authored_links=len(links),specimen_previews=len(browser),manual_edit_save_reopen='not performed',downstream_native_import='not performed',publication='not performed'))
    dump(DEST/'validation/links.json',links)
    print(f'Passed: {len(records)} decks, 192 slides, 16 PDFs, {len(links)} authored links; {len(baseline)} inputs unchanged')
if __name__=='__main__':main()
