# WIW video pipeline — instructions for Claude

Goal: Wealth In Whispers (English, US/Canada audience) short videos with the fewest tokens.
**Your only job per video: write `content/<YYYY-MM>/<slug>/spec.yaml`, commit, push.** GitHub Actions does voice (if
ELEVENLABS_API_KEY is set), timing, render, cover, HighLevel upload (Media Storage `WIW/<Month YYYY>/`), posting to
YouTube/Instagram/Facebook/TikTok/LinkedIn, and deleting media after every post is live (`cleanup.yml`).

Do NOT read tools/*.py or engine/ unless something is broken. Do NOT render locally unless asked for a preview.
Do NOT call the HighLevel connector to post — the workflow does it. Batch several videos in one push.

## Workflow per batch
1. Research facts (cite sources in `source:`; never invent numbers). Keep each video 25–45 s (8–14 lines).
2. Write one spec per video (template below). Rotate `theme` dark → cream → violet.
3. If no ElevenLabs key in the repo: run `python tools/voice.py <folder>` → give the user `script.txt` to voice; the
   user drops `voice.mp3` into the folder (GitHub web upload) and the push triggers everything.
4. `publish: review` first if the user wants to see it (video appears as the run's `videos` artifact); then change to
   `now` or a time and delete nothing else — re-run with workflow_dispatch.
5. For each video also add a matching entry to `lib/breakdowns.ts` in the `000alimran/wiw` site repo (adds the
   article page, sitemap and llms.txt entry); set `youtubeId` once the Short is live.
6. Status lives in `state.json` (written by the workflow). `cleaned: true` = media deleted.

## spec.yaml reference
```yaml
slug: short-kebab-name
theme: dark | cream | violet
publish: review | now | "2026-11-24 11:00 America/New_York"
platforms: [youtube, instagram, facebook, tiktok, linkedin]   # optional, default all
voice_id: <ElevenLabs voice id>                                 # only for auto voice
title: "YouTube title, <=100 chars"
source: "Source: ... · Not financial advice"
hashtags: [Tag1, Tag2]          # no '#'
cover: {line1: "BIG HOOK", line2: "second line", line3: "small label", tone: bad|good}
caption: {long: "IG/LinkedIn/YouTube text (CTA + hashtags auto-added)", short: "FB/TikTok one-liner"}
scenes:                          # each scene = 1 visual held while its lines are spoken
  - lines: ["Caption text, *good highlight*, ~bad highlight~.", {show: "$104B", say: "one hundred and four billion dollars"}]
    visual: {type: ..., stamp: {text: "NOT CASH", at: 1, top: 330, side: left, x: 210, rot: -8}}   # stamp optional
```
`at`: integer = start of that line within the scene (0-based); "+1.5" = seconds after scene start.

Visual types:
- `bignum`: label, value, prefix, suffix, decimals, sep (thousands commas), tone, note, size
- `title`: kicker, text, size, underline (bool), sub
- `bars`: label, items[{name, value (negative hangs down), display, tone, at}], valsize
- `split`: label, parts[{value, display, name, tone, hatch}]   (one bar = parts of a total)
- `flow`: items[{icon, title, sub, tone, at}]                     (vertical cards with arrows)
- `compare`: items[{value, display, name, at}] x2                (block area = ratio)
- `statement`: items[{text, size, tone, strike, strike_at, at, anim}]
- `gauge`: label, from, to, suffix, at, note
- `checklist`: title, items[str], at
- `cta`: kicker, text, handle
Tones: good, bad, mut, ink. Example: `examples/anthropic-104b-catch/spec.yaml`.
