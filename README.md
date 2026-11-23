# Wealth In Whispers — অটো ভিডিও পাইপলাইন

একটা `spec.yaml` লিখে push করলেই GitHub নিজে করবে:
ভয়েস (ঐচ্ছিক) → টাইমিং → ভিডিও রেন্ডার → থাম্বনেইল/কভার → HighLevel Media Storage (`WIW/<মাস>/`) → ৫ চ্যানেলে পোস্ট/শিডিউল → সব লাইভ হলে Media Storage থেকে ফাইল ডিলিট।

## একবারের সেটআপ (৫ মিনিট)
1. **HighLevel token:** YOLO sub-account → Settings → Private Integrations → Create.
   Scopes: `medias.write`, `medias.readonly`, `socialplanner/post.write`, `socialplanner/post.readonly`, `socialplanner/account.readonly`.
2. GitHub repo → Settings → Secrets and variables → Actions → **New repository secret**
   - `GHL_TOKEN` = উপরের token
   - `ELEVENLABS_API_KEY` = (ঐচ্ছিক) দিলে ভয়েসও অটো হবে; না দিলে `voice.mp3` নিজে আপলোড করবে।
3. Settings → Actions → General → Workflow permissions → **Read and write** চালু।

## প্রতিটা ভিডিও
`content/<YYYY-MM>/<slug>/` ফোল্ডারে `spec.yaml` (Claude লিখবে) + `voice.mp3`।
- `publish: review` → শুধু রেন্ডার; ভিডিও Actions রানের **videos** artifact-এ দেখা যাবে।
- `publish: now` → সাথে সাথে পোস্ট।
- `publish: "2026-11-24 11:00 America/New_York"` → শিডিউল।

অবস্থা দেখতে: `state.json` (posts, `cleaned: true` = ফাইল ডিলিট হয়েছে)। ক্লিনআপ প্রতি ২ ঘণ্টায় চলে।

## ফাইল
- `tools/build.py` spec → HTML · `tools/align.py` ভয়েস থেকে লাইনের টাইমিং · `tools/render.py` → MP4 + cover
- `tools/ghl.py` HighLevel আপলোড/পোস্ট/ক্লিনআপ · `tools/voice.py` স্ক্রিপ্ট/ElevenLabs · `tools/themes.py` ৩টা থিম
- `examples/anthropic-104b-catch/` নমুনা spec
