# ریل اینستاگرام نارنجستان — «نارنج سبز؟! کاله یا رسیده؟»

خروجی نهایی در پوشه‌ی `../output` است:
- `narenjestan_reel_4k.mp4` — 2160×3840، 30fps، H.264، صدای AAC 320k، ‏33.5 ثانیه
- `narenjestan_reel_1080p_preview.mp4` — نسخه‌ی سبک برای دیدن روی گوشی

## ساختار
| فایل | کار |
|---|---|
| `index.html` | کل موشن (GSAP + SVG + Canvas)، زمان‌بندی از `timing.js` |
| `vo_edit.py` | برش و فشرده‌کردن صدای گوینده (ElevenLabs، صدای Meisam) و سرعت ۱.۲۴ با rubberband |
| `make_timing.py` | ساخت `timing.js` (زمان هر صحنه و هر کلمه‌ی زیرنویس) از `chunks.json` |
| `music.py` | موسیقی پس‌زمینه‌ی ۱۱۲ ضرب (سنتور، دف، دست) |
| `audio.py` | افکت‌های صوتی + میکس نهایی (‎-14.6 LUFS) |
| `render.js` | رندر فریم‌به‌فریم با Chromium/Playwright |

## ساخت دوباره
```bash
npm install            # gsap و فونت‌ها
python3 vo_edit.py media/vo_raw.mp3 media/vo.wav chunks.json 1.24
python3 make_timing.py chunks.json 1.0
python3 music.py media/music_local.wav 33.47
node render.js frames 30 2 3                      # 2160x3840
python3 audio.py frames/sfx.json media/vo.wav media/music_local.wav media/mix.wav 33.47
ffmpeg -framerate 30 -i frames/%05d.jpg -i media/mix.wav -c:v libx264 -preset slow -crf 16 \
  -pix_fmt yuv420p -c:a aac -b:a 320k -shortest -movflags +faststart out.mp4
```
برای تغییر متن‌ها، `index.html` را ویرایش کنید؛ برای پیش‌نمایش زنده: `index.html?play`.

## وضعیت اصلاحات (در جریان)
- صحنه‌ی ۲: کاسه‌ی سالاد اضافه شد (همزمان با کلمه‌ی «سالاد»).
- متن گوینده اصلاح شد: «این نارنج، سبزه»، «شکوفه‌اش همون بهارنارِنجه»، «رنگ پوست مِلاکِ رسیدن نیست» (نود Meisam در فلوی ElevenLabs: nAf6t5Z8NEFbfGxhh8FS / 8C2w6QmLnqjyL443Y85b).
- `vo_edit2.py`: هم‌ترازی خودکار جمله‌ها با مکث‌ها + سرعت با atempo (به‌جای rubberband که صدا را «فضادار» می‌کرد) + زنجیره‌ی پاک‌سازی.
- قدم بعد: ساخت صدای جدید Meisam، سپس:
  `python3 vo_edit2.py media/vo_new.mp3 media/vo.wav chunks.json 1.2 0.1 && python3 make_timing.py chunks.json 1.0` و رندر/میکس طبق بالا.
