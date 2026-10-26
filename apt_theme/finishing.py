"""Explicit, read-only-source SVG finishing with independently governed SESM tools."""
import hashlib
import json
import math
import re
import subprocess
import sys
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, __version__ as PILLOW_VERSION

from . import svg_converter
from .extraction import load_palette
from .identity import resolve_identity
from .output_names import artifact_file
from .pipeline import write_json
from .target_palette import toml_document
from .transactions import staged_directory

SCHEMA = 'aptlantis.finish-plan.v1'
RECEIPT = 'aptlantis.finish-receipt.v1'
SVG = 'http://www.w3.org/2000/svg'
ASSET_FIELDS = {'id', 'input', 'run', 'target', 'logical', 'palette', 'output', 'role', 'title', 'mode', 'theme_name', 'theme_version'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(command, *, payload=None):
    result = subprocess.run([str(x) for x in command], input=payload, text=True,
                            encoding='utf-8', capture_output=True, check=False)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip() or f'Tool failed: {command[0]}')
    return result.stdout


def local_path(base, value):
    if not isinstance(value, str) or not value:
        raise ValueError('Paths must be nonempty strings')
    return (base / value).resolve(strict=True)


def palette_rows(path):
    document = tomllib.loads(path.read_text(encoding='utf-8-sig'))
    if document.get('theme', {}).get('variant', 'dark') != 'dark':
        raise ValueError('Only recorded dark palettes are supported')
    if document.get('transformation', {}).get('schema') == 'aptlantis.target-palette.v1':
        groups = document['palette']
        if set(groups.get('canonical', {})) & set(groups.get('derived', {})):
            raise ValueError('Duplicate canonical/derived palette identity')
        colors = {**groups.get('canonical', {}), **groups.get('derived', {})}
        order = document['transformation']['token_order']
        if len(order) != len(set(order)) or set(order) != set(colors):
            raise ValueError('Target palette order does not match colors')
        rows = [(key, colors[key]) for key in order]
        canonical = document['source_palette']['canonical']
        for key, color in rows:
            if color['origin']['source'] not in canonical:
                raise ValueError('Unknown canonical origin: ' + key)
            original = canonical[color['origin']['source']]['hex']
            if type(color['origin']['derived']) is not bool or color['origin']['derived'] != (color['hex'].upper() != original.upper()):
                raise ValueError('Incorrect canonical/derived lineage: ' + key)
    else:
        load_palette(path)  # Validate the native canonical contract, including exactly 32 colors.
        colors = document['palette']['canonical']
        rows = list(colors.items())
    for key, color in rows:
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', color['hex']):
            raise ValueError('Invalid palette HEX: ' + key)
        rgb = list(bytes.fromhex(color['hex'][1:]))
        if color.get('rgb', rgb) != rgb:
            raise ValueError('Palette HEX/RGB disagreement: ' + key)
    if not rows:
        raise ValueError('Empty palette')
    return document, rows


def verify_swatch(source, document, rows):
    """Require the selected PNG to match its recorded pipeline swatch geometry/fills."""
    target = 'transformation' in document
    width, header, height = (1200, 70, 100) if target else (1024, 80, 72)
    with Image.open(source) as image:
        image = image.convert('RGB')
        if image.size != (width, header + math.ceil(len(rows) / 4) * height):
            raise ValueError('PNG dimensions do not match the structured palette swatch')
        for i, (key, color) in enumerate(rows):
            x, y = i % 4 * (width // 4), header + i // 4 * height
            box = (x + 10, y + 8, x + 291, y + 56) if target else (x + 12, y + 5, x + 66, y + 59)
            expected = tuple(bytes.fromhex(color['hex'][1:]))
            if image.crop(box).getextrema() != tuple((c, c) for c in expected):
                raise ValueError('PNG fill does not match structured palette: ' + key)
        return '#%02X%02X%02X' % image.getpixel((0, 0))


def palette_svg(item):
    rows = item['rows']
    width, cell, header, row_height = 1200, 300, 72, 105
    height = header + math.ceil(len(rows) / 4) * row_height
    ET.register_namespace('', SVG)
    root = ET.Element(f'{{{SVG}}}svg', {'width': str(width), 'height': str(height),
                                     'viewBox': f'0 0 {width} {height}'})
    def element(tag, attrs, text=None):
        node = ET.SubElement(root, f'{{{SVG}}}{tag}', {k: str(v) for k, v in attrs.items()})
        node.text = text
    element('rect', {'width': width, 'height': height, 'fill': item['background']})
    def text(x, y, value, size=12, available=276):
        element('text', {'x': x, 'y': y, 'fill': '#FFFFFF', 'font-family': 'monospace',
                         'font-size': size, 'textLength': min(len(value) * size * .62, available),
                         'lengthAdjust': 'spacingAndGlyphs'}, value)
    text(16, 34, item['title'], 20, width - 32)
    for i, (key, color) in enumerate(rows):
        x, y = (i % 4) * cell + 12, header + (i // 4) * row_height
        element('rect', {'x': x, 'y': y, 'width': cell - 24, 'height': 42,
                         'fill': color['hex'], 'data-color-id': key})
        text(x, y + 61, key)
        text(x, y + 79, color['hex'])
        if color.get('origin'):
            origin = color['origin']
            text(x, y + 97, ('derived' if origin['derived'] else 'canonical') + ' / ' + origin['source'])
    return ET.tostring(root, encoding='utf-8', xml_declaration=True) + b'\n'


def prepare(plan_path, output):
    """Resolve explicit selections and record all consulted source bytes without writes."""
    output = Path(output).resolve()
    plan_path = plan_path.resolve(strict=True)
    plan = tomllib.loads(plan_path.read_text(encoding='utf-8-sig'))
    if set(plan) - {'schema', 'assets'} or plan.get('schema') != SCHEMA or not isinstance(plan.get('assets'), list) or not plan['assets']:
        raise ValueError('Expected ' + SCHEMA + ' and a nonempty [[assets]] selection')
    base, sources, items, ids, filenames = plan_path.parent, {}, [], set(), set()
    def record(path):
        sha = digest(path)
        if str(path) in sources and sources[str(path)] != sha:
            raise ValueError('A source changed while reading the plan: ' + str(path))
        sources[str(path)] = sha
        return path
    record(plan_path)
    for spec in plan['assets']:
        if not isinstance(spec, dict) or set(spec) - ASSET_FIELDS:
            raise ValueError('Unknown asset fields')
        identifier = spec.get('id', '')
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*', identifier) or identifier in ids:
            raise ValueError('Asset IDs must be unique simple identifiers')
        ids.add(identifier)
        filename = spec.get('output', identifier + '.svg')
        if not isinstance(filename, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]*\.svg', filename, re.I) or re.match(r'^(con|prn|aux|nul|com[1-9]|lpt[1-9])\.', filename, re.I):
            raise ValueError('Output must be a simple SVG filename')
        if filename.casefold() in filenames:
            raise ValueError('Output filename collision')
        filenames.add(filename.casefold())
        mode, role = spec.get('mode', 'embed'), spec.get('role')
        if mode not in ('embed', 'trace', 'palette') or not isinstance(role, str) or not role:
            raise ValueError('Assets require a role and embed, trace or palette mode')
        if ('input' in spec) == ('run' in spec):
            raise ValueError('Select exactly one input file or pipeline run')
        document, rows, theme, identity_source = None, None, None, None
        if 'run' in spec:
            run = local_path(base, spec['run'])
            metadata = json.loads(record(run / 'run.json').read_text(encoding='utf-8-sig'))
            if metadata.get('schema') != 'aptlantis.theme-run.v1' or metadata.get('variant') != 'dark':
                raise ValueError('Not a dark pipeline run')
            if output == run or output.is_relative_to(run) or run.is_relative_to(output):
                raise ValueError('Finishing output must be separate from selected runs')
            theme = metadata
            identity_source = run / 'palette.toml'
            target = spec.get('target')
            logical = spec.get('logical', 'swatch.png' if target else 'palette.png')
            if target:
                source = artifact_file(run, target, logical, verify=True)
                if 'artifact_manifests' in metadata:
                    record(run / metadata['artifact_manifests'][target])
                if mode == 'palette':
                    if logical != 'swatch.png':
                        raise ValueError('Palette mode requires the recorded target swatch')
                    palette = record(artifact_file(run, target, 'palette.toml', verify=True))
                    tokens = json.loads(record(artifact_file(run, target, 'tokens.json', verify=True)).read_text(encoding='utf-8-sig'))
                    document, rows = palette_rows(palette)
                    if [(k, c['hex'], c.get('origin')) for k, c in rows] != [(k, c['hex'], c.get('origin')) for k, c in tokens['tokens'].items()]:
                        raise ValueError('Palette does not match recorded target colors/lineage')
            else:
                if logical != 'palette.png':
                    raise ValueError('Run-root selection supports only palette.png; use input for other files')
                source = run / logical
                if mode == 'palette':
                    document, rows = palette_rows(record(run / 'palette.toml'))
            if document and (document['theme']['name'] != metadata['name'] or
                             document['theme']['source_sha256'] != metadata['source_sha256'] or
                             document['theme'].get('theme_identity') != metadata.get('theme_identity')):
                raise ValueError('Palette identity/provenance does not match the selected run')
            if 'palette' in spec:
                raise ValueError('Run selections resolve their own palette')
        else:
            if 'target' in spec or 'logical' in spec:
                raise ValueError('target/logical require run')
            source = local_path(base, spec['input'])
            if 'palette' in spec:
                identity_source = record(local_path(base, spec['palette']))
                document, rows = palette_rows(identity_source)
                theme = document['theme']
        if 'theme_name' in spec and (not isinstance(spec['theme_name'], str) or not spec['theme_name']):
            raise ValueError('theme_name must be nonempty text')
        if spec.get('theme_name'):
            if theme and spec['theme_name'] != theme['name']:
                raise ValueError('Authored theme name conflicts with recorded identity')
            theme = theme or {'name': spec['theme_name']}
        if 'theme_version' in spec and not theme:
            raise ValueError('theme_version requires theme_name or recorded theme data')
        source = record(source.resolve(strict=True))
        if 'run' in spec and not source.is_relative_to(run):
            raise ValueError('Selected artifact escapes its pipeline run')
        if source.suffix.lower() != '.png':
            raise ValueError('Finishing accepts selected PNG inputs only')
        with Image.open(source) as image:
            if image.format != 'PNG' or getattr(image, 'n_frames', 1) != 1:
                raise ValueError('Finishing requires a single-frame PNG')
            dimensions = image.size
        if mode == 'palette' and rows is None:
            raise ValueError('Palette mode requires matching structured palette data')
        title = spec.get('title', source.stem)
        if not isinstance(title, str) or not title:
            raise ValueError('Asset title must be nonempty text')
        item = {'id': identifier, 'source': source, 'file': filename, 'mode': mode, 'role': role,
                'title': title, 'rows': rows, 'dimensions': dimensions}
        if mode == 'palette':
            item['background'] = verify_swatch(source, document, rows)
        metadata = {'sesm_version': '0.3.0',
                    'asset': {'id': identifier, 'role': role, 'title': title, 'tags': [role]},
                    'artifact': {'kind': 'svg-' + role, 'source_type': 'png', 'source_path': source.name,
                                 'output_path': filename, 'build_profile': mode},
                    'provenance': {'generated': True, 'generator': {'name': 'apt-theme finish', 'version': '0.1.0', 'language': 'Python'},
                                   'input_records': [{'path': source.name, 'record_id': sources[str(source)]}]},
                    'extra': {'conversion_method': mode, 'source_sha256': sources[str(source)]}}
        if theme:
            identity = resolve_identity(theme['name'], spec.get('theme_version'), source=identity_source, imported={'theme': theme})
            recorded = theme.get('theme_identity')
            if recorded and any(recorded.get(key) != getattr(identity, key) for key in ('version', 'prefix', 'slug')):
                raise ValueError('Recorded theme identity disagrees with its name/version')
            metadata['theme'] = {'id': identity.key, 'name': theme['name'], 'version': str(identity.version), 'mode': 'dark'}
            # Diagnostic source labels belong in the receipt, outside descriptive SESM.
            metadata['extra']['theme_identity'] = {k: getattr(identity, k) for k in ('version', 'prefix', 'slug')}
            item['identity_resolution'] = identity.record()
            item['recorded_theme_identity'] = recorded
        if rows:
            metadata['extra']['palette'] = [{'id': k, 'hex': c['hex'], **({'origin': c['origin']} if 'origin' in c else {})} for k, c in rows]
        item['metadata'] = metadata
        items.append(item)
    for name in sources:
        source = Path(name)
        if output == source or output in source.parents:
            raise ValueError('Finishing output must be separate from source/configuration directories')
    return items, sources


def configure(parser):
    parser.add_argument('plan', type=Path, help='explicit TOML asset selection')
    parser.add_argument('--output', type=Path, required=True, help='fresh finishing destination')
    parser.add_argument('--write', action='store_true', help='write finished assets; otherwise preview only')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--sesm-project', type=Path, default=Path(__file__).resolve().parents[2] / 'SESM-Metadata-Embedder')
    parser.add_argument('--sesm-standard', type=Path, default=Path('D:/.city_hall/SESM'))
    parser.add_argument('--sesm-python', default=sys.executable)
    parser.add_argument('--magick', default='magick')
    parser.add_argument('--vtracer', default='vtracer')


def finish(args):
    output = args.output.resolve()
    if output.exists():
        raise ValueError('Finishing requires a fresh output destination')
    items, sources = prepare(args.plan, output)
    embedder = (args.sesm_project / 'scripts' / 'Embed-SESM.py').resolve(strict=True)
    validator = (args.sesm_standard / 'Validate-SESM-Safe.py').resolve(strict=True)
    schema = (args.sesm_standard / 'svg_asset.schema.json').resolve(strict=True)
    tool_sources = {str(p): digest(p) for p in (embedder, validator, schema)}
    implementation_sources = {str(p): digest(p) for p in (Path(__file__), Path(svg_converter.__file__))}
    # Preview validates all planned metadata using the same schema dialect and format checker.
    code = ('import json,sys; from jsonschema import Draft202012Validator,FormatChecker; '
            's=json.load(open(sys.argv[1],encoding="utf-8"))["properties"]["sesm"]; '
            'v=Draft202012Validator(s,format_checker=FormatChecker()); '
            'errors=[e.message for d in json.load(sys.stdin) for e in v.iter_errors(d)]; '
            'print(json.dumps(errors)); sys.exit(bool(errors))')
    invoke([args.sesm_python, '-c', code, schema], payload=json.dumps([i['metadata'] for i in items]))
    tools = {'apt-theme': '0.1.0', 'pillow': PILLOW_VERSION, 'generator_python': sys.version.split()[0],
             'sesm_python': invoke([args.sesm_python, '--version']).strip(),
             'sesm_metadata_version': '0.3.0', 'sesm_sources': tool_sources,
             'implementation_sources': implementation_sources}
    if any(i['mode'] == 'trace' for i in items):
        svg_converter.check_vtracer(args.vtracer)
        tools['vtracer'] = svg_converter.run([args.vtracer, '--version'])
        tools['magick'] = svg_converter.run([args.magick, '-version']).splitlines()[0]
    result = {'schema': RECEIPT, 'written': False, 'output': str(output), 'sources': sources, 'tools': tools,
              'assets': [], 'warnings': [], 'native_application_acceptance': 'not performed'}
    if not args.write:
        result['assets'] = [{'id': i['id'], 'file': i['file'], 'mode': i['mode'], 'metadata': i['metadata'],
                             'schema_validation': 'passed', 'safe_profile': 'not performed'} for i in items]
        return result
    with staged_directory(output, prefix='apt-finish-') as stage:
        stage.mkdir()
        registry = {'assets': {i['file']: i['metadata'] for i in items}}
        (stage / 'sesm-metadata.toml').write_text(toml_document(registry), encoding='utf-8')
        for item in items:
            target = stage / item['file']
            settings = {'mode': item['mode']}
            if item['mode'] == 'palette':
                content = palette_svg(item)
            elif item['mode'] == 'embed':
                content = svg_converter.embed_svg(item['source'].read_bytes(), 'image/png', *item['dimensions'])
            else:
                converter_args = svg_converter.argument_parser().parse_args([
                    '--input', str(item['source']), '--output', str(target), '--mode', 'trace',
                    '--vtracer', args.vtracer, '--magick', args.magick])
                svg_converter.convert(item['source'], target, converter_args)
                settings.update({k: v for k, v in vars(converter_args).items()
                                 if k not in ('input', 'output', 'output_dir', 'dry_run', 'overwrite', 'recursive')})
                content = target.read_bytes()
            target.write_bytes(content)
            artwork_hash = digest(target)
            invoke([args.sesm_python, embedder, '--input', target, '--root', stage,
                    '--config', stage / 'sesm-metadata.toml', '--schema', schema, '--write'])
            validation = json.loads(invoke([args.sesm_python, validator, target, '--schema', schema, '--safe-profile', '--json']))
            validation['file'] = item['file']
            if validation['errors']:
                raise ValueError('SESM validation failed: ' + json.dumps(validation['errors']))
            # The sibling tool promises to preserve every non-SESM byte. Verify that promise.
            finished = target.read_text(encoding='utf-8')
            block = re.search(r'\n  <metadata id="sesm">.*?</metadata>', finished, re.S)
            if not block or (finished[:block.start()] + finished[block.end():]).encode('utf-8') != content:
                raise ValueError('SESM embedding changed artwork bytes')
            result['warnings'].extend({'asset': item['id'], **warning} for warning in validation['warnings'])
            result['assets'].append({'id': item['id'], 'file': item['file'], 'settings': settings,
                                     'sha256': digest(target), 'artwork_sha256': artwork_hash,
                                     'identity_resolution': item.get('identity_resolution'),
                                     'recorded_theme_identity': item.get('recorded_theme_identity'),
                                     'schema_validation': 'passed', 'validation': validation})
        for name, sha in {**sources, **tool_sources, **implementation_sources}.items():
            if digest(Path(name)) != sha:
                raise ValueError('A source or SESM tool changed during finishing: ' + name)
        result['written'] = True
        write_json(stage / 'finish-receipt.json', result)
    return result


def run(args):
    try:
        result = finish(args)
        envelope = {'status': 'warning' if result['warnings'] else 'ok', 'tool': 'apt-theme', 'version': '0.1.0',
                    'data': result, 'warnings': result['warnings'], 'errors': []}
        print(json.dumps(envelope) if args.json else
              f"{'Finished' if result['written'] else 'Previewed'} {len(result['assets'])} selected assets; "
              f"{len(result['warnings'])} safe-profile warnings. " +
              (f"Receipt: {args.output / 'finish-receipt.json'}" if result['written'] else 'No files written.'))
        return 0
    except (ValueError, OSError, KeyError, TypeError, OverflowError, ET.ParseError) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        if args.json:
            print(json.dumps({'status': 'error', 'tool': 'apt-theme', 'version': '0.1.0', 'data': None,
                              'warnings': [], 'errors': [{'code': 'finishing_failed', 'category': 'runtime', 'message': str(exc)}]}))
        return 1
