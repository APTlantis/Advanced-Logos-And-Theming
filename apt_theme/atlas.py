"""Read-only Chromatic Atlas snapshots from explicitly selected pipeline runs."""
import fnmatch
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

from .colors import from_rgb, lab
from .extraction import load_palette
from .identity import PREFIXES, resolve_identity
from .output_names import SCHEMA as ARTIFACT_SCHEMA

SCHEMA = 'aptlantis.chromatic-atlas.v1'
ASSETS = Path(__file__).parent / 'atlas_assets'
DEFAULT_PATTERNS = tuple(prefix + '-*' for prefix in PREFIXES.values())


def snapshot(collection, patterns=DEFAULT_PATTERNS):
    collection = Path(collection).resolve(strict=True)
    if not collection.is_dir():
        raise ValueError('Collection must be a directory')
    if not patterns or any('/' in p or '\\' in p or p in ('.','..') for p in patterns):
        raise ValueError('Include patterns must name immediate child runs only')
    runs = sorted(p for p in collection.iterdir() if p.is_dir() and any(fnmatch.fnmatchcase(p.name, pat) for pat in patterns))
    if not runs:
        raise ValueError('No matching theme runs')
    data = {'schema':SCHEMA,'collection':collection.name,'include':list(patterns),'themes':[],
            'canonical':[],'tokens':[],'sources':[],'findings':[],
            'limits':{'read_only':True,'near_neutral_chroma':.02,'distance':'Euclidean OKLab (L,a,b); unscaled',
                      'projection':'OKLab a,b discards lightness; hue/lightness omits near-neutral colors',
                      'usage':'Exported token lineage; native property/selector usage is not inferred'}}
    sources = {}
    def read(path, kind):
        content = path.read_bytes()
        key = path.relative_to(collection).as_posix()
        digest = hashlib.sha256(content).hexdigest()
        sources[path] = digest
        data['sources'].append({'path':key,'sha256':digest,'kind':kind})
        return content.decode('utf-8-sig'), key
    for run in runs:
        _, palette_path = read(run/'palette.toml','canonical_palette')
        colors, raw = load_palette(run/'palette.toml')
        text, run_path = read(run/'run.json','theme_run')
        metadata = json.loads(text)
        if metadata.get('schema') != 'aptlantis.theme-run.v1' or metadata.get('variant') != 'dark':
            raise ValueError('Expected dark pipeline run: '+run.name)
        canonical = raw.get('palette',{}).get('canonical',{})
        if set(canonical) != set(colors):
            raise ValueError('Expected 32 canonical palette entries: '+run.name)
        theme_id = run.name
        theme = {'id':theme_id,'name':metadata['name'].removeprefix('Aptlantis-').removeprefix('Aptlantis '),
                 'run':run.name,'family':run.name.split('-',1)[0],'palette_source':palette_path,'run_source':run_path,
                 'upstream_source_sha256':raw.get('theme',{}).get('source_sha256'),
                 'targets':[],'roles':{},'findings':metadata.get('semantic_findings',[])}
        if 'theme_identity' in metadata:
            identity = resolve_identity(metadata['name'], metadata['theme_identity']['version'])
            if any(metadata['theme_identity'].get(key) != identity.record()[key] for key in ('version', 'prefix', 'slug')):
                raise ValueError('Theme identity mismatch: ' + run.name)
            theme['family'] = identity.prefix
            theme['theme_version'] = identity.version
        if (run/'semantics.json').exists():
            text, _ = read(run/'semantics.json','semantic_assignments')
            semantics = json.loads(text)
            theme['roles'] = semantics['roles']
            if any(slot not in colors for slot in theme['roles'].values()):
                raise ValueError('Unknown semantic source in '+run.name)
        else:
            data['findings'].append({'theme_id':theme_id,'kind':'missing_semantics','message':'Semantic assignments unavailable; no assignments inferred.'})
        for slot, c in colors.items():
            original = canonical[slot]
            if original.get('rgb',c['rgb']) != c['rgb']:
                raise ValueError('Canonical HEX/RGB disagreement: '+run.name+'/'+slot)
            data['canonical'].append({'id':theme_id+':'+slot,'theme_id':theme_id,'slot':slot,
                'hex':original.get('hex',c['hex']),'rgb':c['rgb'],'oklch':c['oklch'],'oklab':lab(c),
                'stored_oklch':original.get('oklch'),'hue_defined':c['oklch'][1]>=.02,
                'roles':[role for role, ref in theme['roles'].items() if ref==slot],
                'source':palette_path,'source_kind':'canonical'})
        for target in metadata.get('targets',[]):
            if not isinstance(target,str) or '/' in target or '\\' in target or target in ('.','..'):
                raise ValueError('Unsafe target name')
            paths = {}
            receipts = {}
            if 'artifact_manifests' in metadata:
                manifest_path = metadata['artifact_manifests'].get(target)
                if not isinstance(manifest_path, str) or Path(manifest_path).parts != (target, Path(manifest_path).name) or '\\' in manifest_path:
                    raise ValueError('Unsafe artifact manifest path')
                text, _ = read(run/manifest_path, 'artifact_manifest')
                manifest = json.loads(text)
                if manifest.get('schema') != ARTIFACT_SCHEMA or manifest.get('target') != target or manifest.get('theme_identity') != metadata.get('theme_identity'):
                    raise ValueError('Artifact manifest identity mismatch')
                for record in manifest['files']:
                    filename, logical = record['file'], record['logical_name']
                    if not isinstance(filename, str) or Path(filename).name != filename or filename in ('.', '..') or '/' in filename or '\\' in filename:
                        raise ValueError('Unsafe artifact filename')
                    if logical in paths or filename in paths.values():
                        raise ValueError('Duplicate artifact identity')
                    paths[logical], receipts[filename] = filename, record['sha256']
                if 'tokens.json' not in paths:
                    raise ValueError('Artifact manifest omits target tokens')
            file = run/target/paths.get('tokens.json', 'tokens.json')
            if not file.exists():
                data['findings'].append({'theme_id':theme_id,'kind':'missing_target','target':target,'message':'Declared target has no tokens.json; lineage omitted.'})
                continue
            text, target_path = read(file,'exported_tokens')
            if receipts and hashlib.sha256(file.read_bytes()).hexdigest() != receipts[file.name]:
                raise ValueError('Artifact hash mismatch: ' + target_path)
            result = json.loads(text)
            if result.get('target') != target:
                raise ValueError('Target identity mismatch: '+target_path)
            count = 0
            for key, token in result['tokens'].items():
                origin = token.get('origin',{})
                slot = origin.get('source')
                if slot not in colors:
                    raise ValueError('Unknown token source: '+target_path+'/'+key)
                actual = from_rgb(token['rgb'])
                if actual['hex'] != token['hex'].upper():
                    raise ValueError('Token HEX/RGB disagreement: '+target_path+'/'+key)
                derived = actual['hex'] != colors[slot]['hex']
                if bool(origin.get('derived')) != derived:
                    raise ValueError('Token derived flag disagreement: '+target_path+'/'+key)
                data['tokens'].append({'id':theme_id+':'+target+':'+key,'canonical_id':theme_id+':'+slot,
                    'theme_id':theme_id,'target':target,'key':key,'hex':token['hex'],'rgb':actual['rgb'],
                    'oklch':actual['oklch'],'oklab':lab(actual),'derived':derived,
                    'purpose':origin.get('purpose',''),'requested_oklch':origin.get('requested_oklch'),
                    'gamut_mapped':bool(origin.get('gamut_mapped')),'source':target_path})
                count += 1
            preview = next((paths.get(name, name) for name in ('examples.html', 'preview.svg') if (run/target/paths.get(name, name)).is_file()), None)
            theme['targets'].append({'example':('examples/'+run.name+'/'+target+'/'+preview) if preview else None,'id':target,'token_count':count,'source':target_path,
                                     'contrast_failures':result.get('contrast_failures')})
        data['themes'].append(theme)
    data['counts'] = {'themes':len(data['themes']),'canonical':len(data['canonical']),
                      'exported_tokens':len(data['tokens']),'sources':len(data['sources'])}
    # Confirm all inputs stayed unchanged while the snapshot was assembled.
    if any(hashlib.sha256(path.read_bytes()).hexdigest()!=digest for path,digest in sources.items()):
        raise ValueError('A source changed during snapshot construction; retry with a stable collection')
    return data


def build(collection, output, patterns=DEFAULT_PATTERNS, overwrite=False):
    collection = Path(collection).resolve(strict=True)
    output = Path(output).resolve()
    if output == collection or output in collection.parents or output.is_relative_to(collection):
        raise ValueError('Atlas output must be separate from the source collection')
    if output.exists():
        if not overwrite:
            raise ValueError('Output already exists; use --overwrite explicitly')
        marker = output/'.atlas-run.json'
        if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('schema')!=SCHEMA:
            raise ValueError('Refusing to overwrite a non-atlas directory')
    data = snapshot(collection,patterns)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='apt-atlas-',dir=output.parent) as temp:
        stage = Path(temp)/'atlas'
        shutil.copytree(ASSETS,stage)
        example_files = []
        for theme in data['themes']:
            for target in theme['targets']:
                if not target.get('example'):
                    continue
                source_dir = collection/theme['run']/target['id']
                dest_dir = stage/'examples'/theme['run']/target['id']
                for file in sorted(p for p in source_dir.rglob('*') if p.is_file()):
                    if not file.resolve().is_relative_to(collection):
                        raise ValueError('Example asset escapes the selected collection')
                    content = file.read_bytes()
                    dest = dest_dir/file.relative_to(source_dir)
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes(content)
                    example_files.append({'source':file.relative_to(collection).as_posix(),
                                          'file':dest.relative_to(stage).as_posix(),
                                          'sha256':hashlib.sha256(content).hexdigest()})
        if any(hashlib.sha256((collection/item['source']).read_bytes()).hexdigest()!=item['sha256'] for item in example_files):
            raise ValueError('An example changed while copying; retry with a stable collection')
        if any(hashlib.sha256((collection/item['path']).read_bytes()).hexdigest()!=item['sha256'] for item in data['sources']):
            raise ValueError('A data source changed while copying examples; retry with a stable collection')
        (stage/'examples-manifest.json').write_text(json.dumps({'schema':'aptlantis.atlas-examples.v1','files':example_files},indent=2)+'\n',encoding='utf-8')
        data['counts']['offline_examples'] = sum(bool(t.get('example')) for theme in data['themes'] for t in theme['targets'])
        payload = json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
        (stage/'atlas.json').write_text(payload+'\n',encoding='utf-8')
        # Inline data supports both file:// use and a loopback static server, without fetching source paths.
        (stage/'atlas-data.js').write_text('window.ATLAS_DATA='+payload.replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')+';\n',encoding='utf-8')
        (stage/'.atlas-run.json').write_text(json.dumps({'schema':SCHEMA,'counts':data['counts']},indent=2)+'\n',encoding='utf-8')
        (stage/'README.md').write_text('# Chromatic Atlas local snapshot\n\nOpen index.html directly, or serve only this directory over loopback HTTP. atlas.json is the inspectable snapshot; atlas-data.js contains identical data for offline loading. Sources are hashed and read only at snapshot generation. Refresh explicitly using apt-theme atlas. Browser selections are temporary and never modify palettes. Copied offline examples are listed in the inspector; examples-manifest.json records all copied asset hashes. CodeMirror 6 examples require a local HTTP server serving this Atlas directory.\n\nThe OKLab plot omits L from its projection; nearest-neighbor distances use all L,a,b coordinates. Near-neutral hue is not treated as red. Exported token lineage is separate from proven native property/selector usage.\n',encoding='utf-8')
        if output.exists():
            backup = Path(temp)/'previous'
            output.rename(backup)
            try:
                stage.rename(output)
            except BaseException:
                backup.rename(output)
                raise
        else:
            stage.rename(output)
    return {'schema':SCHEMA,**data['counts'],'findings':data['findings'],'output':str(output),'read_only':True}


def configure(parser):
    parser.add_argument('input',type=Path,help='collection directory containing pipeline runs')
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--include',nargs='+',default=list(DEFAULT_PATTERNS),help='immediate child run patterns; default apt-* dnf-* rpm-* yum-* eopkg-*')
    parser.add_argument('--overwrite',action='store_true')
    parser.add_argument('--json',action='store_true')


def run(args):
    print('Building read-only Chromatic Atlas snapshot...',file=sys.stderr)
    result = build(args.input,args.output,args.include,args.overwrite)
    envelope = {'status':'warning' if result['findings'] else 'ok','tool':'apt-theme','version':'0.1.0',
                'data':result,'warnings':result['findings'],'errors':[]}
    print(json.dumps(envelope) if args.json else f"Atlas: {result['themes']} themes, {result['canonical']} canonical colors; open {args.output / 'index.html'}")
    return 0
