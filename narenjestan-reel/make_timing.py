# Builds timing.js from chunks.json (VO chunks with start/end after editing).
# Words inside a chunk get times proportional to their length.
import json, sys

chunks = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'chunks.json'))
tail = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
cues, words = {}, []
for c in chunks:
    cues.setdefault(c['seg'], c['s'])
    ws = c['text'].split()
    L = [max(2, len(w.replace('‌', '').strip('.،؛!؟:…'))) for w in ws]
    tot = sum(L); t = c['s']; span = c['e'] - c['s']
    for w, l in zip(ws, L):
        d = span * l / tot
        words.append({'w': w, 's': round(t, 3), 'e': round(t + d, 3), 'seg': c['seg']})
        t += d
cues['hook'] = 0.0
cues['voEnd'] = chunks[-1]['e']
cues['end'] = round(chunks[-1]['e'] + tail, 3)
open('timing.js', 'w').write('window.CUES=' + json.dumps(cues) + ';\nwindow.WORDS=' + json.dumps(words, ensure_ascii=False) + ';\n')
print(json.dumps(cues))
