---
name: dl-ai-lesson-create
description: Create or revise Chinese AI technical explainer lesson videos from screenshots, captions, outlines, and docs. Use when producing course-style videos about Agent, RAG, LLM, retrieval, vector databases, or similar AI topics; when adapting a screenshot-driven visual style into a Python/Pillow/ffmpeg renderer; when configuring Chinese TTS, subtitles, BGM, transitions, pauses, typography, and 1080p output; or when documenting/reusing the RAG lesson production workflow.
---

# DL.AI 课程视频制作 (Python/Pillow/ffmpeg)

## Workflow

Use this workflow to produce polished Chinese AI lesson videos rather than one-off slide exports.

1. Inspect source material first: `image/` screenshots for style, `docs/` for outline, `captions/` for source narration, and any prior `output/` renderer.
2. Plan chapters before rendering. Merge short source episodes into learner-friendly chapters and avoid exposing internal names such as `New EP01` unless the user requests them.
3. Build or update a deterministic renderer, usually Python + Pillow + ffmpeg. Prefer reusable scene functions, shared typography, color constants, and CLI flags such as `--version`, `--res`, `--tts-backend`, `--force-tts`, `--preview-only`, and `--audio-only`.
4. Render visual previews before full video. Always generate a contact sheet and at least one full-size frame for edge, typography, and subtitle checks.
5. Generate TTS only after text is stable. Cache per-scene source audio, then normalize/convert to a common WAV format before concatenation.
6. Mix narration and BGM with voice priority. Keep BGM original or license-safe, low under speech, and fade in/out.
7. Validate media with ffmpeg: resolution, duration, audio codec, loudness, and whether source audio can be decoded.
8. Preserve prior outputs by bumping `--version` instead of overwriting unless the user explicitly asks.

## Creative Defaults

- Style: Chinese technical explainer animation with warm grey-green background, flat cards/icons, simple process diagrams, code/app windows, and bottom Chinese subtitles.
- Mascot: use the dog lecturer only on question or prompt scenes, not every page.
- Typography: prefer OPPO Sans 4.0 for Chinese and English if available. Fall back clearly if not installed.
- Title/tag: use `信息检索增强`; avoid decorative labels like `小课堂` if the user rejected them.
- Naming: visible title should be learner-facing, e.g. `第一章：RAG 全景入门`, not internal grouping names.
- Examples: localize names and places for Chinese context. Use Shenzhen for locations and `小美` only when an individual subject is actually needed.
- Screen examples: use generic app-like mockups unless the user supplies real product screenshots or asks for specific brands.
- Transitions: add bridge scenes between major topics and let the narrator pause. Avoid uninterrupted script reading.

## Production Rules

- For 1080p, render at native output scale. Do not draw 720p and simply upscale; this causes wavy card edges, jagged lines, and fuzzy text.
- Use scalable coordinates, font sizes, line widths, and pasted image sizes. Test with `--preview-only --res 1080p`.
- Add per-scene pauses after TTS. Good defaults: ordinary scenes 0.55s, question scenes 0.72s, transition scenes 0.90s, outro 0.65s.
- Keep subtitles at the bottom, max two lines, white with dark stroke. Do not add a progress bar if the user dislikes it.
- Add an outro in the style of the provided ending screenshot: next lesson title, lesson chips, and a concise bottom callout.
- Use OPPO Sans 4.0 from project/user/system font paths when available. Do not download proprietary fonts automatically.
- If using DashScope Omni for `林川野`, set voice to `Raymond`; Qwen-TTS voice lists do not include `林川野`.

## TTS And API Handling

- Never hardcode API keys into generated project files. Prefer environment variables or local ignored key files such as `dashscope_api_key.txt`.
- If DashScope returns `AccessDenied` / API-Key restrictions, treat it as an account/key policy problem, not a renderer bug.
- DashScope Qwen-TTS and DashScope Omni are different routes. `林川野` belongs to Omni voice lists as `Raymond`.
- DashScope Omni streaming audio chunks may be raw PCM rather than a WAV container even when format is `wav`. Convert as `s16le`, `24000Hz`, mono before resampling to project WAV.
- Stream events can include empty `choices`; parse defensively and skip non-audio events.
- If TTS text changes, regenerate cached per-scene audio with `--force-tts`.

## References

Read [references/rag-video-pipeline.md](references/rag-video-pipeline.md) when implementing or debugging the renderer, audio pipeline, transitions, or output commands.

## 待补充内容与规划 (TODO / Backlog)

> [!NOTE]
> 本技能定义了完整的制作标准流程，目前以下配套工程资产待进一步封装补充：

- [ ] **渲染器代码模板**：提供开箱即用的 Python + Pillow + ffmpeg 最小可运行渲染器脚手架（如 `scripts/render_lesson.py`）。
- [ ] **场景配置文件范例**：提供分集/分场景配置 YAML/JSON 模板（如 `configs/scene_plan.example.yaml`）。
- [ ] **通用字体与素材包**：提供开源合规的中文字体引用指引及转场/BGM 推荐配置示例。
