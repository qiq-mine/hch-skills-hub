# Production notes

## Asset and data layout

- Keep `scene-plan.json` as the review/production source of truth. Do not let HTML and Remotion drift silently.
- Put Remotion-accessible audio, images, and BGM under `public/`. Reuse source media via safe copy or hard link; do not alter originals.
- Map audio to scene `Sequence`s. Scene duration should include the intended pause after narration.

## HTML approval

Build a static `review.html` with a scene navigator. It should display the 16:9 frame, subtitle treatment, dog-use rule, and outro/next lesson. Fix overlap in HTML first.

Keep the approved HTML class hierarchy intact when reusing its CSS in Remotion. If markup changes, use chapter-scoped classes rather than relying on a multi-level `@import` chain. Treat the scene plan, review HTML, and Remotion data as generated views of the same scene records.

## Rendering

- Use a 1920×1080 composition at 30fps for final output; do not upscale a lower-resolution render.
- Validate full-size stills for the opening, densest layout, dog-question scene, and outro after typography or subtitle changes.
- Make a transformed wrapper around an absolutely positioned outro full-frame with `position:absolute; inset:0`; otherwise the transform can create a zero-height containing block and clip the heading.
- On Windows, if Remotion browser download/cache fails, supply the installed Edge executable using `--browser-executable`.
- Do not assume a junction to another project's `node_modules` is writable. Remotion writes Webpack cache under `node_modules/.cache`; use independent dependencies/cache or serialize cache-mutating commands with the required permission.
- Long full-chapter renders may run as hidden background processes and be monitored through logs. Do not claim completion until the MP4 exists and has nonzero size.
- Render simultaneous chapters with bounded concurrency, separate logs, and realistic time estimates. Confirm progress from log frame counters instead of assuming silence means a hang.
- Use `ffprobe` after preview and final renders. Require the intended resolution, 30 fps, video and audio streams, plausible duration, and nonzero size.

## Voice and sound

- Cached Edge-TTS is suitable for a voiced preview when final TTS is unavailable. Label it provisional.
- Derive scene duration from the generated WAV, then add an explicit pause. Never time video from narration character count alone.
- Edge-TTS may return no Chinese `WordBoundary` events. Detect an empty boundary list and fall back to punctuation-aware chunks; do not describe fallback subtitles as word-aligned. Prefer clauses near 28–30 Chinese characters and avoid splitting quoted phrases where possible.
- Treat a cache entry as valid only when its WAV is nonzero and its timing metadata parses. Write audio and metadata atomically so an interrupted worker cannot leave a partial file that looks cached.
- For DashScope Omni 林川野, use voice `Raymond`; never hardcode API keys.
- Keep BGM low under narration, around 0.04–0.06 source volume.

## Covers

- Generate separate 16:9 and 4:3 cover images, not a crop of one image.
- Use the chapter title and one short learner-facing hook. Avoid excessive UI elements, logos, or unverifiable product screenshots.
- Persist cover images in `covers/` and report the final prompts and paths.
- Render covers before copying large narration caches into `public/`, or keep cover rendering in a lean composition. Remotion copies the public directory while bundling each still.
