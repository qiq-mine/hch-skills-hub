# AI Video Prompting Guide

This reference provides prompt structures, cinematic terminology, and best practices for AI video generation models (Runway Gen-3, Kling, Pika, Google Veo, Luma Dream Machine).

---

## 1. Core Prompt Formula

A robust video prompt should be structured in priority order:

```
[Shot Type & Camera Movement] + [Subject & Core Action] + [Environment & Setting] + [Lighting & Atmosphere] + [Style & Visual Quality]
```

### Example
> "Low-angle tracking shot following a software engineer walking through a server room filled with glowing blue LED racks, cinematic volumetric smoke, rim lighting, shot on 35mm lens, 4k ultra-detailed, photorealistic."

---

## 2. Cinematic Camera Terminology

| Camera Move | Description | Prompt Keyword |
|-------------|-------------|----------------|
| **Dolly In / Out** | Camera moves physically toward or away from subject | `dolly in`, `push in`, `dolly out` |
| **Pan Left / Right** | Camera swivels horizontally on fixed axis | `pan left`, `pan right` |
| **Tilt Up / Down** | Camera angles vertically up or down | `tilt up`, `tilt down` |
| **Tracking / Follow** | Camera physically follows moving subject | `tracking shot`, `follow shot` |
| **Orbit / Arc** | Camera circles around the focal point | `orbiting shot`, `360 arc shot` |
| **Crane / Jib** | Vertical overhead movement | `crane shot descending`, `jib shot` |
| **FPV / Handheld** | Dynamic, first-person or subtle shake | `FPV drone dive`, `subtle handheld camera movement` |
| **Static / Locked** | Camera stays completely still; only scene elements move | `locked-off tripod shot`, `static frame` |

---

## 3. Shot Framing & Angles

- **Wide / Establishing Shot (`extreme wide shot`, `establishing aerial shot`)**: Sets the scene, location, scale.
- **Medium Shot (`medium shot`, `cowboy shot`)**: Balances character actions with surroundings.
- **Close-up (`close-up`, `macro shot`)**: Emphasizes emotional reaction, hand interaction with hardware/tools.
- **Low Angle (`low-angle shot`)**: Makes subjects appear powerful, dominant, dramatic.
- **High Angle / Bird's Eye (`bird's-eye view`, `top-down shot`)**: Shows layouts, architectural patterns, flows.

---

## 4. Lighting & Color Palette

- **Golden Hour / Sunset**: `warm golden hour glow, long dramatic shadows`
- **Cyberpunk / Tech**: `neon cyan and magenta accent lights, high contrast, dark reflective surfaces`
- **Studio Clean**: `soft diffused three-point studio lighting, clean white backdrop, even illumination`
- **Cinematic Volumetric**: `shafts of sunlight piercing through dust particles, volumetric fog, rim lighting`
- **Monochrome / Muted**: `desaturated tones, cool blue moody atmosphere`

---

## 5. Model-Specific Best Practices

### Runway Gen-3 Alpha
- Excels at complex camera motions and realistic physics.
- Use explicit speed descriptors: `slow, steady dolly push` or `high-speed whip pan`.
- Structure text with camera instructions first.

### Kling 1.5 / 2.0
- Excellent for realistic human figures, gestures, and fluid natural motion.
- Avoid overly crowded crowds; describe 1-2 primary figures clearly.

### Google Veo
- Handles cinematic lighting and high semantic understanding.
- Specify lens types (e.g. `anamorphic lens, cinematic bokeh, 24fps`).

---

## 6. What to Avoid (Negative Constraints)

- **Do NOT ask AI models to generate text on signs or screens**: Video diffusion models scramble letterforms. Add text programmatically (Remotion / Hyperframes / After Effects).
- **Avoid conflicting movements**: E.g., `zooming in while subject runs away and camera pans left` causes morphing glitches.
- **Avoid vague descriptors**: Instead of `looks nice and modern`, write `brutalist concrete architecture, floor-to-ceiling glass, minimalist oak furniture`.

---

## 7. 待补充内容与扩展 (TODO)

> [!NOTE]
> 持续维护与补充计划：
> - [ ] 补充不同模型版本（Gen-3 vs Kling vs Veo）实测 Prompt 对比图谱与渲染参数
> - [ ] 补充各主流平台（YouTube Shorts / TikTok / Bilibili）高完播率开篇 3 秒视觉 Prompt 模板库