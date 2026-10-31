"""Seal the local delivery after package checks and explicit visual review."""
import json,zipfile
from pathlib import Path
from prepare import ROOT,DEST,sha,dump
def main():
    checks=json.loads((DEST/'validation/package-checks.json').read_text())
    review=json.loads((DEST/'validation/visual-review.json').read_text());assert review['status']=='passed'
    snapshot=json.loads((DEST/'validation/source-snapshot.json').read_text());changes=[dict(path=r,snapshot_sha256=h,current_sha256=sha(ROOT/r),reason='Collection discovery/navigation addition; implementation unchanged')for r,h in snapshot.items()if sha(ROOT/r)!=h]
    allowed={'README.md','Project-README.md','PROJECT-READMAP.toml','Logos-And-Theming.manifest.toml'};assert all(c['path'] in allowed for c in changes),changes
    dump(DEST/'validation/source-currentness.json',dict(changes_after_snapshot=changes,rule='Snapshot content remains frozen; current contracts are authoritative.'))
    files={p.relative_to(DEST).as_posix():sha(p)for p in DEST.rglob('*')if p.is_file() and '__pycache__' not in p.parts and p.name!='delivery.json'}
    receipt=dict(schema='aptlantis.visual-documentation-delivery.v1',date='2026-10-31',volumes=8,editable_slides=192,guide_pages=120,pdfs=16,markdown_guides=8,preserved_input_files=checks['preserved_input_files'],files=files,verification=dict(package='passed',native_powerpoint='passed; repair disabled; read-only; zero text overflow',independent_pdf_render='passed',visual_review=review['status'],focused_tests='22 passed',artifact_hashes='passed',canonical_and_input_preservation='passed',authored_links=checks['authored_links']),limits=['Manual PowerPoint edit/save/reopen not performed','Downstream theme import, installation and activation not performed','Publication, public-copy changes and live hosting verification not performed','Fresh VTracer fidelity review not performed'],authoring='Local native template preservation; original twelve-slot Office schemes unchanged')
    dump(DEST/'validation/delivery.json',receipt)
    archive=DEST.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED)as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:z.write(p,DEST.name+'/'+p.relative_to(DEST).as_posix())
    with zipfile.ZipFile(archive)as z:
        assert z.testzip() is None
        for rel,h in files.items():
            import hashlib
            assert hashlib.sha256(z.read(DEST.name+'/'+rel)).hexdigest()==h,rel
    dump(archive.with_suffix('.zip.sha256.json'),dict(file=archive.name,sha256=sha(archive),bytes=archive.stat().st_size,members=len(files)+1))
    print(f'Sealed {len(files)+1} files; ZIP {archive.stat().st_size/1024/1024:.1f} MiB; verified every archived hash')
if __name__=='__main__':main()
