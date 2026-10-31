// Exercise authored navigation directly from disk, with all network requests blocked.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require(process.env.VOLUME_NODE_MODULES+'/playwright');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({headless:true});const results=[];
 try{const files=[path.join(root,'index.html'),...JSON.parse(fs.readFileSync(path.join(root,'validation/build.json'))).map(x=>path.join(root,x.stem,'index.html'))];
 for(const file of files)for(const width of [1440,390]){
  const page=await browser.newPage({viewport:{width,height:1000}});const errors=[],network=[],failed=[];
  await page.route(/^https?:/,route=>{network.push(route.request().url());return route.abort()});page.on('pageerror',e=>errors.push(e.message));page.on('requestfailed',r=>failed.push(r.url()));
  await page.goto(pathToFileURL(file).href,{waitUntil:'load'});
  await page.evaluate(async()=>{await Promise.all([...document.images].map(async image=>{image.loading='eager';try{await image.decode()}catch{}}))});
  const metrics=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth+1,missingImages:[...document.images].filter(x=>!x.complete||!x.naturalWidth).map(x=>x.getAttribute('src')),details:document.querySelectorAll('details').length}));
  if(metrics.details){await page.locator('summary').first().click();if(!await page.locator('details').first().getAttribute('open').then(x=>x!==null))throw Error('Notes failed to expand')}
  const name=path.basename(path.dirname(file));await page.screenshot({path:path.join(root,'validation',`index-${name}-${width}.png`)});
  results.push({file:path.relative(root,file),width,...metrics,errors,network,failed});await page.close();
 }
 fs.writeFileSync(path.join(root,'validation/index-browser.json'),JSON.stringify(results,null,2));
 if(results.some(r=>r.overflow||r.missingImages.length||r.errors.length||r.network.length||r.failed.length))throw Error('Index check failed; inspect receipt');console.log('18 direct-file desktop/mobile states passed, notes expand, no missing images or remote requests');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
