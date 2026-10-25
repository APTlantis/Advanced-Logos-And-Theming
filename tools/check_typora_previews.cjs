// Browser simulation only; never installs or activates a Typora theme.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const [run, playwright, executablePath] = process.argv.slice(2);
const {chromium} = require(playwright);
const artifactFile=require('./artifact_paths.cjs');
(async () => {
 const directory = path.resolve(run, 'typora');
 const browser = await chromium.launch({headless:true, ...(executablePath ? {executablePath} : {})});
 const record = {browser:browser.version(), checks:[], external_requests:[], errors:[], native_typora_acceptance:'pending'};
 try {
  const page = await browser.newPage();
  page.on('pageerror', e => record.errors.push(String(e)));
  page.on('console', m => {if(m.type()==='error')record.errors.push(m.text());});
  await page.route(/^https?:/, r => {record.external_requests.push(r.request().url());return r.abort();});
  for (const width of [1440,900,390]) {
   await page.setViewportSize({width,height:1000});
   await page.goto(pathToFileURL(path.join(directory,artifactFile(path.resolve(run),'typora','examples.html'))).href);
   const check = await page.evaluate(() => {
    const table=document.querySelector('#alignment'), cells=[...table.querySelectorAll('tbody tr:first-child td')];
    const style=getComputedStyle(cells[0]);
    const rgb=s=>s.match(/[\d.]+/g).slice(0,3).map(Number);
    const lum=c=>c.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((n,v,i)=>n+v*[.2126,.7152,.0722][i],0);
    const failures=[];
    for(const el of document.querySelectorAll('#write *')) {
     if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;
     let bg=el;while(bg&&getComputedStyle(bg).backgroundColor==='rgba(0, 0, 0, 0)')bg=bg.parentElement;
     const a=lum(rgb(getComputedStyle(el).color)),b=lum(rgb(getComputedStyle(bg).backgroundColor));
     const ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
     if(ratio<4.5)failures.push({text:el.textContent.slice(0,40),ratio});
    }
    return {width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,
     layout:getComputedStyle(table).display,collapse:getComputedStyle(table).borderCollapse,
     border:style.borderTopWidth,padding:parseFloat(style.paddingTop),align:cells.map(c=>getComputedStyle(c).textAlign),
     row_colors:[...table.querySelectorAll('tbody tr')].map(r=>getComputedStyle(r).backgroundColor),
     header:getComputedStyle(table.querySelector('th')).backgroundColor,
     tall_rows:document.querySelectorAll('#tall tbody tr').length,
     wide_columns:document.querySelectorAll('#wide thead th').length,
     clipped_cells:[...document.querySelectorAll('td,th')].filter(c=>c.scrollWidth>c.clientWidth+1).length,
     image_loaded:document.querySelector('img').naturalWidth>0,contrast_failures:failures};
   });
   record.checks.push(check);
   assert.equal(check.overflow,false);assert.equal(check.clipped_cells,0);
   assert.equal(check.layout,'table');assert.equal(check.collapse,'collapse');
   assert.equal(check.border,'1px');assert.ok(check.padding>0);
   assert.deepEqual(check.align,['left','center','right']);
   assert.notEqual(...check.row_colors);assert.ok(!check.row_colors.includes(check.header));
   assert.equal(check.tall_rows,100);assert.equal(check.wide_columns,12);
   assert.equal(check.image_loaded,true);assert.deepEqual(check.contrast_failures,[]);
   await page.screenshot({path:path.join(directory,`browser-${width}.png`),fullPage:false});
  }
  assert.deepEqual(record.errors,[]);assert.deepEqual(record.external_requests,[]);
  record.passed=true;
 } finally {
  fs.writeFileSync(path.join(directory,'browser-validation.json'),JSON.stringify(record,null,2)+'\n');
  await browser.close();
 }
})().catch(e=>{console.error(e);process.exitCode=1});
