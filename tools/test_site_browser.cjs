/* Optional end-to-end check against a local HTTP server.
   See docs/site-playground-verification.md for prerequisites and commands. */
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH || '/usr/bin/chromium',headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 const root=(process.env.SITE_URL || 'http://127.0.0.1:8800').replace(/\/$/, '');
 const preview=process.env.ASMA_PREVIEW_DIR || require('node:path').join(require('node:os').tmpdir(),'asma-site-preview');
 const page=await browser.newPage({viewport:{width:1440,height:1100},reducedMotion:'reduce'});
 const errors=[],badRequests=[];
 page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(!r.url().startsWith(root))badRequests.push(r.url())});
 await page.goto(root+'/?theme=light&motion=off');await page.waitForSelector('[data-molecule-ready="true"]');
 assert.equal(await page.locator('[data-lab-controls]').isDisabled(),false);
 assert.equal(await page.locator('[data-lab-first-total]').innerText(),'1.90');
 assert.equal(await page.locator('[data-lab-second-total]').innerText(),'10.00');
 await page.locator('input[value="proportional"]').check();
 assert.equal(await page.locator('[data-lab-ratio]').innerText(),'1.00×');
 await page.locator('[data-lab-survival]').fill('100');await page.locator('[data-lab-survival]').dispatchEvent('change');
 assert.equal(await page.locator('[data-lab-first-total]').innerText(),'10.00');
 await page.locator('[data-lab-reset]').click();assert.equal(await page.locator('[data-lab-ratio]').innerText(),'5.26×');
 await page.locator('[data-molecule-select]').selectOption('dna');await page.waitForFunction(()=>document.querySelector('[data-molecule-name]').textContent.includes('DNA'));
 await page.locator('[data-molecule-display]').selectOption('atoms');assert.match(await page.locator('[data-molecule-legend]').innerText(),/carbon/);
 await page.locator('[data-theme-toggle]').click();assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
 for(const w of [1440,768,390,320]){await page.setViewportSize({width:w,height:1000});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true)}
 await page.locator('.menu > summary').click();await page.locator('.menu-panel a[href="#vision"]').click();assert.equal(await page.locator('.menu').getAttribute('open'),null);
 // A failed replacement retains an accurately named previously loaded model.
 await page.route('**/models/insulin.json',r=>r.abort());await page.locator('[data-molecule-select]').selectOption('insulin');
 await page.waitForFunction(()=>document.querySelector('[data-molecule-status]').textContent.includes('could not load'));
 assert.equal(await page.locator('[data-molecule-select]').inputValue(),'dna');
 assert.match(await page.locator('[data-molecule-source]').getAttribute('href'),/1BNA/);
 assert.equal(await page.locator('[data-molecule-fallback]').isVisible(),true);
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});const staticPage=await nojs.newPage();await staticPage.goto(root+'/');
 assert.equal(await staticPage.locator('[data-molecule-fallback] img').isVisible(),true);
 assert.equal(await staticPage.locator('[data-molecule-canvas]').getAttribute('tabindex'),'-1');
 assert.equal(await staticPage.locator('[data-molecule-canvas]').getAttribute('aria-hidden'),'true');
 assert.equal(await staticPage.locator('[data-lab-second-total]').innerText(),'10.00');
 // Actual GitHub Pages project prefix, including nested 404 base links, entirely intercepted locally.
 const pages=await browser.newContext();const pref=await pages.newPage();const remote='https://foundation-0.github.io';
 await pref.route(remote+'/**',async route=>{const u=new URL(route.request().url());let rel=u.pathname.replace(/^\/project-asma\/?/,'/');if(rel==='/missing/deep')rel='/404.html';const response=await route.fetch({url:root+rel+u.search});await route.fulfill({response})});
 await pref.goto(remote+'/project-asma/');await pref.waitForSelector('[data-molecule-ready="true"]');
 assert.equal(await pref.locator('[data-lab-first-total]').innerText(),'1.90');
 await pref.goto(remote+'/project-asma/missing/deep');assert.equal(await pref.locator('.brand').evaluate(el=>el.href),remote+'/project-asma/');
 assert.equal(await pref.locator('.skip').evaluate(el=>el.href),remote+'/project-asma/missing/deep#main');
 assert.deepEqual(errors,[]);assert.deepEqual(badRequests,[]);
 fs.mkdirSync(preview,{recursive:true});
 const shots=await browser.newPage({viewport:{width:1440,height:1100},reducedMotion:'reduce'});await shots.goto(root+'/?theme=light&motion=off');await shots.waitForSelector('[data-molecule-ready="true"]');
 await shots.screenshot({path:preview+'/desktop.png'});
 await shots.locator('#vision').screenshot({path:preview+'/vision.png'});
 await shots.locator('#playground').screenshot({path:preview+'/experiment.png'});
 await shots.setViewportSize({width:390,height:844});await shots.goto(root+'/?theme=dark&motion=off');await shots.waitForSelector('[data-molecule-ready="true"]');await shots.screenshot({path:preview+'/mobile.png',fullPage:true});
 await browser.close();console.log('PASS actual site: lab input/reset; both models; replacement failure; themes; 320/390/768/1440 reflow; compact navigation; no-JS fallback; GitHub Pages prefix and nested404; same-origin requests; no page errors.');
})().catch(e=>{console.error(e);process.exit(1)});
