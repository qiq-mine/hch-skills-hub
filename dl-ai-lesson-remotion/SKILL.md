---
name: dl-ai-lesson-remotion
description: Build review-first Remotion workflows for Chinese AI explainer videos about RAG, Agent, LLM, retrieval, vector databases, and prompting. Use when turning captions and outlines into an HTML scene review, synchronized Chinese voiceover, 1080p Remotion renders, subtitles, BGM, and 16:9 plus 4:3 course covers.
---

# Remotion AI 课程制作

Use a review-first workflow. Read [references/production.md](references/production.md) before building or revising a project. Read [references/troubleshooting.md](references/troubleshooting.md) before migrating approved HTML into Remotion or diagnosing Windows render failures.

## Required order

1. Inspect `image/`, captions, docs, existing audio, and previous outputs.
2. Define every scene in `scene-plan.json`: learner-facing title, visual intent, duration, audio, subtitle, and whether the dog lecturer is allowed.
3. Build `review.html` before a Remotion composition. Let the user approve palette, typography, layout, scene count, outro, and covers before rendering video.
4. Implement the approved plan in React/Remotion. Drive animation only with `useCurrentFrame()`, `interpolate()`, `spring()`, and `Sequence`; do not use CSS animations or transitions.
5. Attach cached narration per scene and keep BGM subordinate to speech. Render a key frame and a low-resolution voiced preview before the native 1080p render.
6. Deliver two cover assets: 16:9 for video platforms and 4:3 for course/catalog uses. Store both inside the project output folder.

Never start the native 1080p render until representative 1920×1080 stills pass for the opening, densest layout, dog-question scene, and outro.

## Style defaults

- Match supplied screenshots, not a generic SaaS dashboard.
- Use large blank areas, collage-like screenshots/icons, thin grey arrows, charcoal text, and orange only as emphasis.
- Use OPPO Sans 4.0 when present; verify the local font file before claiming it is active.
- Use the dog lecturer only for raw-question/prompt scenes.
- Keep subtitles at the bottom as white text with dark outline; no progress bar.
- Include a chapter-complete page and next-chapter teaser when a reference ending is available.

## Delivery

Preserve old builds. Report the HTML review path, scene data path, voice source, render resolution, video path, and both cover paths. State clearly if a provisional TTS voice remains to be replaced.

## 待补充内容与规划 (TODO / Backlog)

> [!NOTE]
> 本技能核心规范明确，以下辅助工程模板待补充入库：

- [ ] **分镜头规划模板**：补充 `assets/scene-plan.example.json` 示例结构与字段定义。
- [ ] **HTML 故事板模板**：补充轻量单文件 `assets/review-template.html` 供快速预览。
- [ ] **Remotion 示例工程**：提供可复用的 `Root.tsx` 与封面 (16:9 / 4:3) Composition 范例代码。
