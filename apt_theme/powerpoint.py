"""Editable sample deck bridge, with deterministic Open XML packaging."""
import json
import io
import os
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from uuid import NAMESPACE_URL, uuid5
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


def chart_workbook(parts):
    """Bind the illustrative chart's caches to a real editable workbook."""
    spreadsheet = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    sheet = ET.Element('worksheet', xmlns=spreadsheet)
    rows = ET.SubElement(sheet, 'sheetData')
    values = [['Sample', *[f'Accent {i}' for i in range(1, 7)]], ['Sample A', *range(4, 10)], ['Sample B', *range(10, 4, -1)]]
    for i, values_row in enumerate(values, 1):
        row = ET.SubElement(rows, 'row', r=str(i))
        for j, value in enumerate(values_row):
            cell = ET.SubElement(row, 'c', r=f'{chr(65+j)}{i}', t='inlineStr' if isinstance(value, str) else 'n')
            if isinstance(value, str):
                ET.SubElement(ET.SubElement(cell, 'is'), 't').text = value
            else:
                ET.SubElement(cell, 'v').text = str(value)
    stream = io.BytesIO()
    workbook_parts = {
        '[Content_Types].xml': '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        '_rels/.rels': f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        'xl/workbook.xml': f'<workbook xmlns="{spreadsheet}" xmlns:r="{R}"><sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets></workbook>',
        'xl/_rels/workbook.xml.rels': f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/worksheet" Target="worksheets/sheet1.xml"/></Relationships>',
        'xl/worksheets/sheet1.xml': ET.tostring(sheet, encoding='unicode'),
    }
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as book:
        for key, value in sorted(workbook_parts.items()):
            info = zipfile.ZipInfo(key, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            book.writestr(info, value)
    parts['ppt/embeddings/sample-data.xlsx'] = stream.getvalue()
    chart_path = next(n for n in parts if n.endswith('/chart1.xml'))
    root = ET.fromstring(parts[chart_path])
    for i, series in enumerate(root.findall(f'.//{{{C}}}ser')):
        for kind, column in (('cat', 'A'), ('val', chr(66+i))):
            holder = series.find(f'{{{C}}}{kind}')
            cache = holder[0]
            cache.tag = f'{{{C}}}' + ('strCache' if kind == 'cat' else 'numCache')
            holder.remove(cache)
            ref = ET.SubElement(holder, f'{{{C}}}' + ('strRef' if kind == 'cat' else 'numRef'))
            ET.SubElement(ref, f'{{{C}}}f').text = f'Sheet1!${column}$2:${column}$3'
            ref.append(cache)
    external = ET.SubElement(root, f'{{{C}}}externalData', {f'{{{R}}}id': 'rId1'})
    ET.SubElement(external, f'{{{C}}}autoUpdate', val='0')
    parts[chart_path] = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    parts[str(Path(chart_path).parent / '_rels' / (Path(chart_path).name + '.rels')).replace('\\', '/')] = f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/package" Target="../../embeddings/sample-data.xlsx"/></Relationships>'.encode()
    parts['[Content_Types].xml'] = parts['[Content_Types].xml'].replace(b'</Types>', b'<Override PartName="/ppt/embeddings/sample-data.xlsx" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"/></Types>')


def runtime():
    bundled = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node'
    node = os.environ.get('APT_THEME_NODE') or (str(bundled / 'bin/node.exe') if (bundled / 'bin/node.exe').exists() else shutil.which('node'))
    module = Path(os.environ.get('APT_THEME_ARTIFACT_TOOL', str(bundled / 'node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')))
    if not node or not module.is_file():
        raise ValueError('PowerPoint sample decks require Node.js and @oai/artifact-tool. Set APT_THEME_NODE and APT_THEME_ARTIFACT_TOOL; see docs/POWERPOINT.md.')
    return node, module


def sample_deck(result, directory, name, stem):
    node, module = runtime()
    with tempfile.TemporaryDirectory(prefix='apt-deck-') as temp:
        temp = Path(temp)
        request = temp / 'request.json'
        request.write_text(json.dumps({'name': name, 'slots': {slot: result['tokens'][token]['hex'] for slot, token in result['native_slots'].items()}, 'roles': result['native_slots']}), encoding='utf-8')
        draft = temp / 'draft.pptx'
        try:
            process = subprocess.run([node, str(Path(__file__).with_name('sample_deck.mjs')), str(module), str(request), str(draft)], capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('PowerPoint sample deck timed out') from exc
        if process.returncode:
            raise ValueError('PowerPoint sample deck failed: ' + process.stderr[-3000:])
        with zipfile.ZipFile(draft) as source:
            parts = {n: source.read(n) for n in source.namelist()}
        chart_workbook(parts)
        # Relationship ids are scoped to their owner part. Rename both ends,
        # leaving numeric shape/slide ids and unrelated references intact.
        for filename in sorted(parts):
            if filename.endswith('.rels'):
                mappings = {old: f'rId{i}'.encode() for i, old in enumerate(re.findall(rb'Id="([^"]+)"', parts[filename]), 1)}
                owner = filename.replace('/_rels/', '/').removesuffix('.rels')
                parts[filename] = re.sub(rb'Id="([^"]+)"', lambda m: b'Id="' + mappings[m[1]] + b'"', parts[filename])
                if owner in parts:
                    parts[owner] = re.sub(rb'r:(id|embed|link)="([^"]+)"', lambda m: b'r:' + m[1] + b'="' + mappings.get(m[2], m[2]) + b'"', parts[owner])
        for filename in parts:
            if filename.endswith('.xml'):
                index = iter(range(10000))
                def creation(match):
                    i = next(index)
                    value = ('{' + str(uuid5(NAMESPACE_URL, filename + ':' + str(i))).upper() + '}') if match[1] == b'id' else str(i + 1)
                    return match[0].replace(match[2], value.encode())
                parts[filename] = re.sub(rb'<(?:a16|p14):creationId (id|val)="([^"]+)"', creation, parts[filename])
        with zipfile.ZipFile(directory / (stem + '-sample.pptx'), 'w', zipfile.ZIP_DEFLATED) as output:
            for filename in sorted(parts):
                data = parts[filename]
                if filename in ('ppt/slides/slide2.xml', 'ppt/slides/slide3.xml'):
                    # Artifact Tool's authoring color parser does not recognize
                    # camel-case folHlink. Restore the native scheme reference.
                    root = ET.fromstring(data)
                    hex_value = result['tokens'][result['native_slots']['folHlink']]['hex'][1:]
                    for item in root.iter():
                        if item.tag.endswith('}srgbClr') and item.get('val') == hex_value:
                            item.tag = item.tag.replace('srgbClr', 'schemeClr')
                            item.set('val', 'folHlink')
                    data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                if filename == 'docProps/core.xml':
                    data = normalize_core_properties(data)
                info = zipfile.ZipInfo(filename, (2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                output.writestr(info, data)
    result['sample_deck'] = {'file': stem + '-sample.pptx', 'slides': 4, 'editable': ['text', 'color-slot table', 'chart'], 'chart_data': 'illustrative sample values', 'native_application_acceptance': 'pending'}
