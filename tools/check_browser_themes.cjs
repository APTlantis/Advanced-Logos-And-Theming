// Real offline runtime checks, restricted to the supplied generated pilot root.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const [run,playwright,executablePath]=process.argv.slice(2);
const root=path.resolve(run),{chromium}=require(playwright);
const mime={'.html':'text/html','.js':'text/javascript','.mjs':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json','.md':'text/plain'};
const server=http.createServer((req,res)=>{const dest=path.resolve(root,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!dest.startsWith(root+path.sep)){res.writeHead(403).end();return;}try{res.setHeader('Content-Type',mime[path.extname(dest)]||'application/octet-stream');res.end(fs.readFileSync(dest));}catch{res.writeHead(404).end();}});
(async()=>{await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin='http://127.0.0.1:'+server.address().port;const browser=await chromium.launch({headless:true,executablePath});const record={browser:browser.version(),checks:[],errors:[],external_requests:[],downstream_application_acceptance:'pending'};
try{const page=await browser.newPage();page.on('pageerror',e=>record.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')record.errors.push(m.text())});await page.route('**/*',route=>{const url=route.request().url();if(url.startsWith(origin+'/')||url.startsWith('data:'))return route.continue();record.external_requests.push(url);return route.abort()});
const audit=async selector=>page.evaluate(selector=>{
 const rgb=s=>(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);
 const lum=rgb=>rgb.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
 const failures=[];
 for(const root of document.querySelectorAll(selector))for(const el of [root,...root.querySelectorAll('*')]){
  if(el.tagName==='INPUT'&&!['text','search'].includes(el.type))continue;
  if(!el.getClientRects().length||(!['INPUT','BUTTON'].includes(el.tagName)&&![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())))continue;
  let bg=el;while(bg&&['rgba(0, 0, 0, 0)','transparent'].includes(getComputedStyle(bg).backgroundColor))bg=bg.parentElement;
  if(!bg)continue;const a=lum(rgb(getComputedStyle(el).color)),b=lum(rgb(getComputedStyle(bg).backgroundColor));const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
  if(ratio<4.5-1e-6)failures.push({text:el.textContent.slice(0,30),ratio});
 }return failures;
},selector);
for(const theme of ['black-gold','ada']){
 for(const width of [1440,390]){
  await page.setViewportSize({width,height:1000});await page.goto(origin+'/'+theme+'/markdown/examples.html');await page.waitForSelector('html[data-ready=true]');
  const md=await page.evaluate(()=>({kind:'markdown',width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,headings:document.querySelectorAll('#document h1,#document h2,#document h3,#document h4,#document h5,#document h6').length,tasks:document.querySelectorAll('#document input[type=checkbox]').length,tokens:document.querySelectorAll('#document .token').length,align:[...document.querySelector('#document table').querySelectorAll('th')].map(e=>getComputedStyle(e).textAlign.replace('-webkit-','')),unsafe:!!window.unsafeMarkdownExecuted||!!document.querySelector('#document script,#document [onerror],#document a[href^="javascript:"]'),hostToken:getComputedStyle(document.getElementById('outside-sentinel')).getPropertyValue('--apt-background'),image:[...document.querySelectorAll('#document img')].every(i=>i.naturalWidth>0),tables:[...document.querySelectorAll('#document table')].map(t=>({display:getComputedStyle(t).display,overflow:t.parentElement.scrollWidth>t.parentElement.clientWidth})),alerts:document.querySelectorAll('#extras .markdown-alert').length}));
  md.contrast_failures=await audit('#document,#extras');assert.deepEqual(md.contrast_failures,[]);record.checks.push({theme,...md});assert.equal(md.overflow,false);assert.equal(md.unsafe,false);assert.equal(md.hostToken,'');assert.equal(md.headings,6);assert.equal(md.tasks,2);assert.ok(md.tokens>10);assert.deepEqual(md.align,['left','center','right']);assert.equal(md.image,true);assert.equal(md.alerts,5);assert.ok(md.tables.every(t=>t.display==='table'));if(width===390)assert.ok(md.tables.some(t=>t.overflow));
  await page.locator('#document a').first().focus();assert.equal(await page.locator('#document a').first().evaluate(e=>getComputedStyle(e).outlineStyle),'solid');
  await page.screenshot({path:path.join(root,theme,'markdown','browser-'+width+'.png')});
 }
 for(const version of [5,6]){
  await page.setViewportSize({width:1100,height:1100});await page.goto(origin+'/'+theme+'/codemirror'+version+'/examples.html');await page.waitForSelector('html[data-ready=true]');
  const initial=await page.evaluate(version=>({kind:'codemirror'+version,editors:Object.keys(editors),themed:getComputedStyle(document.querySelector('#javascript '+(version===5?'.CodeMirror':'.cm-editor'))).backgroundColor,unrelated:getComputedStyle(document.querySelector('#unrelated '+(version===5?'.CodeMirror':'.cm-editor'))).backgroundColor,tokens:version===5?document.querySelectorAll('#javascript .cm-keyword,#python .cm-keyword').length:document.querySelectorAll('#javascript .cm-line span,#python .cm-line span').length}),version);
  initial.contrast_failures=await audit('#javascript .CodeMirror,#python .CodeMirror,#markdown .CodeMirror,#javascript .cm-editor,#python .cm-editor,#markdown .cm-editor');assert.deepEqual(initial.contrast_failures,[]);assert.equal(initial.editors.length,4);assert.notEqual(initial.themed,initial.unrelated);assert.ok(initial.tokens>0);
  const content=page.locator('#javascript '+(version===5?'textarea':'.cm-content'));await content.focus();await page.keyboard.press('Control+End');await page.keyboard.type('\n// typed locally');
  assert.ok(await page.evaluate(v=>v===5?editors.javascript.getValue().includes('typed locally'):editors.javascript.state.doc.toString().includes('typed locally'),version));
  await page.evaluate(v=>{if(v===5){editors.javascript.setSelection({line:1,ch:0},{line:2,ch:10});editors.javascript.focus()}else{editors.javascript.dispatch({selection:{anchor:0,head:25}});editors.javascript.focus()}},version);
  await page.waitForTimeout(150);assert.ok(await page.locator('#javascript '+(version===5?'.CodeMirror-selected':'.cm-selectionBackground')).count()>0);
  await page.keyboard.press('Control+f');const input=page.locator('#javascript '+(version===5?'.CodeMirror-dialog input':'.cm-search input[name=search]'));await input.waitFor();await input.fill('answer');await page.keyboard.press('Enter');await page.waitForTimeout(120);const matches=await page.locator('#javascript '+(version===5?'.cm-searching':'.cm-searchMatch')).count();assert.ok(matches>0);const searchContrast=await audit('#javascript .CodeMirror-dialog,#javascript .cm-search');assert.deepEqual(searchContrast,[]);await page.keyboard.press('Escape');
  await page.evaluate(v=>{if(v===5){editors.javascript.setCursor({line:1,ch:1});editors.javascript.focus();editors.javascript.showHint({hint:()=>({list:['answer','value'],from:editors.javascript.getCursor(),to:editors.javascript.getCursor()}),completeSingle:false})}else{editors.javascript.dispatch({selection:{anchor:0}});editors.javascript.focus();CM.startCompletion(editors.javascript)}},version);
  const popup=page.locator(version===5?'#javascript .CodeMirror-hints':'#javascript .cm-tooltip-autocomplete');await popup.waitFor();const completionContrast=await audit(version===5?'#javascript .CodeMirror-hints':'#javascript .cm-tooltip-autocomplete');assert.deepEqual(completionContrast,[]);const popupStyle=await popup.evaluate(e=>({bg:getComputedStyle(e).backgroundColor,fg:getComputedStyle(e).color}));await page.keyboard.press('Escape');
  const bracket=await page.evaluate(v=>{const text=v===5?editors.javascript.getValue():editors.javascript.state.doc.toString();const pos=text.indexOf('(')+1;if(v===5)editors.javascript.setCursor(editors.javascript.posFromIndex(pos));else editors.javascript.dispatch({selection:{anchor:pos}});return pos},version);assert.ok(bracket>0);await page.waitForTimeout(150);assert.ok(await page.locator('#javascript '+(version===5?'.CodeMirror-matchingbracket':'.cm-matchingBracket')).count()>0);
  record.checks.push({theme,...initial,typing:true,selection:true,search_matches:matches,completion:popupStyle,bracket_matching:true});await page.screenshot({path:path.join(root,theme,'codemirror'+version,'browser-1100.png')});
 }
}
assert.deepEqual(record.external_requests,[]);assert.deepEqual(record.errors,[]);record.passed=true;
}finally{fs.writeFileSync(path.join(root,'browser-validation.json'),JSON.stringify(record,null,2)+'\n');await browser.close();await new Promise(resolve=>server.close(resolve));}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
