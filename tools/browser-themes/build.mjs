import {build} from 'esbuild';
import {mkdir, copyFile, readFile, writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const out = new URL('../../apt_theme/vendor/browser-themes/', import.meta.url);
await mkdir(out, {recursive:true});
await build({stdin:{contents:`export {marked} from 'marked'; export {default as DOMPurify} from 'dompurify';`,resolveDir: new URL('.',import.meta.url).pathname.replace(/^\/(\w:)/,'$1')},bundle:true,format:'iife',globalName:'AptMarkdown',platform:'browser',outfile:new URL('markdown.js',out).pathname.replace(/^\/(\w:)/,'$1'),minify:true});
await build({stdin:{contents:`export {EditorView,drawSelection,lineNumbers,highlightActiveLine,highlightActiveLineGutter} from '@codemirror/view'; export {EditorState} from '@codemirror/state'; export {HighlightStyle,syntaxHighlighting,bracketMatching,defaultHighlightStyle} from '@codemirror/language'; export {tags} from '@lezer/highlight'; export {defaultKeymap,history,historyKeymap} from '@codemirror/commands'; export {search,searchKeymap,openSearchPanel} from '@codemirror/search'; export {autocompletion,completionKeymap,startCompletion} from '@codemirror/autocomplete'; export {keymap} from '@codemirror/view'; export {markdown} from '@codemirror/lang-markdown'; export {javascript} from '@codemirror/lang-javascript'; export {python} from '@codemirror/lang-python';`,resolveDir:new URL('.',import.meta.url).pathname.replace(/^\/(\w:)/,'$1')},bundle:true,format:'esm',platform:'browser',outfile:new URL('cm6-runtime.mjs',out).pathname.replace(/^\/(\w:)/,'$1'),minify:true});
const cmFiles=['lib/codemirror.js','lib/codemirror.css','mode/markdown/markdown.js','mode/javascript/javascript.js','mode/python/python.js','addon/search/search.js','addon/search/searchcursor.js','addon/search/match-highlighter.js','addon/dialog/dialog.js','addon/dialog/dialog.css','addon/edit/matchbrackets.js','addon/selection/active-line.js','addon/selection/mark-selection.js','addon/hint/show-hint.js','addon/hint/show-hint.css'];
const files=['markdown.js','cm6-runtime.mjs'];
for(const file of cmFiles){const dest='cm5-'+file.replaceAll('/','-');await copyFile(new URL('node_modules/codemirror/'+file,import.meta.url),new URL(dest,out));files.push(dest);}
const lock=JSON.parse(await readFile(new URL('package-lock.json',import.meta.url),'utf8'));
const packages=[];
for(const [path,pkg] of Object.entries(lock.packages)){
 if(!path || /esbuild/.test(path))continue;
 const name=path.replace('node_modules/','');const license='LICENSE-'+name.replaceAll('/','-').replace('@','')+'.txt';
 let text;for(const candidate of ['LICENSE','LICENSE.md','LICENSE.txt']){try{text=await readFile(new URL(path+'/'+candidate,import.meta.url),'utf8');break;}catch{}}
 if(!text)throw Error('Missing license '+name);
 await writeFile(new URL(license,out),text);files.push(license);packages.push({name,version:pkg.version,integrity:pkg.integrity,license});
}
await copyFile(new URL('package-lock.json',import.meta.url),new URL('package-lock.json',out));files.push('package-lock.json');
await writeFile(new URL('manifest.json',out),JSON.stringify({schema:'aptlantis.browser-theme-assets.v1',packages,files:await Promise.all(files.map(async file=>({file,sha256:createHash('sha256').update(await readFile(new URL(file,out))).digest('hex')})))},null,2)+'\n');
