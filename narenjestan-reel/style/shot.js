const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('ERR', e.message));
  await p.goto('file://' + path.join(__dirname, 'frames.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  for (const n of [1, 2, 3]) { await p.evaluate(n => window.show(n), n); await p.waitForTimeout(150); await p.screenshot({ path: path.join(__dirname, `frame${n}.png`) }); }
  await b.close();
})();
