// Frame-accurate renderer: node render.js <outDir> <fps> <dpr> <workers> [t0] [t1] [--times=a,b,c]
const { chromium } = require('playwright');
const fs = require('fs'); const path = require('path');
const [,, outDir, fpsA, dprA, wA, t0A, t1A] = process.argv;
const fps = +fpsA || 30, dpr = +dprA || 2, workers = +wA || 3;
const timesArg = process.argv.find(a => a.startsWith('--times='));
const url = 'file://' + path.join(__dirname, 'index.html');
(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  const probe = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await probe.goto(url); await probe.evaluate(() => window.ready);
  const dur = await probe.evaluate(() => window.DURATION);
  fs.writeFileSync(path.join(outDir, 'sfx.json'), JSON.stringify(await probe.evaluate(() => window.SFX), null, 0));
  await probe.close();
  let jobs;
  const framesArg = process.argv.find(a => a.startsWith('--frames='));
  if (framesArg) jobs = framesArg.slice(9).split(',').map(n => ({ t: +n / fps, f: path.join(outDir, String(+n).padStart(5, '0') + '.jpg') }));
  else if (timesArg) jobs = timesArg.slice(8).split(',').map((t, i) => ({ t: +t, f: path.join(outDir, `t_${(+t).toFixed(2)}.jpg`) }));
  else {
    const a = t0A ? +t0A : 0, b = t1A ? +t1A : dur;
    const n0 = Math.round(a * fps), n1 = Math.round(b * fps);
    jobs = []; for (let n = n0; n < n1; n++) jobs.push({ t: n / fps, f: path.join(outDir, String(n).padStart(5, '0') + '.jpg') });
  }
  console.log('duration', dur, 'frames', jobs.length);
  const t0 = Date.now(); let done = 0;
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: dpr });
    await page.goto(url); await page.evaluate(() => window.ready);
    for (let i = w; i < jobs.length; i += workers) {
      await page.evaluate(t => window.renderAt(t), jobs[i].t);
      await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))));
      await page.screenshot({ path: jobs[i].f, type: 'jpeg', quality: 93 });
      if (++done % 60 === 0) console.log(done, '/', jobs.length, ((Date.now() - t0) / 1000).toFixed(0) + 's');
    }
    await page.close();
  }));
  await browser.close();
  console.log('done', ((Date.now() - t0) / 1000).toFixed(1) + 's');
})();
