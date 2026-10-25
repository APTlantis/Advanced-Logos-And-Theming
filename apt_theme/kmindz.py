"""Kmindz package exporter, using the supplied kmind.theme-package v1 contract."""
import copy
import hashlib
import json
from importlib.resources import files
from urllib.parse import quote
import xml.etree.ElementTree as ET

from .colors import contrast

TEMPLATE = 'templates/kmindz-template.json'
RAINBOW = ('primary', 'secondary', 'keyword', 'string', 'number', 'type',
           'function', 'operator', 'constant', 'success', 'info', 'warning')

def extend(tokens, checks, add):
    add('root_fill', 'primary', 'root node fill', lightness=.24, chroma=.65)
    add('root_fill_selected', 'primary', 'selected root fill', lightness=.32, chroma=.65)
    add('root_text', 'foreground', 'root text in both states', minimum=4.5, bg='root_fill_selected')
    add('depth1_fill', 'background', 'depth-one node fill', lightness=.22, chroma=.7)
    add('depth1_text', 'foreground', 'depth-one text in both states', minimum=4.5, bg='selection')
    add('depth2_fill', 'secondary', 'depth-two node fill', lightness=.24, chroma=.45)
    add('depth2_text', 'foreground', 'depth-two text in both states', minimum=4.5, bg='selection')
    add('depth3_text', 'muted', 'depth-three-plus text in both states', minimum=4.5, bg='selection')
    add('edge_primary', 'primary', 'primary hierarchy edge', minimum=3)
    add('edge_secondary', 'secondary', 'secondary hierarchy edge', minimum=3)
    for fg, bg in [('foreground','selection'), ('root_text','root_fill'),
                   ('depth1_text','depth1_fill'), ('depth2_text','depth2_fill'), ('depth3_text','panel')]:
        ratio=contrast(tokens[fg],tokens[bg])
        checks.append({'foreground':fg,'background':bg,'ratio':ratio,'required':4.5,'pass':ratio>=4.5})


def preview_svg(variant):
    """Small authored preview of exported node colors; not a Kmindz rendering."""
    ET.register_namespace('', 'http://www.w3.org/2000/svg')
    ns='{http://www.w3.org/2000/svg}'
    svg=ET.Element(ns+'svg',width='244',height='96',viewBox='0 0 244 96',role='img')
    ET.SubElement(svg,ns+'title').text='Dark hierarchy color preview'
    ET.SubElement(svg,ns+'rect',width='244',height='96',fill=variant['background']['color'])
    paints=[variant['rules']['nodeRules'][i]['apply']['paint'] for i in range(3)]
    for i,(x,y,w,h) in enumerate([(8,34,66,28),(96,15,62,24),(176,57,60,24)]):
        paint=paints[i]
        if i: ET.SubElement(svg,ns+'path',d=f'M74 48 Q90 48 {x} {y+12}',fill='none',stroke=variant['tokens']['paint']['edgeStroke'],**{'stroke-width':'3'})
        ET.SubElement(svg,ns+'rect',x=str(x),y=str(y),width=str(w),height=str(h),rx='9',fill=paint['nodeFill'],stroke=paint['nodeStroke'])
        ET.SubElement(svg,ns+'path',d=f'M{x+12} {y+h/2:g}h{w-24}',stroke=paint['text'],**{'stroke-width':'2','stroke-linecap':'round'})
    return ET.tostring(svg,encoding='unicode')


def package(result, name):
    template_bytes=files('apt_theme').joinpath(TEMPLATE).read_bytes()
    out=json.loads(template_bytes)
    variant=copy.deepcopy(out['theme']['variants']['dark'])
    h=lambda key:result['tokens'][key]['hex']
    mapping={'bg':'background','panel':'panel','text':'foreground','muted':'muted','border':'border',
             'nodeFill':'panel','nodeFillSelected':'selection','nodeStroke':'border',
             'nodeStrokeSelected':'primary','edgeStroke':'edge_primary','relationStroke':'edge_secondary',
             'relationStrokeSelected':'primary','summaryStroke':'border'}
    variant['tokens']['paint']={key:h(token) for key,token in mapping.items()}
    variant['background']['color']=h('background')
    variant['rainbow']['palette']=[h(key) for key in RAINBOW]
    root,one,two,deep=variant['rules']['nodeRules']
    root['apply']['paint']={'nodeFill':h('root_fill'),'nodeFillSelected':h('root_fill_selected'),
                          'nodeStroke':h('primary'),'text':h('root_text')}
    one['apply']['paint']={'nodeFill':h('depth1_fill'),'nodeStroke':h('border'),'text':h('depth1_text')}
    one['apply']['incomingEdge']['strokeColor']=h('edge_primary')
    two['apply']['paint']={'nodeFill':h('depth2_fill'),'nodeStroke':h('border'),'text':h('depth2_text')}
    two['apply']['incomingEdge']['strokeColor']=h('edge_secondary')
    deep['apply']['paint']={'nodeFill':h('panel'),'nodeStroke':h('border'),'text':h('depth3_text')}
    deep['apply']['incomingEdge']['strokeColor']=h('border')
    from .targets import slug
    identity=(result.get('theme_identity', {}).get('prefix', '')+'-'+result.get('theme_identity', {}).get('slug', '') if 'theme_identity' in result else slug(name))+'-canonical32'; display=name+' Â· Canonical 32'
    description=f'{name}: image-derived dark mind-map theme from the canonical 32-color palette.'
    out.update(id=identity,name=display,description=description,createdAt=0,updatedAt=0)
    out['theme'].update(id=identity,name=display,description=description,updatedAt=0,variants={'dark':variant})
    svg=preview_svg(variant)
    out['preview']={'thumbnail':{'source':'theme-preview-svg-v1','dataUrl':'data:image/svg+xml;charset=utf-8,'+quote(svg,safe=''),
                                 'width':244,'height':96,'generatedAt':0}}
    slots={'tokens.paint.'+key:token for key,token in mapping.items()}
    slots.update({'root.nodeFill':'root_fill','root.nodeFillSelected':'root_fill_selected','root.text':'root_text',
                  'depth1.nodeFill':'depth1_fill','depth1.text':'depth1_text',
                  'depth2.nodeFill':'depth2_fill','depth2.text':'depth2_text','depth3.text':'depth3_text'})
    return out,svg,slots,hashlib.sha256(template_bytes).hexdigest()


def export_kmindz(result,directory,name):
    from .output_names import artifact_names
    artifact = artifact_names(result)
    out,svg,slots,template_hash=package(result,name)
    (directory/artifact('KMINDS.json')).write_text(json.dumps(out,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8')
    (directory/artifact('preview.svg')).write_text(svg+'\n',encoding='utf-8')
    (directory/artifact('format-provenance.json')).write_text(json.dumps({
        'contract':'kmind.theme-package','schemaVersion':1,'source':f"User-supplied {artifact('KMINDS.json')} template",
        'template_sha256':template_hash,'variant':'dark','timestamps':'0 = unspecified reproducible export timestamp',
        'native_import_acceptance':'pending','preview':'Authored color preview, not a native Kmindz render'},indent=2)+'\n',encoding='utf-8')
    result['native_slots']=slots
    result['kmindz']={'package':artifact('KMINDS.json'),'preview':artifact('preview.svg'),'template_sha256':template_hash,'variant':'dark'}
