// Browser rendering only; no theme installation or native editor automation.
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const [runPath, playwrightPath, executablePath] = process.argv.slice(2);
if (!runPath || !playwrightPath) throw new Error('Usage: node render_visual_previews.cjs RUN PLAYWRIGHT_MODULE');
const {chromium} = require(playwrightPath);
(async () => {
  const root = path.resolve(runPath);
  const browser = await chromium.launch({headless:true, ...(executablePath ? {executablePath} : {})});
  const page = await browser.newPage({viewport:{width:1000, height:580}, deviceScaleFactor:1});
  const evidence = {renderer:'Chromium headless', checks:[], native_editor_acceptance:'pending'};
  try {
    for (const target of ['svg','syntax_highlighting','data_visualization']) {
      const tokens = JSON.parse(fs.readFileSync(path.join(root,target,'tokens.json'),'utf8'));
      for (const example of tokens.examples) {
        const file = path.join(root,target,example);
        if (example.endsWith('.svg')) {
          const svg=fs.readFileSync(file,'utf8').replace(/<\?xml[^>]*\?>/, '');
          await page.setContent('<!doctype html><html><meta charset="utf-8"><body style="margin:0">'+svg+'</body></html>');
        } else await page.goto(pathToFileURL(file).href);
        await page.evaluate(() => document.fonts.ready);
        await page.evaluate(() => window.scrollTo(0,0));
        const check = await page.evaluate(() => ({
          title:document.title,
          horizontal_overflow:document.documentElement.scrollWidth > innerWidth,
          external_media:[...document.querySelectorAll('[src]')].some(n=>/^https?:/.test(n.getAttribute('src'))),
          svg_text:[...document.querySelectorAll('svg text')].map(n=>{
            const b=n.getBBox(); return {text:n.textContent, inside:b.x>=0 && b.y>=0 && b.x+b.width<=960 && b.y+b.height<=540};
          }),
          keyword_color:getComputedStyle(document.querySelector('.token.keyword') || document.documentElement).color,
        }));
        if (check.horizontal_overflow || check.external_media || check.svg_text.some(t=>!t.inside))
          throw new Error('Visual bounds/media check failed: '+example);
        if (target==='syntax_highlighting') {
          const rgb=tokens.tokens.keyword.rgb;
          if (check.keyword_color !== `rgb(${rgb.join(', ')})`) throw new Error('Prism computed color mismatch');
        }
        const png=example.replace(/\.(svg|html)$/,'.png');
        await page.screenshot({path:path.join(root,target,png),fullPage:false,timeout:10000});
        evidence.checks.push({target,example,preview:png,...check});
      }
    }
    fs.writeFileSync(path.join(root,'browser-preview-evidence.json'),JSON.stringify(evidence,null,2)+'\n');
    console.log(`Rendered and checked ${evidence.checks.length} examples.`);
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
