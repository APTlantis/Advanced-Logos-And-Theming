from pathlib import Path
from PIL import Image,ImageDraw
import re,sys
def contact(files,out,cols=4,size=(320,200)):
    files=list(files); w,h=size
    sheet=Image.new('RGB',(cols*w,((len(files)+cols-1)//cols)*h),(20,20,20));draw=ImageDraw.Draw(sheet)
    for i,p in enumerate(files):
        im=Image.open(p).convert('RGB');im.thumbnail((w-4,h-22));x=(i%cols)*w;y=(i//cols)*h
        sheet.paste(im,(x,y));draw.text((x+4,y+h-20),f'{i+1}: {p.stem}',fill='white')
    sheet.save(out)
if __name__=='__main__':
    base=Path(__file__).resolve().parents[1]
    if '--templates' in sys.argv:
        for d in (base/'template-previews').iterdir():
            if d.is_dir(): contact(sorted(d.glob('*.PNG'),key=lambda p:int(re.search(r'\d+',p.stem)[0])),d.with_name(d.name+'-contact.png'))
    else:
        for d in base.iterdir():
            if d.is_dir() and (d/'previews').exists():
                contact(sorted((d/'previews').glob('Slide*.PNG'),key=lambda p:int(re.search(r'\d+',p.stem)[0])),d/'slide-contact.png')
                files=sorted((d/'pdf-previews').glob('*guide-page-*.png'))
                if files:contact(files,d/'guide-contact.png',cols=3,size=(340,460))
                slides=sorted(p for p in (d/'pdf-previews').glob('*.png')if '-guide-' not in p.name)
                if slides:contact(slides,d/'slide-pdf-contact.png')
