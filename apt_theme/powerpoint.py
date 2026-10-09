"""Adapt the preserved PowerPoint template without an external authoring runtime."""
import json
import hashlib
import io
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
DCTERMS = 'http://purl.org/dc/terms/'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'


def validate_core_properties(data):
    """Check QName-valued types, which ElementTree and slide checks miss."""
    namespaces = {}
    for event, item in ET.iterparse(io.BytesIO(data), events=('start-ns', 'start')):
        if event == 'start-ns':
            namespaces[item[0]] = item[1]
        elif item.tag in (f'{{{DCTERMS}}}created', f'{{{DCTERMS}}}modified'):
            value = item.get(f'{{{XSI}}}type', '')
            prefix, separator, local = value.partition(':')
            if not separator or namespaces.get(prefix) != DCTERMS or local != 'W3CDTF':
                raise ValueError('PowerPoint core timestamp has an invalid or undeclared W3CDTF namespace')


def normalize_core_properties(data):
    # xsi:type is a QName in an attribute value. ElementTree does not rewrite
    # that value when changing namespace prefixes, so preserve its declaration.
    ET.register_namespace('cp', 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties')
    ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
    ET.register_namespace('dcterms', DCTERMS)
    ET.register_namespace('xsi', XSI)
    root = ET.fromstring(data)
    for item in root:
        if item.tag in (f'{{{DCTERMS}}}created', f'{{{DCTERMS}}}modified'):
            item.text = '2026-01-01T00:00:00Z'
            item.set(f'{{{XSI}}}type', 'dcterms:W3CDTF')
    output = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    validate_core_properties(output)
    return output


TEMPLATE = Path(__file__).with_name('templates') / 'aptlantis-clogure-template.pptx'
TEMPLATE_SHA256 = 'ff78bc0f960314d5301f3533a18fe65d1a45c6c24e4139ff84e52cc675b6595d'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
PRESENTATION_TYPE = b'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
TEMPLATE_TYPE = b'application/vnd.openxmlformats-officedocument.presentationml.template.main+xml'


def template_parts():
    """Fail closed if the packaged reference is missing or changed."""
    if not TEMPLATE.is_file():
        raise ValueError('PowerPoint template is missing; reinstall the pipeline package')
    data = TEMPLATE.read_bytes()
    if hashlib.sha256(data).hexdigest() != TEMPLATE_SHA256:
        raise ValueError('PowerPoint template hash mismatch; restore the preserved reference')
    with zipfile.ZipFile(io.BytesIO(data)) as source:
        return {n: source.read(n) for n in source.namelist()}


def write_package(path, parts):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as output:
        for filename, data in sorted(parts.items()):
            info = zipfile.ZipInfo(filename, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            output.writestr(info, data)


def sample_deck(result, directory, name, stem):
    """Keep all native layouts, objects and workbooks; adapt color definitions only.

    Byte substitutions preserve namespace declarations, including markup
    compatibility prefixes that generic XML serializers can silently discard.
    The fixed input hash makes the deliberately narrow substitutions auditable.
    """
    parts = template_parts()
    slots = {slot: result['tokens'][token]['hex'][1:]
             for slot, token in result['native_slots'].items()}
    changed = []
    for filename, original in list(parts.items()):
        data = original
        if filename.startswith('ppt/') and filename.endswith('.xml'):
            if filename.startswith('ppt/theme/'):
                def scheme(match):
                    slot = match[1].decode()
                    return (b'<a:' + match[1] + b'><a:srgbClr val="' +
                            slots[slot].encode() + b'"/></a:' + match[1] + b'>')
                data, count = re.subn(
                    rb'<a:(dk1|lt1|dk2|lt2|accent[1-6]|hlink|folHlink)>.*?</a:\1>',
                    scheme, data, flags=re.DOTALL)
                if count != 12:
                    raise ValueError('PowerPoint template must define all twelve Office color slots')
            # Explicit black shadows and pale chart borders also follow the
            # generated palette. Keep alpha/effect transforms and all geometry.
            data = data.replace(b'<a:srgbClr val="000000"/>', b'<a:schemeClr val="dk1"/>')
            data = data.replace(b'<a:srgbClr val="F9F9F9"/>', b'<a:schemeClr val="lt1"/>')
            root = ET.fromstring(data)
            if not filename.startswith('ppt/theme/') and root.findall(f'.//{{{A}}}srgbClr'):
                raise ValueError('Unmapped explicit color in PowerPoint template: ' + filename)
        if data != original:
            changed.append(filename)
        parts[filename] = data
    validate_core_properties(parts['docProps/core.xml'])
    slides = sum(bool(re.fullmatch(r'ppt/slides/slide\d+\.xml', n)) for n in parts)
    layouts = sum(bool(re.fullmatch(r'ppt/slideLayouts/slideLayout\d+\.xml', n)) for n in parts)
    deck_file, template_file = stem + '-sample.pptx', stem + '-template.potx'
    write_package(directory / deck_file, parts)
    template = dict(parts)
    if template['[Content_Types].xml'].count(PRESENTATION_TYPE) != 1:
        raise ValueError('PowerPoint template has an unexpected main content type')
    template['[Content_Types].xml'] = template['[Content_Types].xml'].replace(PRESENTATION_TYPE, TEMPLATE_TYPE)
    write_package(directory / template_file, template)
    result['sample_deck'] = {
        'file': deck_file, 'template_file': template_file, 'slides': slides,
        'layouts': layouts, 'editable': ['text', 'placeholders', 'tables', 'charts'],
        'chart_data': 'illustrative template values',
        'native_application_acceptance': 'pending',
        'source_template': TEMPLATE.name, 'source_sha256': TEMPLATE_SHA256,
        'modified_parts': changed,
        'preserved_parts': len(parts) - len(changed),
    }
    (directory / 'template-provenance.json').write_text(
        json.dumps(result['sample_deck'], indent=2) + '\n', encoding='utf-8')
