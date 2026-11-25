# Rewires index.html timings to the VO chunk times in chunks.json (writes vo.js).
import json, re
ch = json.load(open('chunks.json'))
open('vo.js', 'w').write('window.VO=' + json.dumps(ch, ensure_ascii=False) + ';')
p = 'index.html'; s = open(p).read()
if 'src="vo.js"' not in s:
    s = s.replace('<script src="../logo.js"></script>', '<script src="../logo.js"></script><script src="vo.js"></script>')
s = re.sub(r"cap\((?!c\.s)[^;]*?'\);", "", s)
rep = [
("const CAPS=[];const cap=(t0,t1,html)=>CAPS.push([t0,t1,html]);",
 """const CAPS=[];const cap=(t0,t1,html)=>CAPS.push([t0,t1,html]);
const V={};VO.forEach(c=>{V[c.seg]=c.s;V[c.seg+'_e']=c.e;});
const KW=['اورنج','پرتقال','هند','نارانگا','ایران','نارنگ','نارنج','اسپانیا','نارانخا','نورانژ','اورانژ','نون','گیلان','پرتغالی‌ها','بفرست'];
VO.forEach((c,i)=>{if(c.seg==='hook')return;const nx=VO[i+1];let h=c.text;KW.forEach(k=>{h=h.split(k).join('<b>'+k+'</b>')});cap(c.s-.05,nx?Math.min(nx.s-.05,c.e+.6):c.e+1.2,h);});"""),
("},4.1);", "},V.india-.35);"),
("const T={map:4.4,s1:9.6,s2:14.6,s3:19.8,end:25.2};", "const T={map:V.india,s1:V.iran,s2:V.arab,s3:V.spain,end:V.fr1-.05};"),
("tl.to('#bgPaper',{opacity:1,duration:.35},4.2);show('#mapL',4.3);sfx('whoosh',4.2,.7);", "tl.to('#bgPaper',{opacity:1,duration:.35},T.map-.25);show('#mapL',T.map-.15);sfx('whoosh',T.map-.3,.7);"),
("{scale:1,filter:'blur(0px)',duration:.6},4.3);", "{scale:1,filter:'blur(0px)',duration:.6},T.map-.15);"),
("tl.set('#cam',cam(0,1.9),4.3);", "tl.set('#cam',cam(0,1.9),T.map-.15);"),
("stopOn(0,T.map+.3);", "stopOn(0,T.map+.15);"),
("drawRoute(0,T.s1-.4,1.4);stopOn(1,T.s1+.9);", "drawRoute(0,T.s1-.4,1.2);stopOn(1,T.s1+.7);"),
("drawRoute(1,T.s2-.4,1.0);stopOn(2,T.s2+.5);", "drawRoute(1,T.s2-.4,.9);stopOn(2,T.s2+.4);"),
("drawRoute(2,T.s3-.4,1.6);stopOn(3,T.s3+1.1);", "drawRoute(2,T.s3-.4,1.4);stopOn(3,T.s3+.9);"),
("const F=25.2;", "const F=V.fr1,F2=V.fr2;"),
("ease:'back.out(3)'},F+2.0);sfx('boing',F+2.0,.7);", "ease:'back.out(3)'},F2);sfx('boing',F2,.7);"),
("tl.to('#frh1',{autoAlpha:0,duration:.2},F+2.0);", "tl.to('#frh1',{autoAlpha:0,duration:.2},F2);"),
("ease:'back.out(2.4)'},F+2.1);", "ease:'back.out(2.4)'},F2+.1);"),
("ease:'power2.out'},F+2.7);tl.to('#nchar',{autoAlpha:0,duration:.5},F+3.4);sfx('swoosh_up',F+2.7,.8);", "ease:'power2.out'},F2+1.3);tl.to('#nchar',{autoAlpha:0,duration:.5},F2+2.0);sfx('swoosh_up',F2+1.3,.8);"),
("ease:'back.out(1.8)'},F+4.2);sfx('ding',F+4.3,.8);", "ease:'back.out(1.8)'},V.fr3-.1);sfx('ding',V.fr3,.8);"),
("ease:'power2.in'},F+7.0);", "ease:'power2.in'},V.en-.25);"),
("const E=32.4;", "const E=V.en,ES=V.en2+1.6;"),
("ease:'power4.in'},E+1.6);sfx('stamp',E+1.85,1);", "ease:'power4.in'},ES);sfx('stamp',ES+.25,1);"),
("immediateRender:false},E+1.9);tl.set('#stage',{x:0,y:0},E+2.2);", "immediateRender:false},ES+.3);tl.set('#stage',{x:0,y:0},ES+.6);"),
("{scale:1.25,duration:4.5,ease:'none'},E+.5);", "{scale:1.25,duration:V.tw0-E,ease:'none'},E+.5);"),
("ease:'power2.in'},E+4.6);", "ease:'power2.in'},V.tw0-.25);"),
("const W2=37.2;", "const W2=V.tw0;"),
("{autoAlpha:1,y:0,duration:.4},W2+1.4);tl.fromTo('#arr',{autoAlpha:0},{autoAlpha:1,duration:.3},W2+1.7);sfx('pop',W2+1.4,.7);",
 "{autoAlpha:1,y:0,duration:.4},V.tw1+1.0);tl.fromTo('#arr',{autoAlpha:0},{autoAlpha:1,duration:.3},V.tw1+1.3);sfx('pop',V.tw1+1.0,.7);"),
("yoyo:true,repeat:1},W2+3.2);tl.to('#m1',{autoAlpha:0,duration:.15},W2+3.6);", "yoyo:true,repeat:1},V.tw2+.4);tl.to('#m1',{autoAlpha:0,duration:.15},V.tw2+.9);"),
("ease:'back.out(2.5)'},W2+3.6);flash(W2+3.6,.35);sfx('chime',W2+3.6,.8);", "ease:'back.out(2.5)'},V.tw2+.9);flash(V.tw2+.9,.35);sfx('chime',V.tw2+.9,.8);"),
("tl.to('#arr',{autoAlpha:0,duration:.2},W2+3.5);", "tl.to('#arr',{autoAlpha:0,duration:.2},V.tw2+.8);"),
("{x:1380,duration:6.2,ease:'none'},W2+.2);", "{x:1380,duration:V.cta-W2,ease:'none'},W2+.2);"),
("tl.to('#tw .h,#tw .sea,#m2',{autoAlpha:0,duration:.25},W2+6.9);", "tl.to('#tw .h,#tw .sea,#m2',{autoAlpha:0,duration:.25},V.cta-.3);"),
("const C=44.2,END=51.5;", "const C=V.cta,END=+(V.cta2_e+1.3).toFixed(2);"),
("},C+2.0);sfx('pop',C+2.0,.8);", "},V.cta2);sfx('pop',V.cta2,.8);"),
("},C+2.8);sfx('pop',C+2.8,.8);", "},V.cta2+1.4);sfx('pop',V.cta2+1.4,.8);"),
("{autoAlpha:1,y:0,duration:.4},C+3.4);sfx('chime',C+3.4,.6);", "{autoAlpha:1,y:0,duration:.4},C+1.6);sfx('chime',C+1.6,.6);"),
("yoyo:true,repeat:5,ease:'sine.inOut'},C+3.8);", "yoyo:true,repeat:3,ease:'sine.inOut'},V.cta2+.6);"),
]
for a, b in rep:
    if a not in s:
        raise SystemExit('missing: ' + a[:80])
    s = s.replace(a, b)
open(p, 'w').write(s)
print('ok; literal caps left:', len(re.findall(r"cap\((?!c\.s)", s)))
