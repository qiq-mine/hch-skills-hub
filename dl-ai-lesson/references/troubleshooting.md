# Remotion lesson troubleshooting

## Review-to-Remotion migration

- Reuse the approved DOM/class hierarchy when importing review CSS. Unsupported replacement classes make an outro collapse even when the content is present.
- Neutralize review-only global rules such as `body { display:grid }` inside the production bundle.
- Make animation wrappers around absolutely positioned layouts full-frame containers. Set `position:absolute; inset:0` before applying `transform` or `scale`.
- Do not leave literal `/dog-tutor.png` paths inside raw HTML. Replace them at render time with `staticFile('dog-tutor.png')`, or build the element in React with `<Img>`.
- Keep subtitles outside injected visual HTML so they remain synchronized and consistently layered.

## TTS and subtitle timing

- Measure speech duration from the decoded WAV and set scene duration to `speech + pauseAfter`.
- Expect Edge-TTS Chinese boundary metadata to be empty on some versions. If empty, split on `。！？；` first, then `，、：`, cap lines near 28–30 characters, and label timing as approximate.
- Validate cache files by nonzero size and parseable metadata. Regenerate partial outputs.
- A terminated parent command may leave an encoder child running on Windows. Inspect output timestamps and active processes before rerunning; never launch two writers for the same file.

## Windows and Remotion

- Prefer the installed Edge binary, commonly `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`, via `--browser-executable` when Chromium discovery stalls.
- A shared or junctioned `node_modules` can fail with `EPERM` when Remotion clears `node_modules/.cache/webpack`. Prefer independent dependencies. If reuse is necessary, serialize cache-mutating commands and use the required permission.
- Store preview and 1080p logs separately per chapter. Verify progress from the last `Rendered x/y` line.
- Parallel full chapters are CPU-heavy. Use bounded concurrency and expect estimates to fluctuate.
- Render covers before copying large narration caches into `public/`, or use a lean cover composition. Remotion copies the public directory while bundling each still.

## Required QA gates

1. TypeScript/build succeeds and compositions report 1920×1080 at 30 fps.
2. Full-size stills pass for opening, dense scene, dog scene, and outro.
3. Voiced 960×540 preview contains H.264 video and AAC audio with the planned duration.
4. Native final is rendered directly at 1920×1080, never upscaled.
5. `ffprobe` confirms resolution, frame rate, audio stream, duration, and nonzero file size.
6. Covers exist as separately composed 16:9 and 4:3 PNGs.
