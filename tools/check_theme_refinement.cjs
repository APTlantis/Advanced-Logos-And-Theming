// Offline authored-specimen QA plus the installed KMind validator (no app writes).
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const vm = require('node:vm'), crypto = require('node:crypto');
const [pilot, playwright, executablePath, plugin, evidence, nativeStylesheet] = process.argv.slice(2);
const root = path.resolve(pilot), output = path.resolve(evidence);
const {chromium} = require(playwright);
const read = file => JSON.parse(fs.readFileSync(file, 'utf8'));
function artifact(run, target, logical) {
  const metadata = read(path.join(run, 'run.json'));
  const manifest = read(path.join(run, metadata.artifact_manifests[target]));
  return path.join(run, target, manifest.files.find(r => r.logical_name === logical).file);
}
function hostValidator(source) {
  // Exact contiguous functions from the identified installed version, with its
  // exact color and route validators. Nothing from the UI bundle is executed.
  const functions = source.slice(source.indexOf('function WYe('), source.indexOf('function UYe('));
  const colors = source.slice(source.indexOf('function xw('), source.indexOf('function lQ('));
  const routes = source.slice(source.indexOf('const FYe=new Set('), source.indexOf('function k3('));
  assert(functions.startsWith('function WYe(') && functions.includes('Theme variant is required.'));
  const sandbox = {};
  vm.runInNewContext(functions + colors + routes + ';validate=(theme)=>{const issues=[];WYe(theme,"theme",issues);return issues}', sandbox, {timeout:1000});
  return sandbox.validate;
}
(async () => {
  fs.mkdirSync(output, {recursive:true});
  const pluginSource = fs.readFileSync(path.join(plugin, 'index.js'), 'utf8');
  const validate = hostValidator(pluginSource);
  const browser = await chromium.launch({headless:true, executablePath});
  const record = {browser:browser.version(), plugin:read(path.join(plugin,'plugin.json')).version,
    plugin_index_sha256:crypto.createHash('sha256').update(pluginSource).digest('hex'),
    themes:[], external_requests:[], errors:[], native_application_acceptance:'pending'};
  try {
    const page = await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
    page.on('pageerror', error => record.errors.push(String(error)));
    await page.route('**/*', route => {
      if (route.request().url().startsWith('data:')) return route.continue();
      record.external_requests.push(route.request().url()); return route.abort();
    });
    for (const entry of read(path.join(root,'pilot.json'))) {
      const run = path.join(root,entry.theme), tokens = read(artifact(run,'siyuan','tokens.json'));
      const packageValue = read(artifact(run,'kmindz','KMINDS.json'));
      assert.equal(validate(packageValue.theme).length,0,'Host validator accepts package theme');
      const broken = structuredClone(packageValue.theme); delete broken.variants.light;
      assert(validate(broken).some(issue => issue.path === 'theme.variants.light' && issue.code === 'invalid_theme'));
      const result = {theme:entry.theme, host_theme_validator:'passed', previous_single_variant:'rejected', viewports:[]};
      for (const width of [1440,900,390]) {
        await page.setViewportSize({width,height:1000});
        await page.setContent(fs.readFileSync(artifact(run,'siyuan','examples.html'),'utf8'));
        const checks = await page.evaluate(() => {
          function rgb(value) {return value.match(/[\d.]+/g).slice(0,3).map(Number);}
          function ratio(a,b) {
            const l = c => c.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
            const [low,high]=[l(a),l(b)].sort((x,y)=>x-y);return(high+.05)/(low+.05);
          }
          function background(element) {
            for (let e=element;e;e=e.parentElement) {
              const color=getComputedStyle(e).backgroundColor;
              if (color!=='rgba(0, 0, 0, 0)' && color!=='transparent') return rgb(color);
            } return [255,255,255];
          }
          const text=[];
          for(const element of document.querySelectorAll('.specimen *')) {
            if (element.closest('.specimen-unrelated') || element.id==='explicit-color' || ![...element.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())) continue;
            const style=getComputedStyle(element);if(style.display==='none')continue;
            text.push({selector:element.className||element.tagName,ratio:ratio(rgb(style.color),background(element))});
          }
          return {text,overflow:document.documentElement.scrollWidth>innerWidth,
            heading:getComputedStyle(document.querySelector('.h2')).color,
            link:getComputedStyle(document.querySelector('#reference-link')).color,
            even:getComputedStyle(document.querySelector('tbody tr:nth-child(2)')).backgroundColor,
            odd:getComputedStyle(document.querySelector('tbody tr:nth-child(1)')).backgroundColor,
            alignment:getComputedStyle(document.querySelector('td[style]')).textAlign,
            explicit:getComputedStyle(document.querySelector('#explicit-color')).color,
            syntax:getComputedStyle(document.querySelector('.hljs-title.function_')).color,
            unrelated:getComputedStyle(document.querySelector('#unrelated-heading')).color};
        });
        assert(!checks.overflow, entry.theme+' horizontal overflow '+width);
        assert(checks.text.every(t=>t.ratio>=4.5-1e-6),JSON.stringify(checks.text.filter(t=>t.ratio<4.5)));
        assert.notEqual(checks.heading,checks.link);assert.notEqual(checks.even,checks.odd);
        assert.equal(checks.alignment,'right');assert.equal(checks.explicit,'rgb(170, 187, 204)');
        assert.equal(checks.unrelated,'rgb(1, 2, 3)');
        await page.locator('#tree-hover').hover();
        const hover=await page.locator('#tree-hover').evaluate(e=>getComputedStyle(e).backgroundColor);
        const panel=tokens.tokens.panel.rgb;assert.notEqual(hover,`rgb(${panel.join(', ')})`);
        await page.locator('#focus-input').focus();
        assert.equal(await page.locator('#focus-input').evaluate(e=>getComputedStyle(e).outlineStyle),'solid');
        await page.locator('#reference-link').hover();
        const linkHover=await page.locator('#reference-link').evaluate(e=>getComputedStyle(e).color);
        const expected=tokens.tokens[tokens.siyuan.aliases.hover].rgb;
        assert.equal(linkHover,`rgb(${expected.join(', ')})`);
        await page.mouse.down();
        const pressed=await page.locator('#reference-link').evaluate(e=>getComputedStyle(e).color);
        assert.equal(pressed,`rgb(${tokens.tokens[tokens.siyuan.aliases.pressed].rgb.join(', ')})`);
        await page.mouse.up();
        await page.evaluate(()=>{const range=document.createRange();range.selectNodeContents(document.querySelector('.protyle-wysiwyg p'));getSelection().removeAllRanges();getSelection().addRange(range)});
        const selection=await page.locator('.protyle-wysiwyg p').first().evaluate(e=>getComputedStyle(e,'::selection').backgroundColor);
        assert.equal(selection,`rgb(${tokens.tokens.selection.rgb.join(', ')})`);
        result.viewports.push({width,text_pairs:checks.text.length,minimum_contrast:Math.min(...checks.text.map(t=>t.ratio)),overflow:false,hover_focus_pressed_selection:'passed',alignment_user_color_isolation:'passed'});
        await page.evaluate(()=>getSelection().removeAllRanges());await page.mouse.move(0,0);
        if(width===1440)await page.screenshot({path:path.join(output,entry.theme+'-after.png'),fullPage:true});
      }
      // Removing the theme must leave unrelated controls with identical styles.
      const isolated=await page.evaluate(()=>{
        const selectors=['#unrelated-button','#unrelated-input','#unrelated-heading'];
        const values=()=>selectors.map(s=>{const c=getComputedStyle(document.querySelector(s));return[c.color,c.backgroundColor,c.borderColor]});
        const before=values();document.querySelector('#theme').remove();return JSON.stringify(before)===JSON.stringify(values());
      });assert(isolated,'Unrelated plugin controls changed');
      await page.setViewportSize({width:1440,height:1000});
      await page.setContent(fs.readFileSync(path.join(root,entry.theme+'-before.html'),'utf8'));
      await page.screenshot({path:path.join(output,entry.theme+'-before.png'),fullPage:true});
      record.themes.push(result);
      if (nativeStylesheet) {
        const nativeCss=fs.readFileSync(nativeStylesheet,'utf8');
        const specimen=fs.readFileSync(artifact(run,'siyuan','examples.html'),'utf8');
        await page.setContent(specimen.replace('<style>','<style>'+nativeCss+'</style><style>'));
        // Compose the generated CSS with the real host stylesheet; fixture
        // geometry remains authored. This still does not exercise the app.
        const colors=await page.evaluate(()=>{
          const style=s=>getComputedStyle(document.querySelector(s));
          return {heading:style('.h2').color,link:style('#reference-link').color,
            selected:style('#tree-selected .b3-list-item__toggle').color,
            even:style('tbody tr:nth-child(2)').backgroundColor,
            syntax:style('.hljs-title.function_').color,
            font:style('.protyle-wysiwyg').fontFamily,
            explicit:style('#explicit-color').color};
        });
        const rgb=key=>`rgb(${tokens.tokens[key].rgb.join(', ')})`;
        assert.equal(colors.heading,rgb('secondary'));assert.equal(colors.link,rgb('primary'));
        assert.equal(colors.selected,rgb('selection_text'));assert.equal(colors.even,rgb('panel'));
        assert.equal(colors.syntax,rgb('function_on_panel'));assert.equal(colors.explicit,'rgb(170, 187, 204)');
        result.installed_stylesheet_composition={passed:true,sha256:crypto.createHash('sha256').update(nativeCss).digest('hex'),computed:colors};
      }
    }
    assert.deepEqual(record.external_requests,[]);assert.deepEqual(record.errors,[]);
    fs.writeFileSync(path.join(output,'browser.json'),JSON.stringify(record,null,2)+'\n');
    console.log(JSON.stringify({themes:record.themes.length,viewports:9,host_validator:'passed',external_requests:0,errors:0}));
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
