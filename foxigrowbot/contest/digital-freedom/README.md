# Digital Freedom Contest Video

Entry video for the **$200,000 Digital Freedom Contest** (deadline: July 15, Dubai time).

## Final files

| File | Format | Use on |
|------|--------|--------|
| `output/digital-freedom-contest-vertical.mp4` | 9:16 (1080×1920) | TikTok, Instagram Reels, YouTube Shorts, Snapchat |
| `output/digital-freedom-contest-horizontal.mp4` | 16:9 (1920×1080) | X (Twitter), YouTube |

**Duration:** ~52 seconds

## What’s in the video

- **Hook:** Titanic metaphor — freedoms sinking
- **Durov speech segment:** Oslo Freedom Forum footage frame with source URL (`youtube.com/watch?v=1Yq_5aDdJ24`)
- **Key quotes** from Pavel Durov’s speech on surveillance, privacy, and Telegram
- **CTA:** Defend digital freedom + FoxiGrow branding

## Contest compliance

✅ Uses **ideas and quotes** from @durov’s Oslo Freedom Forum speech  
✅ Includes **speech source footage frame** with YouTube link and play overlay  
✅ Topic: **digital freedom**  
✅ English narration + on-screen text  

### Recommended before submitting

For strongest compliance, splice in **10–15 seconds of actual video** from the speech:

1. Download locally: https://www.youtube.com/watch?v=1Yq_5aDdJ24
2. Clip the Titanic opening or “this deal is always a scam” section
3. Replace segment `02_intro` / `03_quote1` in the timeline

```bash
# Example: insert a real clip over the speech segment
ffmpeg -i durov_clip.mp4 -i output/digital-freedom-contest-vertical.mp4 \
  -filter_complex "[1:v][0:v]overlay=enable='between(t,2,12)'" final.mp4
```

## Rebuild

```bash
cd foxigrowbot/contest/digital-freedom
pip install pillow edge-tts
python3 build_video.py
```

## Posting checklist

- [ ] Post on TikTok / IG / YouTube / X / Snapchat Spotlight
- [ ] Use hashtags: `#DigitalFreedom` `#Telegram` `#PavelDurov` `#FoxiGrow`
- [ ] Caption example below
- [ ] Wait for July 6 submission instructions on @FoxiGrow channel
- [ ] Target 10,000+ authentic views

## Suggested caption

> They said give up privacy for safety. Pavel Durov says that deal is always a scam. 🦊
>
> Our digital freedoms are sinking — and most people don’t see it yet.
>
> Full speech: https://www.youtube.com/watch?v=1Yq_5aDdJ24
>
> #DigitalFreedom #Telegram #Privacy #PavelDurov #FoxiGrow
