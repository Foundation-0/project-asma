/* Browser integration test. Run against a local HTTP server (never file://).
   PLAYWRIGHT_MODULE=/path/to/playwright-core node tools/test_molecular_viewer.cjs
   Optional SITE_URL=http://127.0.0.1:8766 and CHROMIUM_PATH=/usr/bin/chromium. */
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const digest = buffer => createHash('sha256').update(buffer).digest('hex');
const path = require('node:path');
const playwrightModule = process.env.PLAYWRIGHT_MODULE || 'playwright-core';
const { chromium } = require(playwrightModule);
const { PNG } = require(path.join(path.dirname(require.resolve(playwrightModule)), 'lib/utilsBundle'));
const base = process.env.SITE_URL || 'http://127.0.0.1:8766';
const fixture = `<!doctype html><html><head><style>
body{background:#07101a;color:#f5efdf;font:16px system-ui}main{max-width:900px;margin:30px auto}fieldset{min-width:0}
.stage{height:440px;position:relative;background:radial-gradient(ellipse,#142732,#07101a 70%)}
canvas{width:100%;height:100%;display:block;touch-action:none} [hidden]{display:none!important}
</style></head><body><main data-molecule-viewer>
<h1 data-molecule-name>Experimental structures</h1><p data-molecule-description></p>
<select data-molecule-select><option value="insulin">Human insulin</option><option value="dna">DNA</option></select>
<fieldset data-molecule-controls disabled><select data-molecule-display><option value="backbone">Backbone guide</option><option value="atoms">Atoms and bonds</option></select>
${['left','right','up','down','zoom-in','zoom-out','reset','rotate'].map(name=>`<button data-molecule-action="${name}">${name}</button>`).join(' ')}</fieldset>
<div class="stage"><canvas data-molecule-canvas></canvas><div data-molecule-fallback>Experimental structures explained in accessible text.</div></div>
<p data-molecule-status role="status"></p><p data-molecule-count></p><p data-molecule-legend></p><p data-molecule-limits></p><a data-molecule-source>Source</a><p data-molecule-loading>Loading</p>
</main><script type="module" src="/assets/molecular-viewer.js"></script></body></html>`;

(async () => {
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium', headless: true,
    args: ['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1100, height: 1000 } });
  const errors = [], requests = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('request', request => requests.push(request.url()));
  await page.addInitScript(() => {
    window.viewerFrameCount = 0;
    const request = window.requestAnimationFrame;
    window.requestAnimationFrame = callback => request.call(window, time => { window.viewerFrameCount++; callback(time); });
  });
  await page.route('**/viewer-test.html', route => route.fulfill({ contentType: 'text/html', body: fixture }));
  await page.goto(`${base}/viewer-test.html`);
  await page.waitForSelector('[data-molecule-ready="true"]');
  assert.match(await page.locator('[data-molecule-count]').innerText(), /399 atoms/);
  assert.equal(await page.locator('[data-molecule-fallback]').isVisible(), false);
  assert.equal(await page.locator('[data-molecule-canvas]').getAttribute('tabindex'), '0');
  const canvas = page.locator('canvas');
  await canvas.focus();
  await page.keyboard.press('r');
  await page.waitForTimeout(100);
  const originalPixels = PNG.sync.read(await canvas.screenshot({ path: '/tmp/asma-viewer-original.png' }));
  const original = digest(originalPixels.data);
  await canvas.focus(); await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(100);
  assert.notEqual(digest(PNG.sync.read(await canvas.screenshot()).data), original, 'Keyboard rotation changes the frame');
  await page.keyboard.press('r');
  await page.waitForTimeout(100);
  const resetPixels = PNG.sync.read(await canvas.screenshot({ path: '/tmp/asma-viewer-reset.png' }));
  assert.equal(resetPixels.data.length, originalPixels.data.length);
  // GPU/compositor quantisation can differ by one 8-bit code value per channel.
  const maxResetDifference = resetPixels.data.reduce((max, value, index) => Math.max(max, Math.abs(value - originalPixels.data[index])), 0);
  assert.ok(maxResetDifference <= 2, `Reset restores the original frame (max channel error: ${maxResetDifference})`);
  const frames = await page.evaluate(() => window.viewerFrameCount);
  await page.waitForTimeout(250);
  assert.equal(await page.evaluate(() => window.viewerFrameCount), frames, 'Idle viewer does not animate');
  const box = await canvas.boundingBox();
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down(); await page.mouse.move(box.x + box.width / 2 + 70, box.y + box.height / 2 + 20); await page.mouse.up();
  await page.waitForTimeout(100);
  assert.notEqual(digest(PNG.sync.read(await canvas.screenshot()).data), original, 'Pointer drag changes the frame');
  await page.keyboard.press('r');
  await page.keyboard.press('+');
  await page.waitForTimeout(100);
  assert.notEqual(digest(PNG.sync.read(await canvas.screenshot()).data), original, 'Keyboard zoom changes the frame');
  await page.keyboard.press('r');
  await page.locator('[data-molecule-display]').selectOption('atoms');
  assert.match(await page.locator('[data-molecule-legend]').innerText(), /carbon gray/);
  await page.screenshot({ path: '/tmp/asma-insulin-atoms.png' });
  await page.locator('[data-molecule-select]').selectOption('dna');
  await page.waitForFunction(() => document.querySelector('[data-molecule-ready="true"]') && document.querySelector('[data-molecule-count]').textContent.includes('486 atoms'));
  await page.screenshot({ path: '/tmp/asma-dna-atoms.png' });
  assert.match(await canvas.getAttribute('aria-label'), /1BNA/);
  await page.locator('[data-molecule-display]').selectOption('backbone');
  await page.screenshot({ path: '/tmp/asma-dna-backbone.png' });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.locator('[data-molecule-action="rotate"]').click();
  assert.equal(await page.locator('[data-molecule-action="rotate"]').getAttribute('aria-pressed'), 'false');
  assert.match(await page.locator('[data-molecule-status]').innerText(), /reduced motion/);
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(100);
  await page.screenshot({ path: '/tmp/asma-dna-mobile.png' });
  assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), true);
  await canvas.evaluate(node => node.dispatchEvent(new Event('webglcontextlost', { cancelable: true })));
  assert.equal(await page.locator('[data-molecule-fallback]').isVisible(), true);
  assert.equal(await page.locator('[data-molecule-action="left"]').isDisabled(), true);
  assert.deepEqual(errors, []);
  assert.ok(requests.every(url => url.startsWith(base)), 'No external runtime requests');
  const failurePage = await browser.newPage();
  await failurePage.route('**/viewer-test.html', route => route.fulfill({ contentType: 'text/html', body: fixture }));
  await failurePage.route('**/models/insulin.json', route => route.fulfill({ status: 503, body: 'Unavailable' }));
  await failurePage.goto(`${base}/viewer-test.html`);
  await failurePage.waitForFunction(() => document.querySelector('[data-molecule-status]').textContent.includes('could not load'));
  assert.equal(await failurePage.locator('[data-molecule-fallback]').isVisible(), true);
  const disabledPage = await browser.newPage();
  await disabledPage.route('**/viewer-test.html', route => route.fulfill({ contentType: 'text/html', body: fixture }));
  await disabledPage.addInitScript(() => { HTMLCanvasElement.prototype.getContext = () => null; });
  await disabledPage.goto(`${base}/viewer-test.html`);
  await disabledPage.waitForFunction(() => document.querySelector('[data-molecule-status]').textContent.includes('unavailable'));
  assert.equal(await disabledPage.locator('[data-molecule-fallback]').isVisible(), true);
  const noJS = await browser.newContext({ javaScriptEnabled: false });
  const noJSPage = await noJS.newPage();
  await noJSPage.route('**/viewer-test.html', route => route.fulfill({ contentType: 'text/html', body: fixture }));
  await noJSPage.goto(`${base}/viewer-test.html`);
  assert.equal(await noJSPage.locator('[data-molecule-fallback]').isVisible(), true);
  await browser.close();
  console.log('PASS: both coordinate models; representation switch; pointer rotation; keyboard rotation/zoom/reset; no idle animation; reduced motion; mobile sizing; context loss; HTTP failure; no WebGL; no JS; same-origin assets; no page errors.');
})().catch(error => { console.error(error); process.exit(1); });
