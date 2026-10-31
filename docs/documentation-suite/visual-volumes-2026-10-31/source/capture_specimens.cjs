// Capture verified copies through a loopback-only static server. No vendor rebuild.
const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require(process.env.VOLUME_NODE_MODULES+'/playwright');
const base=path.resolve(__dirname,'..');
const inventories=JSON.parse(fs.readFileSync(path.join(base,'validation/template-inventory.json')));
const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.mjs':'text/javascript','.svg':'image/svg+xml','.json':'application/json','.png':'image/png','.woff2':'font/woff2'};
const server=http.createServer((req,res)=>{try{let file=path.resolve(base,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));if(!file.startsWith(base+path.sep))throw Error('outside root');const b=fs.readFileSync(file);res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});res.end(b)}catch{res.writeHead(404);res.end('Not found')}});
server.listen(0,'127.0.0.1',async()=>{
 let browser;try{
 browser=await chromium.launch({headless:true});const port=server.address().port;const records=[];
 for(const item of inventories){
  const specs=[['website','components'],['svg','product-illustration'],['data_visualization','bars']];
  if(item.stem==='dnf-clojure')specs.splice(0,3,['markdown','examples'],['codemirror5','examples'],['codemirror6','examples']);
  for(const [target,kind] of specs){
   const dir=path.join(base,item.stem,'artifacts',target);const manifest=JSON.parse(fs.readFileSync(path.join(dir,`${item.stem}-${target.replaceAll('_','-')}-files.json`)));
   let e=manifest.files.find(x=>x.file.endsWith(`-${kind}.svg`))||manifest.files.find(x=>x.file.endsWith(`-${kind}.html`));if(!e)throw Error(target+' '+kind);
   const page=await browser.newPage({viewport:{width:1440,height:960},deviceScaleFactor:1});const errors=[],remote=[];
   await page.route('**/*',route=>{const u=route.request().url();if(/^https?:/.test(u)&&!u.startsWith(`http://127.0.0.1:${port}/`)){remote.push(u);return route.abort()}return route.continue()});
   page.on('pageerror',e=>errors.push(e.message));
   const url=`http://127.0.0.1:${port}/${item.stem}/artifacts/${target}/${e.file}`;
   await page.goto(url,{waitUntil:'networkidle'});const output=path.join(base,item.stem,'figures',`${target}-specimen.png`);if(e.file.endsWith('.svg'))await page.locator('svg').screenshot({path:output});else await page.screenshot({path:output,fullPage:false});
   records.push({stem:item.stem,target,source:`${item.stem}/artifacts/${target}/${e.file}`,viewport:[1440,960],externalRequests:remote,errors,caption:target==='data_visualization'?'Illustrative generated fixture; not project measurements.':'Actual generated specimen, rendered in Chromium.'});await page.close();
  }
 }
 fs.writeFileSync(path.join(base,'validation/specimen-browser.json'),JSON.stringify(records,null,2));console.log(`Captured ${records.length} actual specimens`);
 }catch(e){console.error(e);process.exitCode=1}finally{if(browser)await browser.close();server.close()}
});
