const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.argv[2]);
(async () => {
 const root = path.resolve(__dirname,'..');
 const recordPath = path.join(root,'migration/website-target-acceptance-2026-10-09.json');
 const record = JSON.parse(fs.readFileSync(recordPath,'utf8'));
 const browser = await chromium.launch({headless:true,executablePath:process.argv[3]});
 const errors=[],requests=[],checks=[];
 try {
  const context = await browser.newContext();
  await context.route(/^https?:/,r=>{requests.push(r.request().url());return r.abort()});
  const page = await context.newPage();
  page.on('pageerror',e=>errors.push(String(e)));
  for (const review of record.reviews) {
   const directory=path.join(root,record.pilot,review.folder,'website');
   for (const file of ['landing.html','components.html']) {
    for (const width of [1440,390]) {
     await page.setViewportSize({width,height:1000});
     await page.goto(pathToFileURL(path.join(directory,file)).href);
     const state=await page.evaluate(()=>{
      const rgb=s=>(s.match(/[\d.]+/g)||[]).slice(0,3).map(Number);
      const lum=c=>{const v=c.map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4});return v[0]*.2126+v[1]*.7152+v[2]*.0722};
      const failures=[];let textCount=0;
      for (const el of document.body.querySelectorAll('*')) {
       if (!el.getClientRects().length||['SCRIPT','STYLE','OPTION'].includes(el.tagName))continue;
       if (![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;
       const style=getComputedStyle(el);let bg=el;
       while(bg&&getComputedStyle(bg).backgroundColor==='rgba(0, 0, 0, 0)')bg=bg.parentElement;
       if (!bg)continue;
       const a=lum(rgb(style.color)),b=lum(rgb(getComputedStyle(bg).backgroundColor));
       const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
       const large=parseFloat(style.fontSize)>=24||(parseFloat(style.fontSize)>=18.66&&parseInt(style.fontWeight)>=700);
       if(ratio<(large?3:4.5))failures.push({text:el.textContent.slice(0,65),ratio});
       textCount++;
      }
      return {overflow:document.documentElement.scrollWidth>innerWidth,textCount,failures};
     });
     assert.equal(state.overflow,false,`${review.folder} ${file} ${width}`);
     assert.deepEqual(state.failures,[],`${review.folder} ${file} ${width} text contrast`);
     if(file==='components.html') {
      await page.getByRole('button',{name:'Open dialog',exact:true}).click();
      assert.equal(await page.locator('dialog').evaluate(d=>d.open),true);
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('dialog').evaluate(d=>d.open),false);
      const button=page.getByRole('button',{name:'Save draft (demo)',exact:true});
      await button.focus();
      assert.equal(await button.evaluate(b=>getComputedStyle(b).outlineStyle),'solid');
      const rest=await button.evaluate(b=>getComputedStyle(b).backgroundColor);
      await button.hover();
      const hover=await button.evaluate(b=>getComputedStyle(b).backgroundColor);
      assert.notEqual(rest,hover);
      await page.mouse.down();
      const pressed=await button.evaluate(b=>getComputedStyle(b).backgroundColor);
      await page.mouse.up();
      assert.notEqual(pressed,hover);
      await page.locator('#name').fill('Local specimen');
      await button.click();
      assert.equal(await page.locator('#name').inputValue(),'Local specimen');
     } else {
      await page.locator('details').first().locator('summary').click();
      assert.equal(await page.locator('details').first().evaluate(d=>d.open),true);
     }
     checks.push({folder:review.folder,file,width,...state});
     if(width===1440)await page.screenshot({path:path.join(root,record.pilot,review.folder,file.replace('.html','.png')),fullPage:true});
    }
   }
  }
  assert.deepEqual(errors,[]);assert.deepEqual(requests,[]);
  record.browser={version:browser.version(),checks,errors,blocked_network_requests:requests,limits:'Chromium specimen rendering; production framework integration and screen-reader acceptance not evaluated'};
  fs.writeFileSync(recordPath,JSON.stringify(record,null,2)+'\n');
  console.log(`${checks.length} responsive website checks, visible-text contrast, dialog, focus, action states and offline interactions passed.`);
 } finally {await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
