// "نارنجی" mascot — vector green bitter orange with expressive face. narenjiSVG(expr, opts) -> SVG string
(function () {
  const INK = '#1f3410';
  const E = {
    neutral:  { brows: [[-4, 0], [4, 0]],   eyes: 'open', look: [0, 2],  mouth: 'smile', arms: 'down' },
    happy:    { brows: [[-8, -6], [8, -6]], eyes: 'happy', look: [0, 0], mouth: 'grin', arms: 'up' },
    surprised:{ brows: [[-4, -16], [4, -16]], eyes: 'wide', look: [0, 0], mouth: 'o', arms: 'side' },
    sad:      { brows: [[14, -4], [-14, -4]], eyes: 'open', look: [0, 8], mouth: 'frown', arms: 'down', tear: true },
    angry:    { brows: [[-14, 6], [14, 6]], eyes: 'open', look: [0, 0], mouth: 'grit', arms: 'fists' },
    wink:     { brows: [[-4, -4], [6, -10]], eyes: 'wink', look: [4, 0], mouth: 'smirk', arms: 'thumb' },
  };
  function brow(cx, tilt, lift) { // tilt: + raises inner end
    const y = 186 + lift, dx = 26;
    return `<path d="M${cx - dx},${y + (cx < 200 ? 0 : -tilt)} Q${cx},${y - 12 - Math.abs(tilt) * .3} ${cx + dx},${y + (cx < 200 ? -tilt : 0)}" stroke="${INK}" stroke-width="10" stroke-linecap="round" fill="none"/>`;
  }
  function eye(cx, kind, look, blink) {
    const cy = 236;
    if (kind === 'happy' || (kind === 'wink' && cx > 200)) return `<path d="M${cx - 26},${cy + 6} Q${cx},${cy - 22} ${cx + 26},${cy + 6}" stroke="${INK}" stroke-width="9" stroke-linecap="round" fill="none"/>`;
    const ry = (kind === 'wide' ? 42 : 35) * (1 - blink), rx = kind === 'wide' ? 32 : 29;
    if (ry < 4) return `<path d="M${cx - 26},${cy} L${cx + 26},${cy}" stroke="${INK}" stroke-width="8" stroke-linecap="round"/>`;
    const pr = kind === 'wide' ? 12 : 16;
    return `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#fff" stroke="${INK}" stroke-width="5"/>
      <clipPath id="c${cx}"><ellipse cx="${cx}" cy="${cy}" rx="${rx - 2}" ry="${ry - 2}"/></clipPath>
      <g clip-path="url(#c${cx})"><circle cx="${cx + look[0]}" cy="${cy + look[1] + 4}" r="${pr}" fill="${INK}"/>
      <circle cx="${cx + look[0] + 6}" cy="${cy + look[1] - 3}" r="${pr * .35}" fill="#fff"/></g>`;
  }
  function mouth(kind, talk) {
    const o = talk || 0;
    switch (kind) {
      case 'grin': return `<path d="M158,288 Q200,${336 + o * 10} 242,288 Z" fill="#7a1f12" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/><path d="M178,${310 + o * 4} Q200,${326 + o * 8} 222,${310 + o * 4} Q200,${318} 178,${310 + o * 4}" fill="#ff7a6b"/>`;
      case 'o': return `<ellipse cx="200" cy="304" rx="16" ry="${22 + o * 6}" fill="#7a1f12" stroke="${INK}" stroke-width="6"/>`;
      case 'frown': return `<path d="M170,312 Q200,290 230,312" stroke="${INK}" stroke-width="9" stroke-linecap="round" fill="none"/>`;
      case 'grit': return `<rect x="168" y="292" width="64" height="24" rx="10" fill="#fff" stroke="${INK}" stroke-width="6"/><path d="M184,292 V316 M200,292 V316 M216,292 V316" stroke="${INK}" stroke-width="4"/>`;
      case 'smirk': return `<path d="M170,300 Q205,318 236,288" stroke="${INK}" stroke-width="9" stroke-linecap="round" fill="none"/>`;
      default: return o > .1 ? `<path d="M170,292 Q200,${312 + o * 18} 230,292 Z" fill="#7a1f12" stroke="${INK}" stroke-width="6" stroke-linejoin="round"/>`
                               : `<path d="M168,294 Q200,322 232,294" stroke="${INK}" stroke-width="9" stroke-linecap="round" fill="none"/>`;
    }
  }
  function arms(kind) {
    const a = { down: [[60, 300, 30, 350], [340, 300, 370, 350]], up: [[62, 270, 22, 200], [338, 270, 378, 200]],
      side: [[60, 280, 10, 280], [340, 280, 390, 280]], fists: [[62, 300, 40, 330], [338, 300, 360, 330]],
      thumb: [[60, 300, 30, 350], [340, 290, 380, 250]] }[kind];
    return a.map(([x1, y1, x2, y2]) => `<path d="M${x1},${y1} Q${(x1 + x2) / 2 + (x2 < 200 ? -8 : 8)},${(y1 + y2) / 2 - 10} ${x2},${y2}" stroke="#2f6514" stroke-width="10" stroke-linecap="round" fill="none"/><circle cx="${x2}" cy="${y2}" r="14" fill="#a3cd39" stroke="#2f6514" stroke-width="5"/>`).join('') +
      (kind === 'thumb' ? `<path d="M380,250 v-20" stroke="#2f6514" stroke-width="9" stroke-linecap="round"/>` : '');
  }
  window.narenjiSVG = function (expr, o = {}) {
    const e = E[expr] || E.neutral, blink = o.blink || 0, talk = o.talk || 0, sq = o.squash || 0;
    let dots = ''; let s = 9;
    for (let i = 0; i < 70; i++) { s = (s * 9301 + 49297) % 233280; const a = s / 233280 * 6.283; s = (s * 9301 + 49297) % 233280; const r = Math.sqrt(s / 233280) * 128;
      dots += `<circle cx="${(200 + Math.cos(a) * r).toFixed(1)}" cy="${(255 + Math.sin(a) * r).toFixed(1)}" r="2.2" fill="#2f6514" opacity=".28"/>`; }
    return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 440">
<defs><radialGradient id="body" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#9fd35a"/><stop offset=".55" stop-color="#5c9e2e"/><stop offset="1" stop-color="#2f6514"/></radialGradient>
<radialGradient id="blushY" cx="78%" cy="62%" r="40%"><stop offset="0" stop-color="#e8d24a" stop-opacity=".55"/><stop offset="1" stop-color="#e8d24a" stop-opacity="0"/></radialGradient></defs>
<ellipse cx="200" cy="410" rx="${110 + sq * 20}" ry="14" fill="#000" opacity=".18"/>
<g transform="translate(200 400) scale(${1 + sq * .06} ${1 - sq * .06}) translate(-200 -400)">
${arms(e.arms)}
<ellipse cx="168" cy="396" rx="22" ry="12" fill="#2f6514"/><ellipse cx="232" cy="396" rx="22" ry="12" fill="#2f6514"/>
<circle cx="200" cy="255" r="140" fill="url(#body)" stroke="#24510f" stroke-width="6"/>
<circle cx="200" cy="255" r="137" fill="url(#blushY)"/>${dots}
<ellipse cx="148" cy="170" rx="40" ry="20" fill="#fff" opacity=".22" transform="rotate(-30 148 170)"/>
<path d="M200,118 C198,104 200,96 206,88" stroke="#5a3a1a" stroke-width="9" stroke-linecap="round" fill="none"/>
<path d="M204,96 C170,60 130,70 112,92 C140,108 178,110 204,96 Z" fill="#6ea240" stroke="#2f6514" stroke-width="4"/>
<path d="M206,94 C232,60 268,64 284,82 C262,100 230,104 206,94 Z" fill="#a3cd39" stroke="#2f6514" stroke-width="4"/>
<ellipse cx="128" cy="290" rx="20" ry="12" fill="#ff8a6a" opacity=".45"/><ellipse cx="272" cy="290" rx="20" ry="12" fill="#ff8a6a" opacity=".45"/>
${brow(150, e.brows[0][0], e.brows[0][1])}${brow(250, e.brows[1][0], e.brows[1][1])}
${eye(150, e.eyes, e.look, blink)}${eye(250, e.eyes, e.look, blink)}
${e.tear ? '<path d="M128,262 q-10,22 0,30 q10,-8 0,-30 Z" fill="#7cc8ff" stroke="#3b8fd1" stroke-width="3"/>' : ''}
${mouth(e.mouth, talk)}
</g></svg>`;
  };
})();
