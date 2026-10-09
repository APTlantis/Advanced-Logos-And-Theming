// Offline Chromium verification; no installation or native editor automation.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const {pathToFileURL, fileURLToPath} = require('node:url');
const [runPath, playwrightPath, executablePath] = process.argv.slice(2);
if (!runPath || !playwrightPath) throw new Error('Usage: node render_visual_previews.cjs RUN PLAYWRIGHT_MODULE [CHROMIUM_EXECUTABLE]');
const {chromium} = require(playwrightPath);
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
(async () => {
  const root = path.resolve(runPath);
  const browser = await chromium.launch({headless:true, ...(executablePath ? {executablePath} : {})});
  const context = await browser.newContext({viewport:{width:1100, height:750}, deviceScaleFactor:1});
  const requests = [], errors = [];
  await context.route(/^https?:/, route => { requests.push(route.request().url()); return route.abort(); });
  const page = await context.newPage();
  page.on('pageerror', error => errors.push(String(error)));
  page.on('console', message => { if (message.type()==='error') errors.push(message.text()); });
  const evidence = {renderer:'Chromium headless', browser_version:browser.version(), node_version:process.version,
    checks:[], blocked_network_requests:requests, errors, native_editor_acceptance:'pending'};
  try {
    for (const target of ['svg','syntax_highlighting','data_visualization']) {
      const directory = path.join(root,target);
      if (!fs.existsSync(path.join(directory,'tokens.json'))) continue;
      const tokens = JSON.parse(fs.readFileSync(path.join(directory,'tokens.json'),'utf8'));
      for (const example of tokens.examples) {
        await page.setViewportSize({width:1100,height:750});
        const file = path.join(directory,example);
        if (example.endsWith('.svg')) {
          const svg=fs.readFileSync(file,'utf8').replace(/<\?xml[^>]*\?>/, '');
          await page.setContent('<!doctype html><html><meta charset="utf-8"><body style="margin:0">'+svg+'</body></html>');
        } else await page.goto(pathToFileURL(file).href);
        await page.evaluate(() => document.fonts.ready);
        const check = await page.evaluate(() => ({
          title:document.title,
          horizontal_overflow:document.documentElement.scrollWidth > innerWidth,
          external_media:[...document.querySelectorAll('[src]')].some(n=>/^https?:/.test(n.getAttribute('src'))),
          svg_text:[...document.querySelectorAll('svg text')].map(n=>{
            const b=n.getBBox(), view=n.ownerSVGElement.viewBox.baseVal;
            return {text:n.textContent, inside:b.x>=0 && b.y>=0 && b.x+b.width<=view.width && b.y+b.height<=view.height};
          }),
        }));
        assert(!check.horizontal_overflow && !check.external_media && check.svg_text.every(t=>t.inside), example+' bounds/media');
        if (target==='syntax_highlighting') {
          await page.waitForFunction(() => document.querySelector('code .token'));
          const grammar = await page.evaluate(() => {
            const code = document.querySelector('code');
            const language=code.className.replace('language-','');
            const representatives={comment:'comment',keyword:'keyword',string:'string',number:'number',
              function:'function','class-name':'type',property:'constant',tag:'constant',selector:'type',operator:'operator'};
            const colors=[];
            for (const [cls,role] of Object.entries(representatives)) {
              const node=[...code.querySelectorAll('.token.'+cls)].find(n=>n.children.length===0);
              if (node) colors.push({class:cls,role,color:getComputedStyle(node).color});
            }
            return {language,registered:!!Prism.languages[language],tokens:code.querySelectorAll('.token').length,
              source:code.textContent,source_file:code.dataset.source,colors,
              sample_executed:window.sampleExecuted===true, scripts:[...document.scripts].map(s=>s.getAttribute('src'))};
          });
          const raw=fs.readFileSync(path.join(directory,grammar.source_file),'utf8');
          assert.equal(grammar.source,raw.replace(/\r\n/g,'\n'),example+' source preserved');
          assert(grammar.registered && grammar.tokens>0 && !grammar.sample_executed);
          assert(grammar.scripts.every(src=>src && src.startsWith('vendor/prism/')),'Unexpected executable sample script');
          assert(grammar.colors.length>=2,example+' representative tokens');
          for (const color of grammar.colors) {
            assert.equal(color.color,`rgb(${tokens.tokens[color.role].rgb.join(', ')})`,example+' '+color.class);
          }
          check.grammar={...grammar,source:undefined};
          check.source_sha256=hash(path.join(directory,grammar.source_file));
          const navigation=await page.locator('nav a').evaluateAll(nodes=>nodes.map(n=>n.href));
          for (const href of navigation) assert(fs.existsSync(fileURLToPath(href)));
          await page.keyboard.press('Tab');
          assert.equal(await page.evaluate(()=>document.activeElement.textContent),'All languages');
          await page.keyboard.press('Enter');
          await page.waitForURL('**/examples.html');
          assert.equal(await page.locator('.cards a').count(),12);
          await page.goto(pathToFileURL(file).href);
          await page.waitForFunction(() => document.querySelector('code .token'));
          const [download]=await Promise.all([page.waitForEvent('download'),page.locator('a[download]').click()]);
          assert.equal(hash(await download.path()),check.source_sha256);
          check.download_and_navigation='passed';
          await page.screenshot({path:path.join(directory,example.replace('.html','.png')),fullPage:true});
          await page.setViewportSize({width:390,height:844});
          assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),example+' narrow overflow');
          await page.locator('pre').focus();
          assert.equal(await page.evaluate(()=>document.activeElement.tagName),'PRE');
          await page.screenshot({path:path.join(directory,example.replace('.html','-narrow.png')),fullPage:true});
          check.narrow_layout='passed';
        } else {
          const png=example.replace('.svg','.png');
          await page.screenshot({path:path.join(directory,png),clip:{x:0,y:0,width:960,height:540}});
          check.preview=png;
        }
        evidence.checks.push({target,example,...check});
      }
      await page.setViewportSize({width:1100,height:750});
      await page.goto(pathToFileURL(path.join(directory,'examples.html')).href);
      await page.screenshot({path:path.join(directory,'examples.png'),fullPage:true});
      await page.setViewportSize({width:390,height:844});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),target+' index narrow overflow');
      await page.screenshot({path:path.join(directory,'examples-narrow.png'),fullPage:true});
      if (target==='data_visualization') {
        await page.goto(pathToFileURL(path.join(directory,'heatmap-values.html')).href);
        const data=JSON.parse(fs.readFileSync(path.join(directory,'example-data.json'),'utf8'));
        const values=await page.locator('tbody td').allTextContents();
        assert.deepEqual(values.map(Number),data.heatmap.flat());
        evidence.heatmap_table='96 matching values';
      }
      await page.setViewportSize({width:390,height:844});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),target+' index/table narrow overflow');
    }
    const gallery=path.join(root,'visual-examples.html');
    if (fs.existsSync(gallery)) {
      await page.setViewportSize({width:1100,height:750});
      await page.goto(pathToFileURL(gallery).href);
      await page.locator('img').evaluateAll(nodes=>nodes.forEach(n=>n.loading='eager'));
      await page.waitForFunction(()=>[...document.images].every(n=>n.complete && n.naturalWidth>0));
      for (const href of await page.locator('a').evaluateAll(nodes=>nodes.map(n=>n.href)))
        assert(fs.existsSync(fileURLToPath(href)),'Gallery link missing');
      await page.screenshot({path:path.join(root,'visual-examples.png'),fullPage:true});
      await page.setViewportSize({width:390,height:844});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Gallery narrow overflow');
      evidence.review_gallery='Links, images and narrow layout passed';
    }
    assert.deepEqual(errors,[],'Browser errors');
    assert.deepEqual(requests,[],'Examples attempted a network request');
    const plain = await browser.newContext({javaScriptEnabled:false});
    const plainPage = await plain.newPage();
    const markupPage=path.join(root,'syntax_highlighting','syntax-markup.html');
    if (fs.existsSync(markupPage)) {
      await plainPage.goto(pathToFileURL(markupPage).href);
      assert((await plainPage.locator('code').textContent()).includes('<script>'));
      assert.equal(await plainPage.locator('code .token').count(),0);
      evidence.no_javascript_fallback='Readable escaped source';
    }
    await plain.close();
    fs.writeFileSync(path.join(root,'browser-preview-evidence.json'),JSON.stringify(evidence,null,2)+'\n');
    console.log(`Rendered and checked ${evidence.checks.length} examples offline.`);
  } finally { await browser.close(); }
})().catch(e=>{console.error(e);process.exitCode=1;});
