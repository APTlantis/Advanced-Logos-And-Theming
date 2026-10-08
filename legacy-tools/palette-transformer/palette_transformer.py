#!/usr/bin/env python3
"""Deterministic logo-palette adaptation. Python 3.11+, Pillow for swatches."""
import argparse, copy, hashlib, json, math, re, sys, tomllib
from pathlib import Path

VERSION = '1.0.0'
PROFILES = {'terminal':20, 'notepad':32, 'sublime':40, 'siyuan':64, 'jetbrains':96, 'website':112, 'powerpoint':24, 'desktop':80}

def linear(v):
    return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4

def encode(v):
    return 12.92*v if v <= .0031308 else 1.055*v**(1/2.4)-.055

def rgb_to_lch(rgb):
    r,g,b = [linear(v/255) for v in rgb]
    l,m,s = [.4122214708*r+.5363325363*g+.0514459929*b, .2119034982*r+.6806995451*g+.1073969566*b, .0883024619*r+.2817188376*g+.6299787005*b]
    l,m,s = [v**(1/3) for v in (l,m,s)]
    L = .2104542553*l+.793617785*m-.0040720468*s
    a = 1.9779984951*l-2.428592205*m+.4505937099*s
    b = .0259040371*l+.7827717662*m-.808675766*s
    return [L,math.hypot(a,b),math.degrees(math.atan2(b,a))%360]

def raw_rgb(lch):
    L,C,h=lch; a=C*math.cos(math.radians(h)); b=C*math.sin(math.radians(h))
    l,m,s = [(L+.3963377774*a+.2158037573*b)**3,(L-.1055613458*a-.0638541728*b)**3,(L-.0894841775*a-1.291485548*b)**3]
    return [4.0767416621*l-3.3077115913*m+.2309699292*s,-1.2684380046*l+2.6097574011*m-.3413193965*s,-.0041960863*l-.7034186147*m+1.707614701*s]

def lch_to_rgb(lch):
    L,C,h=lch; L=max(0,min(1,L)); original=C
    def inside(v): return all(-1e-7 <= x <= 1+1e-7 for x in v)
    if not inside(raw_rgb([L,C,h])):
        lo,hi=0,C
        for _ in range(32):
            mid=(lo+hi)/2
            if inside(raw_rgb([L,mid,h])): lo=mid
            else: hi=mid
        C=lo
    rgb=[round(max(0,min(1,encode(max(0,x))))*255) for x in raw_rgb([L,C,h])]
    return rgb, original-C > 1e-6

def color(rgb):
    return {'hex':'#'+''.join(f'{v:02X}' for v in rgb),'rgb':rgb,'oklch':dict(zip(('l','c','h'),rgb_to_lch(rgb)))}

def coords(c):
    o=c['oklch']; return [o['l'],o['c']*math.cos(math.radians(o['h'])),o['c']*math.sin(math.radians(o['h']))]

def distance(a,b): return math.dist(coords(a),coords(b))
def contrast(a,b):
    def lum(c):
        r,g,b=[linear(v/255) for v in c['rgb']]; return .2126*r+.7152*g+.0722*b
    x,y=sorted([lum(a),lum(b)]); return (y+.05)/(x+.05)

def load(path):
    raw=path.read_bytes(); data=tomllib.loads(raw.decode('utf-8-sig')); colors={}; notices=[]
    for family,entries in data['palette'].items():
        for name,c in entries.items():
            if name in colors: raise ValueError(f'duplicate color id: {name}')
            if 'oklch' in c:
                o=c['oklch']; values=[float(o[k]) for k in ('l','c','h')]
                if not all(math.isfinite(v) for v in values) or not 0<=values[0]<=1 or values[1]<0: raise ValueError(f'invalid OKLCH: {name}')
                rgb,mapped=lch_to_rgb(values)
            elif 'hex' in c:
                if not re.fullmatch(r'#[0-9a-fA-F]{6}',c['hex']): raise ValueError(f'invalid hex: {name}')
                rgb=[int(c['hex'][i:i+2],16) for i in (1,3,5)]
            else: rgb=c['rgb']
            if len(rgb)!=3 or any(type(v) is not int or not 0<=v<=255 for v in rgb): raise ValueError(f'invalid RGB: {name}')
            if 'hex' in c and 'oklch' in c and color(rgb)['hex'] != c['hex'].upper(): notices.append(f'{name}: hex disagrees with OKLCH; OKLCH used')
            colors[name]={**color(rgb),'family':family}
    roles=data.get('roles',{})
    for group,entries in roles.items():
        for role,ref in entries.items():
            if ref not in colors: raise ValueError(f'unknown role reference: {group}.{role} = {ref}')
    if not colors: raise ValueError('empty palette')
    return data,colors,hashlib.sha256(raw).hexdigest(),notices

def transform(data,source,count,profile,settings=None):
    settings=settings or {}
    roles=copy.deepcopy(data.get('roles',{})); selected={}; derived=[]; remaps=[]
    if count>=len(source): selected=copy.deepcopy(source)
    else:
        refs=[]
        for group,role in [('base','app_bg'),('base','editor_bg'),('text','fg_primary')]:
            ref=roles.get(group,{}).get(role)
            if ref and ref not in refs: refs.append(ref)
        if profile=='terminal': refs += [r for r in roles.get('terminal',{}).values() if r not in refs]
        if len(refs)>count: raise ValueError(f'count {count} cannot preserve {len(refs)} required anchors')
        for ref in refs: selected[ref]=copy.deepcopy(source[ref])
        if not selected:
            ref=next(iter(source)); selected[ref]=copy.deepcopy(source[ref])
        while len(selected)<count:
            ref=max((r for r in source if r not in selected),key=lambda r:min(distance(source[r],c) for c in selected.values()))
            selected[ref]=copy.deepcopy(source[ref])
    # Purpose-driven expansion, followed by bounded family variants. No artificial hue invention.
    anchor=roles.get('base',{}).get('app_bg',next(iter(source)))
    dark=data.get('theme',{}).get('variant','dark')=='dark'
    candidates=[]
    for i in range(1,settings.get("surface_depth",7)+1): candidates.append((f'surface_depth_{i:02}',anchor,(.035*i if dark else -.035*i),.65,'surface','nested surface'))
    for group in ('accent','text','syntax'):
        for role,ref in roles.get(group,{}).items():
            for state,delta,scale in [('hover',.055 if dark else -.055,1),('pressed',-.055 if dark else .055,.9),('subdued',-.12 if dark else .12,.55)]:
                candidates.append((f'{group}_{role}_{state}',ref,delta,scale,group,f'{role} {state}'))
    for step in range(1,9):
        for ref,c in source.items(): candidates.append((f'{ref}_variant_{step:02}',ref,(1 if step%2 else -1)*(.035*((step+1)//2)),.85,c['family'],'family variation'))
    for name,ref,delta,scale,family,purpose in candidates:
        if len(selected)>=count: break
        o=source[ref]['oklch']; requested=[o['l']+delta,o['c']*scale,o['h']]
        if not 0<=requested[0]<=1: continue
        rgb,mapped=lch_to_rgb(requested); c=color(rgb)
        if min(distance(c,s) for s in selected.values())<settings.get('minimum_distance',.012): continue
        c['family']=family
        c['origin']={'source':ref,'operation':'oklch_shift','delta_l':delta,'chroma_scale':scale,'delta_h':0.0,'purpose':purpose,'gamut_mapped':mapped,'requested_oklch':requested}
        selected[name]=c; derived.append(name)
        roles.setdefault('derived',{})[name]=name
    for group,entries in roles.items():
        for role,ref in list(entries.items()):
            if ref not in selected:
                target=min(selected,key=lambda s:distance(source[ref],selected[s])); entries[role]=target
                remaps.append({'role':f'{group}.{role}','from':ref,'to':target,'distance_oklab':distance(source[ref],selected[target])})
    return selected,roles,derived,remaps

def validation(data,colors,roles,notices):
    checks=[]; bg=roles.get('base',{}).get('app_bg')
    if bg:
        for group in ('text','syntax'):
            for role,ref in roles.get(group,{}).items():
                ratio=contrast(colors[ref],colors[bg]); required=data.get('validation',{}).get('minimum_contrast_body',4.5)
                checks.append({'role':f'{group}.{role}','background':bg,'ratio':round(ratio,3),'required':required,'pass':ratio>=required})
        for role in ('border_subtle','border_strong'):
            ref=roles.get('base',{}).get(role)
            if ref:
                ratio=contrast(colors[ref],colors[bg]); required=data.get('validation',{}).get('minimum_contrast_ui',3)
                checks.append({'role':f'base.{role}','background':bg,'ratio':round(ratio,3),'required':required,'pass':ratio>=required})
    collisions=[]; items=list(colors.items())
    for i,(a,ca) in enumerate(items):
        for b,cb in items[i+1:]:
            d=distance(ca,cb)
            if d<.02: collisions.append({'a':a,'b':b,'distance_oklab':round(d,6),'same_family':ca['family']==cb['family'],'severity':'review'})
    return {'contrast_checks':checks,'contrast_failures':sum(not c['pass'] for c in checks),'near_colors':collisions,'notices':notices,'coverage':'Declared text/syntax and borders against app_bg only; exporter must validate actual component pairings.','apca':'Not computed; reported ratios use WCAG relative luminance.','semantic_note':'Source semantic and ANSI mappings are preserved, including unconventional hue assignments.'}

def toml_dump(data):
    # Tables-only serializer supports nested metadata without third-party TOML dependencies.
    lines=[]
    def value(v):
        if isinstance(v,bool): return str(v).lower()
        if isinstance(v,str): return json.dumps(v,ensure_ascii=False)
        if isinstance(v,(float,int)): return repr(v)
        if isinstance(v,list): return '['+', '.join(value(x) for x in v)+']'
        raise TypeError(type(v))
    def walk(d,path):
        if path: lines.append('['+'.'.join(json.dumps(k) for k in path)+']')
        for k,v in d.items():
            if not isinstance(v,dict): lines.append(json.dumps(k)+' = '+value(v))
        lines.append('')
        for k,v in d.items():
            if isinstance(v,dict): walk(v,path+[k])
    walk(data,[]); return '\n'.join(lines)

def swatch(colors,path,title):
    from PIL import Image,ImageDraw,ImageFont
    cols=4; cellw=300; cellh=100; rows=math.ceil(len(colors)/cols)
    img=Image.new('RGB',(cols*cellw,rows*cellh+70),'#101923'); d=ImageDraw.Draw(img)
    font=ImageFont.load_default(size=13); heading=ImageFont.load_default(size=24)
    d.text((20,20),title,fill='#EDF0E7',font=heading)
    for i,(name,c) in enumerate(colors.items()):
        x=(i%cols)*cellw; y=(i//cols)*cellh+70
        d.rectangle((x+10,y+8,x+cellw-10,y+55),fill=c['hex'])
        d.text((x+10,y+60),name,fill='#EDF0E7',font=font)
        d.text((x+10,y+80),c['hex']+('  derived' if 'origin' in c else '  canonical'),fill='#B2BCC7',font=font)
    img.save(path)

def run(input_path,output,profile,count=None,strict=False,settings=None):
    data,source,digest,notices=load(input_path); count=PROFILES[profile] if count is None else count
    if count<1 or count>512: raise ValueError('count must be between 1 and 512')
    colors,roles,derived,remaps=transform(data,source,count,profile,settings)
    report=validation(data,colors,roles,notices)
    result={'theme':copy.deepcopy(data.get('theme',{})),'transformation':{'version':VERSION,'profile':profile,'mode':'reduce' if count<len(source) else 'preserve' if count==len(source) else 'expand','requested_count':count,'actual_count':len(colors),'unique_hex_count':len({c['hex'] for c in colors.values()}),'source_sha256':digest,'canonical_count':len(source)},'palette':{},'roles':roles,'validation':copy.deepcopy(data.get('validation',{}))}
    result['theme']['final_colors']=len(colors)
    for key in ('source','targets'):
        if key in data: result[key]=copy.deepcopy(data[key])
    if len(colors)<count: report['notices'].append(f'Requested {count}; emitted {len(colors)} after distinctness filtering')
    for name,c in colors.items(): result['palette'].setdefault(c['family'],{})[name]={k:v for k,v in c.items() if k!='family'}
    manifest={'source_sha256':digest,'retained':[n for n in source if n in colors],'added':derived,'omitted':[n for n in source if n not in colors],'modified_canonical':[],'role_remaps':remaps}
    output.mkdir(parents=True,exist_ok=True)
    (output/'palette.toml').write_text(toml_dump(result),encoding='utf-8')
    (output/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    swatch(colors,output/'swatch.png',f"{data.get('theme',{}).get('name','Palette')} / {profile} / {len(colors)} colors")
    return result,report

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('input',type=Path); p.add_argument('--output',type=Path,default=Path('profiles')); p.add_argument('--profile',choices=[*PROFILES,'all'],default='all'); p.add_argument('--count',type=int); p.add_argument('--strict',action='store_true',help='exit 2 if contrast checks fail; still write reports'); p.add_argument('--profiles',type=Path,help='TOML profile configuration'); a=p.parse_args()
    if a.profile=='all' and a.count: p.error('--count requires one profile')
    try:
        failed=False
        config=tomllib.loads(a.profiles.read_text(encoding='utf-8-sig')).get('profiles',{}) if a.profiles else {}
        for profile in PROFILES if a.profile=='all' else [a.profile]:
            settings=config.get(profile,{})
            result,report=run(a.input,a.output/profile,profile,a.count if a.count is not None else settings.get('target_count'),a.strict,settings)
            print(f"{profile}: {result['transformation']['actual_count']} colors; {report['contrast_failures']} contrast checks failed")
            failed |= bool(report['contrast_failures'])
        return 2 if a.strict and failed else 0
    except (ValueError,KeyError,OSError,ImportError,tomllib.TOMLDecodeError) as e:
        print(f'Error: {e}',file=sys.stderr); return 1
if __name__=='__main__': sys.exit(main())
