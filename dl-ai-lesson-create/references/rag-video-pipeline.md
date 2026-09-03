# RAG Chinese Lesson Video Pipeline

Use this reference when creating or maintaining a Python-generated Chinese AI course video like the RAG lesson.

## Input Layout

Expected project pattern:

- `image/`: visual references and ending screenshot.
- `docs/`: course outline and Chinese notes.
- `captions/`: source episode captions.
- `demo/`: prototype assets and voice samples.
- `output/new-ep01/`: generated renderer, assets, audio cache, subtitles, previews, and videos.

Inspect screenshots visually before writing the renderer. Capture the palette, typography density, subtitle style, character usage, cards, code windows, and app mockup conventions.

## Renderer Pattern

Prefer a single deterministic Python renderer:

- `SCENES`: list of scene dictionaries with `section`, `title`, `layout`, `duration`, and `voice` or transition `body`.
- Scene functions: `scene_title`, `scene_question`, `scene_pipeline`, `scene_code`, `scene_transition`, `scene_outro`.
- Shared helpers: rounded rectangle, multiline wrapping, centered text, arrows, dog placement, subtitles, audio conversion.
- CLI flags: `--version`, `--res`, `--tts-only`, `--render-only`, `--preview-only`, `--audio-only`, `--force-tts`, `--tts-backend`.

Output naming should preserve versions:

```powershell
python output\new-ep01\build_new_ep01.py --version v6 --res 1080p --force-tts
```

## Visual Preferences From This Project

- Use warm grey-green background, off-white cards, orange highlights, dark charcoal text, muted grey labels, and soft green accents.
- Use OPPO Sans 4.0 when installed. Check project `fonts/`, output `fonts/`, user font directory, and `C:\Windows\Fonts`.
- Render 1080p natively with scaled coordinates, line widths, font sizes, pasted images, and background texture. Do not upscale a 720p frame.
- Keep the dog lecturer only on question/prompt scenes.
- Use generic app screenshots for examples unless the user supplies real screenshots.
- Keep top-right tag as `信息检索增强`.
- Do not show `New EP01`; visible chapter labels should be `第一章：...`.
- Avoid a bottom progress bar if the user has rejected it.
- Add an outro based on the provided ending screenshot: next lesson, lesson chips, and a bottom callout.

## Narration And Rhythm

Do not run the narration as an uninterrupted script. Add bridge scenes and pauses.

Recommended major transition scenes:

- Course overview to problem framing.
- Problem framing to applications.
- Applications to system architecture.
- Architecture to LLM internals.
- LLM internals to chapter summary.

Recommended pause padding after each generated TTS segment:

- Ordinary content: `0.55s`
- Question/prompt scenes: `0.72s`
- Transition scenes: `0.90s`
- Outro: `0.65s`

Transition scenes should carry one short bridge sentence, such as:

- `我们先不讲架构，先看它为什么会答错。`
- `知道它怎么做之后，我们看看它到底能放在哪些地方。`
- `场景很多，但底层结构其实可以收束成几块固定组件。`

## TTS Backends

Keep backend selection configurable.

### Edge TTS fallback

Use when API keys are unavailable or when quick offline-ish validation is enough after prior dependency setup. Example voice used in the project:

```text
zh-CN-YunyangNeural
```

### DashScope Qwen-TTS

Use for Qwen-TTS voices such as `Ethan`, `Neil`, `Cherry`, or `Emilien`. Do not use it for `林川野`; Qwen-TTS does not expose that voice name.

Common 403:

```text
AccessDenied: Access denied by API-Key restrictions.
```

Treat this as key/model/workspace policy, not as a Python rendering issue.

### DashScope Omni / 林川野

Use DashScope Omni for `林川野`:

```text
model: qwen3.5-omni-plus
voice: Raymond
```

The compatible endpoint may need a workspace URL:

```text
https://<WorkspaceId>.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
```

Do not assume stream events always contain `choices[0]`; some events are empty or usage-only.

Important pitfall: stream `audio.data` can be raw PCM, not a WAV file. Convert with ffmpeg as:

```text
-f s16le -ar 24000 -ac 1 -i source.pcm
```

Then resample to the project standard:

```text
-af apad=pad_dur=<pause> -ar 44100 -ac 1 -c:a pcm_s16le segment.wav
```

## Audio Mix

- Concatenate normalized WAV narration segments.
- Generate or provide license-safe BGM.
- Mix with voice loudnorm/compression first, BGM lowpass/highpass and low volume, fade BGM in/out, then limiter.
- Verify loudness with ffmpeg loudnorm. Around `-15` to `-17 LUFS` integrated is acceptable for this course style, with BGM below speech.

## Validation Checklist

Before final response, verify:

- `py_compile` passes for the renderer.
- `--preview-only --res 1080p` produces a contact sheet.
- At least one full-size 1080p frame is inspected for text overflow, card edges, and line aliasing.
- TTS source audio decodes or raw PCM conversion succeeds.
- Final MP4 has expected resolution, duration, H.264 video, AAC audio.
- SRT and script markdown are regenerated from current scenes.
- Previous versions are not overwritten unless requested.

## User Preference Memory

For this course, carry these preferences unless the user overrides them:

- Chinese technical explainer animation.
- OPPO Sans 4.0 typography.
- `林川野` voice via DashScope Omni `Raymond`.
- Shenzhen for locations.
- Use `小美` only when a person is needed.
- Add Chinese internet-native phrasing.
- Use bridge transitions and pauses between topics.
- Preserve app screenshot-style mockups where examples benefit from context.
