const { chromium } = require('playwright'); const path = require('path'); const fs = require('fs');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1800, height: 1260 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'sheet.html')); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.screenshot({ path: path.join(__dirname, 'narenji_expressions.png') });
  const q = await b.newPage({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 });
  await q.goto('file://' + path.join(__dirname, 'anim.html')); await q.evaluate(() => window.ready); await q.waitForTimeout(300);
  const out = path.join(__dirname, 'frames'); fs.mkdirSync(out, { recursive: true });
  for (let i = 0; i < 180; i++) { await q.evaluate(t => window.renderAt(t), i / 30); await q.screenshot({ path: path.join(out, String(i).padStart(4, '0') + '.png') }); }
  await b.close();
})();
