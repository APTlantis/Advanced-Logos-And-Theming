// Browser rendering checks for an explicitly produced finishing receipt; no source mutations.
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const [directory, playwright, executablePath, destination] = process.argv.slice(2);
const root = path.resolve(directory), evidence = path.resolve(destination || path.join(root, '..', 'browser'));
const {chromium} = require(playwright);
(async () => {
  fs.mkdirSync(evidence, {recursive: true});
  const receipt = JSON.parse(fs.readFileSync(path.join(root, 'finish-receipt.json'), 'utf8'));
  const browser = await chromium.launch({headless: true, executablePath});
  const record = {browser: browser.version(), assets: [], external_requests: [], errors: []};
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1000}, deviceScaleFactor: 1});
    page.on('pageerror', e => record.errors.push(String(e)));
    await page.route('**/*', route => {
      if (route.request().url().startsWith('data:')) return route.continue();
      record.external_requests.push(route.request().url());
      return route.abort();
    });
    const gallery = [];
    for (const asset of receipt.assets) {
      const svg = fs.readFileSync(path.join(root, asset.file), 'utf8');
      const before = svg.replace(/\n  <metadata id="sesm">[\s\S]*?<\/metadata>/, '');
      assert.notEqual(before, svg, 'Expected exactly one SESM block');
      const pixels = await page.evaluate(async ({before, svg}) => {
        async function render(text) {
          const image = new Image();
          image.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(text)));
          await image.decode();
          const canvas = document.createElement('canvas');
          canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
          const context = canvas.getContext('2d'); context.drawImage(image, 0, 0);
          return {width: canvas.width, height: canvas.height, data: context.getImageData(0, 0, canvas.width, canvas.height).data};
        }
        const a = await render(before), b = await render(svg);
        let differences = 0;
        for (let i = 0; i < a.data.length; i++) if (a.data[i] !== b.data[i]) differences++;
        return {width: b.width, height: b.height, metadata_pixel_differences: differences};
      }, {before, svg});
      assert.equal(pixels.metadata_pixel_differences, 0);
      await page.setContent(svg);
      const geometry = await page.evaluate(() => {
        const root = document.querySelector('svg'), bounds = root.viewBox.baseVal;
        return [...root.querySelectorAll('text')].map(text => {
          const box = text.getBBox();
          return {text: text.textContent, in_bounds: box.x >= 0 && box.y >= 0 && box.x + box.width <= bounds.width + .1 && box.y + box.height <= bounds.height + .1};
        });
      });
      assert.ok(geometry.every(item => item.in_bounds), 'Text escapes SVG bounds: ' + asset.file);
      const images = await page.locator('svg image').evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
      let embedded_png_equal = null;
      if (asset.settings.mode === 'embed') {
        assert.equal(images.length, 1);
        const metadata = JSON.parse(await page.locator('metadata#sesm').textContent());
        const expected = metadata.extra.source_sha256;
        embedded_png_equal = require('node:crypto').createHash('sha256').update(Buffer.from(images[0].split(',')[1], 'base64')).digest('hex') === expected;
        assert.equal(embedded_png_equal, true);
      } else if (asset.settings.mode === 'palette') {
        assert.equal(images.length, 0);
        const metadata = JSON.parse(await page.locator('metadata#sesm').textContent());
        const colors = await page.locator('rect[data-color-id]').evaluateAll(nodes => nodes.map(node => ({id: node.dataset.colorId, hex: node.getAttribute('fill')})));
        assert.deepEqual(colors, metadata.extra.palette.map(row => ({id: row.id, hex: row.hex})));
      }
      let trace_comparison = null, originalImage = '';
      if (asset.settings.mode === 'trace') {
        const metadata = JSON.parse(await page.locator('metadata#sesm').textContent());
        const [source] = Object.entries(receipt.sources).find(([, sha]) => sha === metadata.extra.source_sha256);
        const png = fs.readFileSync(source);
        assert.equal(require('node:crypto').createHash('sha256').update(png).digest('hex'), metadata.extra.source_sha256);
        const pngUrl = 'data:image/png;base64,' + png.toString('base64');
        trace_comparison = await page.evaluate(async ({pngUrl, svg}) => {
          async function render(url) {
            const image = new Image(); image.src = url; await image.decode();
            const canvas = document.createElement('canvas'); canvas.width = image.naturalWidth; canvas.height = image.naturalHeight;
            const context = canvas.getContext('2d'); context.drawImage(image, 0, 0);
            return {width: canvas.width, height: canvas.height, data: context.getImageData(0, 0, canvas.width, canvas.height).data};
          }
          const original = await render(pngUrl), traced = await render('data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg))));
          if (original.width !== traced.width || original.height !== traced.height) throw Error('Trace dimensions changed');
          let difference = 0, changed = 0;
          for (let i = 0; i < original.data.length; i++) { difference += Math.abs(original.data[i] - traced.data[i]); if (original.data[i] !== traced.data[i]) changed++; }
          return {mean_absolute_channel_difference: difference / original.data.length, changed_channel_fraction: changed / original.data.length, note: 'Lossy raster-to-vector comparison; no universal fidelity threshold claimed'};
        }, {pngUrl, svg});
        originalImage = `<div><p>Original PNG</p><img src="${pngUrl}" alt="original PNG"></div>`;
      }
      record.assets.push({file: asset.file, ...pixels, embedded_png_equal, labels_checked: geometry.length, trace_comparison});
      gallery.push(`<section><h2>${asset.id} / ${asset.settings.mode}</h2><p>${asset.validation.profile}</p><div class="comparison">${originalImage}<div><p>Finished SVG</p><img src="data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}" alt="${asset.id}"></div></div></section>`);
    }
    const html = '<!doctype html><meta charset="utf-8"><title>SVG finishing review</title><style>body{background:#171d24;color:#edf0e7;font:16px system-ui;margin:32px}section{border:1px solid #59636f;padding:20px;margin:24px 0}img{display:block;max-width:100%;max-height:680px}h1,h2{font-weight:500}.comparison{display:flex;gap:24px;align-items:start}.comparison>div{min-width:0;flex:1}</style><h1>Selected SVG finishing review</h1><p>Local browser evidence; native application import remains unperformed.</p>' + gallery.join('');
    fs.writeFileSync(path.join(evidence, 'review.html'), html);
    await page.setContent(html);
    await page.locator('img').evaluateAll(nodes => Promise.all(nodes.map(node => node.decode())));
    await page.screenshot({path: path.join(evidence, 'review.png'), fullPage: true});
    assert.deepEqual(record.errors, []); assert.deepEqual(record.external_requests, []);
    record.passed = true;
    fs.writeFileSync(path.join(evidence, 'browser-validation.json'), JSON.stringify(record, null, 2) + '\n');
    console.log(JSON.stringify(record));
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
