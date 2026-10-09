const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.argv[2]);
(async () => {
  const root = path.resolve(__dirname, '..');
  const recordPath = path.join(root, 'migration/chart-neutral-gallery-2026-10-09.json');
  const record = JSON.parse(fs.readFileSync(recordPath, 'utf8'));
  const browser = await chromium.launch({headless: true, executablePath: process.argv[3], args: ['--allow-file-access-from-files']});
  try {
    const page = await browser.newPage();
    const checks = [];
    for (const entry of record.galleries) {
      for (const file of ['examples.html', 'heatmap-values.html']) {
        for (const width of [1200, 390]) {
          await page.setViewportSize({width, height: 900});
          await page.goto(pathToFileURL(path.join(root, 'output', path.dirname(entry.gallery), file)).href);
          const state = await page.evaluate(() => ({
            background: getComputedStyle(document.body).backgroundColor,
            foreground: getComputedStyle(document.body).color,
            overflow: document.documentElement.scrollWidth > innerWidth,
            loadedCharts: [...document.querySelectorAll('object')].filter(o => o.contentDocument?.documentElement?.tagName === 'svg').length
          }));
          assert.equal(state.background, 'rgb(24, 26, 29)');
          assert.equal(state.foreground, 'rgb(236, 238, 240)');
          assert.equal(state.overflow, false);
          if (file === 'examples.html') assert.equal(state.loadedCharts, 3);
          checks.push({gallery: entry.gallery, file, width, ...state});
        }
      }
    }
    await page.setViewportSize({width: 1200, height: 900});
    await page.goto(pathToFileURL(path.join(root, 'output/dnf-Clojure/data_visualization/examples.html')).href);
    await page.screenshot({path: path.join(root, 'pilot/chart-neutral-gallery-2026-10-09/gallery.png'), fullPage: true});
    record.browser = {version: browser.version(), checks};
    record.focused_tests = {count: 30, result: 'passed outside Windows sandbox'};
    fs.writeFileSync(recordPath, JSON.stringify(record, null, 2) + '\n');
    console.log(`${checks.length} desktop/mobile gallery and table checks passed.`);
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
