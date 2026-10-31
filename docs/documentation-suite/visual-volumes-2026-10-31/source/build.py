"""Local template-preserving PowerPoint and separately typeset guide authoring.

Authoring dependencies: python-pptx, Pillow, reportlab, lxml, pypdf.
Never invoked by apt-theme. Inputs are captured by prepare.py.
"""
from pathlib import Path
from copy import deepcopy
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,html,textwrap,sys,re
from xml.etree import ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
from pptx import Presentation
from pptx.util import Inches,Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE,MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from content import VOLUMES
from prepare import ROOT,DEST,sha,dump

FONT=Path('C:/Windows/Fonts')
pdfmetrics.registerFont(TTFont('Arial',str(FONT/'arial.ttf')))
pdfmetrics.registerFont(TTFont('Arial-Bold',str(FONT/'arialbd.ttf')))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
def rgb(c):return RGBColor.from_string(c.lstrip('#'))
def text(s,x,y,w,h,value,size,color,bold=False,font='Arial'):
    sh=s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h));sh.name='Documentation text'
    f=sh.text_frame;f.word_wrap=True;f.margin_left=f.margin_right=0;f.margin_top=f.margin_bottom=0
    for i,line in enumerate(value.split('\n')):
        p=f.paragraphs[0] if i==0 else f.add_paragraph();p.text=line;p.font.name=font;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=rgb(color);p.space_after=Pt(7)
    return sh
def rect(s,x,y,w,h,color,ellipse=False):
    sh=s.shapes.add_shape(MSO_SHAPE.OVAL if ellipse else MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h));sh.fill.solid();sh.fill.fore_color.rgb=rgb(color);sh.line.fill.background();return sh
def picture(s,p,x,y,w,h):
    im=Image.open(p);iw,ih=im.size;scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale
    return s.shapes.add_picture(str(p),Inches(x+(w-dw)/2),Inches(y+(h-dh)/2),width=Inches(dw),height=Inches(dh))
def pilfont(n,bold=False):return ImageFont.truetype(str(FONT/('arialbd.ttf' if bold else 'arial.ttf')),n)
def clean_color(c):return tuple(bytes.fromhex(c.lstrip('#')))
def luminance(h):
    a=[v/255 for v in clean_color(h)];a=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in a];return sum(x*y for x,y in zip(a,[.2126,.7152,.0722]))
def contrast(a,b):x,y=sorted([luminance(a),luminance(b)]);return (y+.05)/(x+.05)
def readable(c,t):return c if contrast(c,t)>=4.5 else ('#'+('FEFEFE' if luminance(t)<.2 else '000000'))
def wrap(draw,value,font,width):
    lines=[]
    for line in value.split('\n'):
        current=''
        for word in line.split():
            candidate=(current+' '+word).strip()
            if draw.textlength(candidate,font=font)>width and current:lines.append(current);current=word
            else:current=candidate
        lines.append(current)
    return lines
def ptext(draw,xy,value,font,fill,width,spacing=9):
    x,y=xy
    for line in wrap(draw,value,font,width):draw.text((x,y),line,font=font,fill=fill);y+=font.size+spacing
    return y

def data_for(item):
    run=ROOT/'output'/item['run'];r=json.loads((run/'run.json').read_text()); targets={}
    for target,rel in r['artifact_manifests'].items():
        m=json.loads((run/rel).read_text()); entry=next(e for e in m['files'] if e['role']=='tokens' and e['file'].endswith('.json'));targets[target]=json.loads((run/Path(rel).parent/entry['file']).read_text())
    sem=json.loads((run/'semantics.json').read_text());t=targets['powerpoint']['tokens']
    return dict(run=r,targets=targets,roles=sem['roles'],findings=sem.get('findings',[]),bg=t['background']['hex'],fg=t['foreground']['hex'],accent=t['primary']['hex'],secondary=t['secondary']['hex'],panel=t['panel']['hex'])

def palette_figure(item,d,out):
    im=Image.new('RGB',(1600,1000),d['bg']);draw=ImageDraw.Draw(im)
    ptext(draw,(60,35),'The complete canonical 32',pilfont(54,True),d['fg'],1480)
    for i,(key,c) in enumerate(item['palette'].items()):
        x=60+(i%8)*188;y=160+(i//8)*188;draw.rectangle((x,y,x+170,y+108),fill=c['hex']);draw.text((x,y+118),key,font=pilfont(23),fill=d['fg']);draw.text((x,y+148),c['hex'],font=pilfont(22),fill=d['fg'])
    draw.text((60,940),f"{item['stem']} / exact palette.toml values / lightness order",font=pilfont(25),fill=d['fg']);im.save(out)
def plot_figure(item,d,out):
    im=Image.new('RGB',(1600,900),d['bg']);dr=ImageDraw.Draw(im)
    dr.text((60,35),'Lightness across the canonical palette',font=pilfont(48,True),fill=d['fg'])
    for v in [0,.25,.5,.75,1]:
        y=730-v*540;dr.line((110,y,1520,y),fill=d['panel'],width=3);dr.text((28,y-16),f'{v:.2f}',font=pilfont(24),fill=d['fg'])
    for i,(key,c) in enumerate(item['palette'].items()):
        l=c['oklch']['l'];x=120+i*43;y=730-l*540;dr.rectangle((x,y,x+30,730),fill=c['hex']);dr.text((x,750),f'{i+1:02}',font=pilfont(20),fill=d['fg'])
    dr.text((110,820),'OKLCH L (0–1). Exact recorded values; this is not an aesthetic score.',font=pilfont(27),fill=d['fg']);im.save(out)
def lineage(item,d):
    role='primary';key=d['roles'][role];c=item['palette'][key];t=d['targets']['powerpoint']['tokens'][role]
    return [key,c['hex'],'primary',t['hex'],'accent1'], f"{key} {c['hex']} maps to primary; PowerPoint emits {t['hex']}; derived={str(t['origin']['derived']).lower()}. Office accent1 binds primary."
def diagram_figure(labels,d,out,title='Recorded workflow'):
    im=Image.new('RGB',(1600,560),d['bg']);dr=ImageDraw.Draw(im);ptext(dr,(60,30),title,pilfont(44,True),d['fg'],1480)
    cols=[c['hex'] for c in d['targets']['powerpoint']['tokens'].values() if c['hex'] not in [d['bg'],d['fg']]]
    n=len(labels);width=1440/n
    for i,label in enumerate(labels):
        x=70+i*width;c=cols[i%len(cols)];dr.rectangle((x,170,x+width-30,190),fill=c)
        dr.text((x,225),f'{i+1:02}',font=pilfont(64,True),fill=d['fg']);ptext(dr,(x,325),label,pilfont(28,True),d['fg'],width-35)
    im.save(out)

def add_slide(prs,d,title,num,cover=False,original=None):
    if cover:
        slide=prs.slides.add_slide(original.slide_layout)
        for sh in list(slide.shapes):sh._element.getparent().remove(sh._element)
        # Native ring artwork is retained as editable shapes from the actual source cover.
        for sh in original.shapes:
            if not sh.has_text_frame:slide.shapes._spTree.insert_element_before(deepcopy(sh._element),'p:extLst')
    else:
        slide=prs.slides.add_slide(prs.slide_layouts[13])
        for sh in list(slide.shapes):sh._element.getparent().remove(sh._element)
    slide.background.fill.solid();slide.background.fill.fore_color.rgb=rgb(d['bg'])
    if not cover:text(slide,.6,.35,12.05,.9,title,30,d['fg'],True)
    text(slide,.6,7.08,11,.24,'Logos-And-Theming  /  documentation snapshot 2026-10-31',9,d['fg'])
    text(slide,12,7.02,.7,.3,f'{num:02}',12,d['fg'])
    return slide
def flow(slide,labels,d,y=3.0):
    colors=[c['hex'] for c in d['targets']['powerpoint']['tokens'].values() if c['hex'] not in [d['bg'],d['fg']]]
    n=len(labels);step=12.0/n
    for i,label in enumerate(labels):
        x=.65+i*step;col=colors[(i*3)%len(colors)];rect(slide,x,y,step-.22,.10,col);text(slide,x,y+.30,step-.25,.7,f'{i+1:02}',38,d['fg'],True);text(slide,x,y+1.15,step-.28,1.05,label,20,d['fg'],True)
def concept(slide,labels,d,index,body):
    colors=[c['hex']for c in d['targets']['powerpoint']['tokens'].values()if c['hex'] not in [d['bg'],d['fg']]]
    mode=index%3
    if mode==0:flow(slide,labels,d,3.1)
    elif mode==1:
        for j,label in enumerate(labels):
            y=2.9+j*.72;rect(slide,.7,y,.22,.48,colors[(j*3)%len(colors)]);text(slide,1.12,y,5.5,.55,label,23,d['fg'],True)
        text(slide,7,3.0,5.2,2.7,body.split('. ')[0]+'.',23,d['fg'])
    else:
        for j,label in enumerate(labels):
            x=.7+(j%2)*6.1;y=2.95+(j//2)*1.5;c=colors[(j*3)%len(colors)]
            rect(slide,x,y,.6,.6,c,True);text(slide,x+.85,y+.05,4.8,1.05,label,24,d['fg'],True)
def source_notes(s,explanation,refs,item):
    sources=json.loads((DEST/'validation/source-snapshot.json').read_text())
    lines=[explanation,'','Documentation snapshot: 2026-10-31. Historical acceptance retains its original date.','Native editing/save/reopen and downstream theme activation are not established by this slide.','','Source references:']
    for ref in refs:lines.append(f'{ref}\nSHA-256: {sources[ref]}')
    lines.append(f"Physical source run: output/{item['run']}\nSource artwork SHA-256: {item['palette'] and json.loads((ROOT/'output'/item['run']/'run.json').read_text())['source_sha256']}")
    s.notes_slide.notes_text_frame.text='\n'.join(lines)

def build_deck(item,v,d,replace=False):
    directory=DEST/item['stem'];stem=f"{item['stem']}-{v['topic']}";output=directory/(stem+'.pptx')
    if output.exists() and not replace:raise FileExistsError(output)
    prs=Presentation(ROOT/item['powerpoint']['sample']);originals=list(prs.slides);spec=[]
    assert (prs.slide_width,prs.slide_height)==(12192000,6858000)
    def slide(title,body,kind,cover=False):
        s=add_slide(prs,d,title,len(spec)+1,cover,originals[0]);spec.append(dict(number=len(spec)+1,title=title,explanation=body,kind=kind,sources=v['refs']));source_notes(s,body,v['refs'],item);return s
    s=slide(v['title'],v['subtitle'],'cover',True)
    text(s,.65,.9,7.5,.5,item['stem'],20,d['fg']);text(s,.65,2.05,7.6,2.0,v['title'],40,d['fg'],True);text(s,.65,4.4,7.1,1.2,v['subtitle'],23,d['fg']);text(s,.65,6.15,9,.5,'Visual volume  /  editable diagrams and source-backed examples',14,d['fg'])
    s=slide('Choose your reading route','Start with visuals, continue into examples, and use the guide and source records for deeper inspection.','route');flow(s,['See the source','Follow the color','Explore outputs','Inspect evidence'],d,2.5);text(s,.65,1.45,11.8,.7,'Slides explain the story. The guide carries procedures, limits, and references.',23,d['fg'])
    s=slide('Begin with the actual artwork','This image is the preserved source from the selected run, not recreated artwork.','artwork');art=directory/'figures'/Path(item['artwork']).name;picture(s,art,6.6,1.4,5.9,5.3)
    text(s,.65,1.65,5.5,1.2,item['run'],32,d['fg'],True);text(s,.65,3.1,5.3,2.3,'Original input bytes remain preserved.\nThe generation prefix records artwork identity.\nThe source hash is attached in speaker notes.',22,d['fg']);text(s,.65,6.3,5.3,.45,'Source: '+Path(item['artwork']).name,12,d['fg'])
    s=slide('All 32 canonical colors remain available','Every tile uses the exact recorded canonical RGB value. IDs belong to this palette.','palette')
    for i,(key,c) in enumerate(item['palette'].items()):
        x=.65+(i%8)*1.53;y=1.55+(i//8)*1.24;rect(s,x,y,1.32,.66,c['hex']);text(s,x,y+.72,1.4,.22,key,11,d['fg']);text(s,x,y+.95,1.4,.22,c['hex'],11,d['fg'])
    s=slide('Fifteen destinations, measured token counts','These counts come from the selected run, not target budget defaults.','target-table')
    table=s.shapes.add_table(16,3,Inches(.7),Inches(1.5),Inches(7.5),Inches(5.1)).table
    for c,w in zip(table.columns,[4.5,1.5,1.5]):c.width=Inches(w)
    rows=[['Target','Named','Unique']]+[[k,str(t['named_count']),str(t['unique_count'])]for k,t in d['targets'].items()]
    for ri,row in enumerate(rows):
        for ci,value in enumerate(row):
            cell=table.cell(ri,ci);cell.text=value;cell.fill.solid();cell.fill.fore_color.rgb=rgb(d['panel'] if ri else d['bg']);cell.margin_top=cell.margin_bottom=Inches(.015)
            for p in cell.text_frame.paragraphs:p.font.name='Arial';p.font.size=Pt(12);p.font.color.rgb=rgb(d['fg']);p.font.bold=ri==0
    text(s,8.65,2.05,3.7,1.15,'Named tokens can share a color.',28,d['fg'],True);text(s,8.65,3.65,3.7,1.8,'Aliases are intentional. Budgets are limits, not a requirement to fill every slot.',21,d['fg'])
    labels,line=lineage(item,d);s=slide('Follow one recorded color into Office',line,'lineage');flow(s,[labels[0]+'\n'+labels[1],labels[2],labels[3],labels[4]],d,2.6);text(s,.65,1.5,12,.7,'Canonical identity  /  semantic purpose  /  target value  /  native binding',21,d['fg']);text(s,.65,6.25,12,.5,line,13,d['fg'])
    specimen_map={'artwork-to-applications':{7:'svg'},'canonical-32':{},'semantic-interfaces':{},'themes-on-web':{4:'website'},'writing-in-color':{1:'markdown',6:'codemirror5',7:'codemirror6'},'visual-collection':{7:'svg',8:'data_visualization'},'artwork-custody':{},'safe-operation':{}}
    for i,(title,lead,body,rawlabels) in enumerate(v['chapters']):
        labels=rawlabels.split('|');kind='specimen' if i in specimen_map[v['topic']] else ('plot' if v['topic']=='canonical-32' and i==4 else ('statement' if i%4==1 else 'flow'))
        s=slide(title,body,kind)
        if kind=='specimen':
            image=directory/'figures'/(specimen_map[v['topic']][i]+'-specimen.png');picture(s,image,5.7,1.55,6.95,4.7);text(s,.65,1.65,4.65,1.9,lead,25,d['fg'],True);text(s,.65,3.8,4.6,2.3,'\n'.join(labels),21,d['fg']);text(s,5.8,6.38,6.7,.35,('Illustrative fixture. ' if 'data_visualization' in image.name else 'Actual generated specimen. ')+'Copied bytes; Chromium preview.',11,d['fg'])
        elif kind=='plot':
            text(s,.65,1.45,12,.7,lead,25,d['fg'],True)
            text(s,.7,2.4,2.2,3.8,'Crystal canonical values\n\nHue versus lightness\n\nNear-neutral colors shown separately',18,d['fg'])
            for val in [0,.25,.5,.75,1]:
                y=6.15-val*3.5;rect(s,3.3,y,8.9,.015,d['panel']);text(s,2.8,y-.12,.45,.3,str(val),10,d['fg'])
            for key,c in item['palette'].items():
                l=c['oklch']['l'];ch=c['oklch']['c'];h=c['oklch']['h'];x=3.5+(h/360)*8.3 if ch>=.02 else 12.3;y=6.15-l*3.5;rect(s,x,y,.13,.13,c['hex'],True)
            text(s,3.3,6.5,8.9,.3,'Hue 0–360 degrees / vertical axis: OKLCH lightness 0–1',12,d['fg'])
        elif kind=='statement':
            text(s,.7,1.7,11.8,1.7,lead,34,d['fg'],True)
            for j,label in enumerate(labels):
                x=.7+j*(12/len(labels));c=list(item['palette'].values())[min(31,8+j*6)]['hex'];rect(s,x,4.0,12/len(labels)-.25,.19,c);text(s,x,4.65,12/len(labels)-.3,1.4,label,22,d['fg'])
            text(s,.7,6.42,11.8,.3,'See the illustrated guide and speaker notes for the complete explanation.',12,d['fg'])
        else:
            text(s,.65,1.45,12,1.1,lead,26,d['fg'],True);concept(s,labels,d,i,body);text(s,.65,6.45,12,.3,'Evidence and limitations: '+v['refs'][i%len(v['refs'])],12,d['fg'])
    s=slide('Keep the image, the explanation, and the evidence together','Use the source records to inspect claims and the native files to begin a separate acceptance review.','recap');flow(s,['Preserve identity','Read exact values','Review in context','Record the gate'],d,2.9);text(s,.65,1.55,12,.9,'The palette stays inspectable from artwork to application.',29,d['fg'],True)
    s=slide('Continue with the guide and recorded sources','The offline index links guides, copied artifacts, previews, and validation receipts.','references')
    text(s,.7,1.55,11.8,1.1,'Read the illustrated guide for worked examples and acceptance checks.',25,d['fg'],True);text(s,.7,2.8,11.7,2.7,'\n'.join(v['refs']),20,d['fg'],font='Courier New');text(s,.7,6.12,11.7,.5,'Current source contracts take precedence over this dated documentation snapshot.',16,d['fg'])
    assert len(spec)==24
    for e in list(prs.slides._sldIdLst)[:len(originals)]:prs.part.drop_rel(e.rId);prs.slides._sldIdLst.remove(e)
    prs.core_properties.title=v['title'];prs.core_properties.author='Aptlantis';prs.core_properties.subject='Visual documentation volume, 2026-10-31';prs.core_properties.keywords=item['stem']+'; canonical 32; local pilot'
    prs.save(output)
    # Restore protected native design parts after XML serialization.
    with ZipFile(ROOT/item['powerpoint']['sample']) as z:preserved={n:z.read(n)for n in z.namelist()if n.startswith(('ppt/theme/','ppt/slideMasters/','ppt/slideLayouts/','ppt/media/'))}
    with ZipFile(ROOT/item['powerpoint']['template']) as z:
        for n,b in preserved.items():assert z.read(n)==b,n
    with ZipFile(output) as z:parts={n:z.read(n)for n in z.namelist()}
    parts.update(preserved)
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for n,b in parts.items():z.writestr(n,b)
    dump(DEST/'source/specifications'/(stem+'.json'),dict(title=v['title'],stem=item['stem'],topic=v['topic'],slides=spec,template=item['powerpoint'],design_changes='Original theme/master/layout/media parts preserved exactly. Original editable ring artwork reused on cover. New slide geometry, native tables, diagrams, explicit recorded canonical/token colors, and actual specimen pictures.',fontPolicy=dict(basis='reference',families=['Arial','Courier New'],reference=item['powerpoint']['sample']),protected_parts=len(preserved)))
    return stem

class GuidePDF:
    def __init__(self,path,v,d):
        self.c=canvas.Canvas(str(path),pagesize=(612,792));self.c.setTitle(v['title']+' — illustrated guide');self.c.setAuthor('Aptlantis');self.d=d;self.v=v;self.page=0
    def new(self,title):
        if self.page:self.c.showPage()
        self.page+=1;c=self.c;d=self.d;c.setFillColor(HexColor(d['bg']));c.rect(0,0,612,792,fill=1,stroke=0);self.p(title,48,738,516,24,True);c.setFillColor(HexColor(d['fg']));c.setFont('Arial',8);c.drawString(48,28,'Logos-And-Theming / documentation snapshot 2026-10-31');c.drawRightString(564,28,str(self.page))
    def p(self,value,x,y,w,size=11,bold=False):
        style=ParagraphStyle('body',fontName='Arial-Bold' if bold else 'Arial',fontSize=size,leading=size*1.45,textColor=HexColor(self.d['fg']),spaceAfter=8,splitLongWords=True)
        p=Paragraph(html.escape(value).replace('\n','<br/>'),style);_,h=p.wrap(w,700)
        assert y-h>=44,(self.v['title'],self.page,value[:70],y-h)
        p.drawOn(self.c,x,y-h);return y-h-12
    def image(self,p,x,y,w,h):
        im=Image.open(p);iw,ih=im.size;scale=min(w/iw,h/ih);dw,dh=iw*scale,ih*scale;self.c.drawImage(str(p),x+(w-dw)/2,y-h+(h-dh)/2,dw,dh,mask='auto')
    def save(self):self.c.save()

def exercise(item,v):
    stem=item['stem'];run=item['run']
    recipes={
    'artwork-to-applications':f'python -m apt_theme.cli import output/{run}/palette.toml --output .build/visual-volume-tour-new --targets powerpoint --json',
    'canonical-32':f'python -m apt_theme.cli generate output/{run}/source/{Path(item["artwork"]).name} --output .build/crystal-extraction-new --targets windows_terminal --json',
    'semantic-interfaces':f'python -m apt_theme.cli import output/{run}/palette.toml --output .build/factor-mapping-new --targets windows_terminal,powerpoint --json',
    'themes-on-web':f'python -m apt_theme.cli import output/{run}/palette.toml --output .build/caddy-web-new --targets website --json',
    'writing-in-color':f'python -m http.server 8126 --bind 127.0.0.1 --directory docs/documentation-suite/visual-volumes-2026-10-31/{stem}',
    'visual-collection':f'python -m apt_theme.cli atlas output --include {run} --output .build/cloudflare-atlas-new --json',
    'artwork-custody':f'python scripts/Convert-to-SVG.py --input output/{run}/source/{Path(item["artwork"]).name} --output .build/flathub-embed-new.svg',
    'safe-operation':f'python -m apt_theme.cli import output/{run}/palette.toml --output .build/swift-terminal-new --targets windows_terminal --json'}
    return recipes[v['topic']]

def build_guide(item,v,d,stem):
    directory=DEST/item['stem'];fig=directory/'figures';palette_figure(item,d,fig/'canonical-32.png');plot_figure(item,d,fig/'canonical-lightness.png');labels,line=lineage(item,d);diagram_figure([labels[0]+' '+labels[1],'Semantic primary','PowerPoint '+labels[3],'Office accent1'],d,fig/'primary-lineage.png','One recorded color, four contexts')
    for i,ch in enumerate(v['chapters']):diagram_figure(ch[3].split('|'),d,fig/f'chapter-{i+1:02}.png',ch[0])
    intro=f"This guide follows {item['run']}, a recorded dark theme with 32 canonical colors and fifteen target artifacts. Read the visual examples first, then inspect the linked data and source snapshot. The engine remains a local pilot. This collection is a dated explanation of existing behavior, not installation or publication evidence."
    prereq='Prerequisites: familiarity with files and folders; a prepared project Python environment for command exercises; ImageMagick for image generation and converter operations; installed native applications only for their separate acceptance reviews. Documentation authoring uses its own bundled Python libraries and does not change pipeline dependencies.'
    worked='Start by reading figures/run.json and its artifact_manifests. Locate the relevant inventory under artifacts, check its recorded file hash, and open the corresponding specimen. Compare figures/palette.toml with figures/semantics.json. Find the primary source ID, then read the PowerPoint primary token origin and the Office XML accent1 slot. The lineage figure shows the exact values in this selected run. Keep derived target values separate from canonical RGB.'
    worked2='For a revision, choose a destination that does not already exist. Record the command, interpreter, input hash, stdout, stderr, and exit code. Compare the resulting canonical IDs and RGB values before evaluating application tokens. Import is the appropriate path when preserving the selected 32. Use generation only when intentionally selecting from an image again. Do not apply these recipes to a reviewed source run or public folder.'
    checks=['Confirm the selected physical run, generation prefix, and source hash.','Verify artifact hashes and retain complete dependency directories.','Compare canonical IDs and RGB values before and after the exercise.','Read semantic findings, aliases, derived flags, and declared contrast checks.','Review actual rendering in the intended environment and record its version.','Keep manual edit/save/reopen, installation, activation, and publication as separate gates.']
    glossary={'Canonical palette':'Exactly 32 recorded source colors with IDs independent of application roles.','Semantic role':'A purpose mapped to a canonical source ID.','Target token':'An emitted application value with recorded origin and adaptation details.','Artifact manifest':'The authoritative target inventory of actual filenames, roles, and SHA-256 values.','Derived value':'A target HEX that differs from its canonical source; it does not change that source.','Native acceptance':'Observed behavior in a named application, distinct from static and browser checks.'}
    md=[f'# {v["title"]}',f'**{item["stem"]} · Documentation snapshot: 31 October 2026**',v['subtitle'],'## Purpose and prerequisites',intro,prereq,'## Reading route','Use the 24-slide deck for orientation, this guide for explanations, and the copied source snapshot for inspection. Operational examples and their execution status are recorded in the collection validation/commands.json.','![Preserved source artwork](figures/'+Path(item['artwork']).name+')','## The canonical palette','![All 32 exact canonical colors](figures/canonical-32.png)','![Recorded canonical lightness](figures/canonical-lightness.png)','## One color through the system',line,'![Recorded primary lineage](figures/primary-lineage.png)']
    for i,(title,lead,body,_) in enumerate(v['chapters']):md += [f'## {i+1:02} · {title}',lead,body,f'![{title}](figures/chapter-{i+1:02}.png)']
    md+=['## Worked example',worked,worked2,'### Recipe', 'Run from the project root with the prepared project interpreter. Choose a new path if the example destination exists. See commands.json for separately recorded bounded equivalents; this exact displayed path is source-checked, not executed.', '```powershell',exercise(item,v),'```','## Failure and recovery','Stop on conflicting identity, missing or mismatched files, invalid input, or unsafe output placement. Keep diagnostics and the previous run. Correct the plan or configuration and use a fresh destination. Do not replace a preservation baseline with changed inputs.','## Acceptance checklist']+['- [ ] '+x for x in checks]+['## Glossary']+[f'**{k}:** {val}'for k,val in glossary.items()]+['## Sources and dates','Current source contracts take precedence over this snapshot. Historical browser/native/hosting acceptance records keep their original dates. New documentation rendering evidence is recorded separately.']
    snapshot=json.loads((DEST/'validation/source-snapshot.json').read_text())
    md += [f'- [{r}](../source/snapshot/{r}) — SHA-256 `{snapshot[r]}`'for r in v['refs']]
    md += ['- [Delivery validation](../validation/delivery.json)','- [Command evidence](../validation/commands.json)','- [Copied native artifacts](artifacts/)','- [Source artwork and run records](figures/)']
    (directory/(stem+'-guide.md')).write_text('\n\n'.join(md)+'\n',encoding='utf-8')
    pdf=GuidePDF(directory/(stem+'-guide.pdf'),v,d)
    pdf.new(v['title']);y=pdf.p(v['subtitle'],48,650,516,18,True);y=pdf.p(intro,48,y-15,516);pdf.image(fig/Path(item['artwork']).name,125,450,362,310);pdf.p(item['stem']+' / preserved original artwork',48,100,516,10)
    pdf.new('How to read this volume');y=pdf.p(prereq,48,675,516);y=pdf.p('Use the slides for orientation and the guide for source-backed detail. The companion index links every slide preview, copied artifact, source snapshot, and validation receipt.',48,y,516);pdf.image(fig/'canonical-32.png',48,510,516,360);pdf.p('Canonical colors retain exact IDs and HEX values. This spread is independent of target-specific palettes.',48,130,516)
    pdf.new('One palette, several representations');pdf.image(fig/'canonical-lightness.png',48,675,516,290);pdf.image(fig/'primary-lineage.png',48,360,516,190);pdf.p(line,48,145,516,11)
    for pair in range(8):
        a=v['chapters'][pair*2];b=v['chapters'][pair*2+1];pdf.new(f'{pair*2+1:02}–{pair*2+2:02} / '+('Explanation' if pair<6 else 'Review and recovery'))
        y=pdf.p(a[0],48,675,516,18,True);y=pdf.p(a[1],48,y,516,12,True);y=pdf.p(a[2],48,y,516,11)
        pdf.image(fig/f'chapter-{pair*2+1:02}.png',48,y-8,516,150)
        y=min(345,y-175);y=pdf.p(b[0],48,y,516,18,True);y=pdf.p(b[1],48,y,516,12,True);pdf.p(b[2],48,y,516,11)
    specimens=sorted(fig.glob('*-specimen.png'))
    pdf.new('A gallery of actual generated outputs')
    for j,image in enumerate(specimens[:2]):
        top=680-j*305;pdf.image(image,48,top,516,250);pdf.p(('Illustrative chart fixture' if image.name.startswith('data_visualization') else 'Actual generated '+image.stem.replace('-specimen','').replace('_',' '))+' / copied bytes, rendered in Chromium.',48,top-260,516,9)
    pdf.new('Explore the native files')
    pdf.image(specimens[2],48,675,516,360)
    pdf.p('The copied artifacts directory retains native files, token origins, swatches, manifests, validation, and local browser dependencies. Open the topic index for exact links. CM6 previews require local HTTP; other preview behavior follows each native contract.',48,285,516,12)
    pdf.p('These images show the generated specimens. Fictional scenes and chart fixture values remain illustrative. Browser rendering does not establish native editor import, manual editing, installation, or production host integration.',48,165,516,11)
    md_gallery=['## Actual generated output gallery']
    for p in specimens:md_gallery.append(f'![Actual generated specimen; chart values remain illustrative](figures/{p.name})')
    with (directory/(stem+'-guide.md')).open('a',encoding='utf-8')as stream:stream.write('\n\n'+'\n\n'.join(md_gallery)+'\n')
    pdf.new('Worked example and acceptance');y=pdf.p(worked,48,680,516);y=pdf.p(worked2,48,y,516);y=pdf.p('Recipe (source-checked; bounded equivalents are logged separately):',48,y,516,11,True);y=pdf.p(exercise(item,v),48,y,516,9)
    y=pdf.p('Acceptance checklist',48,y-8,516,16,True)
    for x in checks:y=pdf.p('[ ] '+x,48,y,516,10)
    pdf.new('Glossary and source references');y=680
    for k,val in glossary.items():y=pdf.p(k+': '+val,48,y,516,10)
    y=pdf.p('Source snapshot references',48,y-8,516,16,True)
    for r in v['refs']:y=pdf.p(r+'\nSHA-256: '+snapshot[r],48,y,516,8)
    pdf.p('Delivery receipts: ../validation/delivery.json and ../validation/commands.json. Historical acceptance retains its original date. Manual edit/save/reopen, downstream activation, and publication are not established by this guide.',48,y-5,516,9);pdf.save()

def build_index(records):
    css='body{margin:0;background:#0c1921;color:#fefefc;font:18px Arial,sans-serif;line-height:1.55}main{max-width:1200px;margin:auto;padding:48px 30px}h1{font-size:54px;line-height:1.05}h2{font-size:32px}a{color:#8de6e3}img{max-width:100%;height:auto}article{padding:32px 0;border-top:1px solid #4a7488}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:20px}nav a{margin-right:22px}small{display:block}details{padding:12px 0}summary{cursor:pointer}:focus-visible{outline:3px solid #f7d483;outline-offset:4px}'
    top=['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Eight visual volumes — Logos-And-Theming</title><style>'+css+'</style><main><h1>One image.<br>Many useful forms.</h1><p>Eight themed visual volumes about Logos-And-Theming. 192 editable slides, illustrated guides, actual generated specimens, and inspectable source records.</p><p>Documentation snapshot: 31 October 2026. Local pilot. Open this index directly from disk. CM6 specimens require local HTTP; see the Clojure guide.</p><nav><a href="README.md">Collection guide</a><a href="validation/delivery.json">Delivery evidence</a><a href="validation/commands.json">Command checks</a><a href="validation/visual-review.json">Visual review</a></nav>']
    for item,v,stem in records:
        rel=item['stem'];title=html.escape(v['title']);top.append(f'<article><h2><a href="{rel}/index.html">{title}</a></h2><p>{html.escape(v["subtitle"])} <small>{rel}</small></p><a href="{rel}/index.html"><img loading="lazy" width="720" height="405" src="{rel}/previews/Slide1.PNG" alt="{title} cover"></a><nav><a href="{rel}/{stem}.pptx">Editable PowerPoint</a><a href="{rel}/{stem}.pdf">Slide PDF</a><a href="{rel}/{stem}-guide.pdf">Illustrated guide PDF</a><a href="{rel}/{stem}-guide.md">Markdown source</a></nav></article>')
        spec=json.loads((DEST/'source/specifications'/(stem+'.json')).read_text());p=[f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{title}</title><style>{css}</style><main><a href="../index.html">All eight volumes</a><h1>{title}</h1><p>{html.escape(v["subtitle"])}</p><nav><a href="{stem}.pptx">PowerPoint</a><a href="{stem}.pdf">Slide PDF</a><a href="{stem}-guide.pdf">Guide PDF</a><a href="{stem}-guide.md">Markdown guide</a></nav><h2>Actual generated specimens</h2><p>Preserved target trees. Chart data and fictional scenes remain illustrative. Browser previews do not establish downstream native acceptance.</p><div class="grid">']
        run=ROOT/'output'/item['run'];r=json.loads((run/'run.json').read_text())
        for target,manifest in r['artifact_manifests'].items():
            data=json.loads((run/manifest).read_text());links=[e for e in data['files']if e['file'].endswith('.html')and('examples' in e['file']or 'components' in e['file'])]
            if links:
                e=links[0];p.append(f'<a href="artifacts/{target}/{e["file"]}">{target.replace("_"," ")}</a>')
        p.append('</div><h2>Slide-by-slide reading</h2>')
        for slide in spec['slides']:
            n=slide['number'];p.append(f'<article><h2>{n:02}. {html.escape(slide["title"])}</h2><img loading="lazy" src="previews/Slide{n}.PNG" width="1280" height="720" alt="{html.escape(slide["title"])}"><details><summary>Explanation and source references</summary><p>{html.escape(slide["explanation"])}</p>')
            for ref in slide['sources']:p.append(f'<p><a href="../source/snapshot/{ref}">{ref}</a></p>')
            p.append('</details></article>')
        p.append('</main></html>');(DEST/rel/'index.html').write_text('\n'.join(p),encoding='utf-8')
    top.append('</main></html>');(DEST/'index.html').write_text('\n'.join(top),encoding='utf-8')

def main():
    replace='--replace-drafts' in sys.argv
    items=json.loads((DEST/'validation/template-inventory.json').read_text());records=[]
    for item,v in zip(items,VOLUMES):
        d=data_for(item);stem=build_deck(item,v,d,replace);build_guide(item,v,d,stem);records.append((item,v,stem));print(stem,flush=True)
    build_index(records)
    dump(DEST/'validation/build.json',[dict(stem=i['stem'],topic=v['topic'],file=f"{i['stem']}/{s}.pptx",slides=24,guide_pages=15)for i,v,s in records])
    provenance=[]
    for i,v,s in records:
        for p in (DEST/i['stem']/'figures').glob('*.png'):
            provenance.append(dict(file=p.relative_to(DEST).as_posix(),sha256=sha(p),basis=('Chromium specimen: see specimen-browser.json' if '-specimen' in p.stem else 'Recorded canonical values / chapter concepts / original preserved source'),source_run='output/'+i['run'],authoring_script='source/build.py'))
    dump(DEST/'validation/figure-provenance.json',provenance)
if __name__=='__main__':main()
