---
name: dl-ai-lesson
description: "从截图、讲稿、大纲制作面向中文学习者的 AI 技术讲解视频。同一套制作标准，两种渲染器二选一：分支 A（Python/Pillow/ffmpeg 确定性渲染）与分支 B（Remotion/React 审阅优先）。涵盖分集分镜规划、审阅门禁、TTS 混音、OPPO Sans 字体规范与成片校验。Triggers: dl-ai-lesson, /dl-ai-lesson, 视频制作, AI课程视频, 课程视频, Remotion视频."
---

# DL.AI 课程视频制作

从截图、讲稿、大纲制作面向中文学习者的 AI 技术讲解视频。同一套制作标准，两种渲染器二选一（用户说 Remotion 走分支 B，否则默认分支 A）。

- **分支 A：Python/Pillow/ffmpeg 确定性渲染** — 可复用场景函数、CLI 驱动、逐帧可控。
- **分支 B：Remotion/React 审阅优先** — 先出 `review.html` 给用户确认，再进 Remotion 渲染。

**合规**：BGM 用原创或 license-safe 素材；字体不用自动下载的商用字体（OPPO Sans 仅当本地已安装时使用）。

## 共享工作流

1. 先看素材：`image/` 截图定风格、`docs/` 看大纲、`captions/` 拿旁白、旧 `output/` 看已有渲染器。
2. 先规划分集/分镜再渲染。短源视频合并为学习者友好的章节；可见标题用学习者语言（如 `第一章：RAG 全景入门`），不暴露内部编号。
3. **审阅门禁**：分支 A 先渲染 contact sheet + 至少一帧全尺寸预览；分支 B 先出 `review.html` 故事板。用户确认配色、版式、镜头数、封面后再进全量渲染/TTS。
4. 配音只在文案定稿后生成。TTS 按场景缓存源音频，归一化为统一 WAV 后再拼接。
5. 混音人声优先：BGM 低衬于旁白，淡入淡出。
6. 用 ffmpeg 校验成片：分辨率、时长、音频编码、响度、源音频可解码。
7. 保留历史版本：`--version` 递增，不覆盖旧产出（用户明确要求除外）。

## 分支 A：Python/Pillow/ffmpeg 确定性渲染

构建或复用确定性渲染器（Python + Pillow + ffmpeg）：可复用的场景函数、共享字体/配色常量、CLI 参数（`--version`、`--res`、`--tts-backend`、`--force-tts`、`--preview-only`、`--audio-only`）。

### 生产规则

- 1080p 必须原生渲染，禁止 720p 放大（卡片边缘波浪、线条锯齿、文字发虚）。
- 坐标/字号/线宽/贴图尺寸全部用可缩放写法；用 `--preview-only --res 1080p` 验证。
- TTS 后加场景停顿：普通 0.55s、提问 0.72s、转场 0.90s、结尾 0.65s。
- 字幕放底部、最多两行、白字深色描边；用户不喜欢就不加进度条。
- 片尾按给定结尾截图风格：下集标题 + 课程 chips + 底部简短 callout。
- OPPO Sans 4.0 只从项目/用户/系统字体路径取，不自动下载商用字体。
- DashScope Omni 的 `林川野` 对应 voice 名 `Raymond`（Qwen-TTS 列表里没有）。

实现与排错读 [references/rag-video-pipeline.md](references/rag-video-pipeline.md)。

## 分支 B：Remotion/React 审阅优先

### 强制顺序

1. 看 `image/`、字幕、文档、已有音频与旧产出。
2. `scene-plan.json` 定义每个场景：学习者标题、视觉意图、时长、音频、字幕、是否允许狗讲师。
3. **先建 `review.html`**，用户确认配色、字体、版式、场景数、片尾、封面后再写 Remotion。
4. React/Remotion 实现：动画只用 `useCurrentFrame()`、`interpolate()`、`spring()`、`Sequence`；禁用 CSS 动画/过渡。
5. 每场景挂缓存旁白、BGM 服从人声；先渲染关键帧 + 低分辨率带声预览，再原生 1080p。
6. 交付两个封面：16:9（视频平台）与 4:3（课程/目录），都存进项目输出目录。

开场、版式最密页、狗提问场景、片尾四张 1920×1080 静帧通过前，不开原生 1080p 渲染。

工程规范读 [references/production.md](references/production.md)；Remotion 迁移与渲染排错读 [references/troubleshooting.md](references/troubleshooting.md)。

## 创意与风格默认值（两分支通用）

- 中文技术讲解动画：浅灰白底、扁平卡片/图标、简单流程图、代码/应用窗口、底部中文字幕。
- 狗讲师只出现在提问/提示场景，不每页都用。
- 字体：OPPO Sans 4.0（本地有才用，引用前先验文件）；代码用等宽。
- 标题/标签用学习者语言（如 `信息检索增强`）；用户否决过的装饰词（如 `小课堂`）不再用。
- 示例本地化：地名用人话（如深圳）；真人示例非必要不用。
- 转场：大主题之间加过渡场景、让旁白停顿；不要从头到尾 uninterrupted 念稿。
- 屏幕示例：用通用应用 mockup，除非用户给了真实截图或点名品牌。

## TTS 与配音

- 配音 key 永不硬编码进项目文件：走环境变量或本地忽略的 key 文件（如 `dashscope_api_key.txt`）。
- DashScope 报 `AccessDenied`/key 受限：先查账号与 key 策略，不是渲染器 bug。
- Qwen-TTS 与 Omni 是两条路线；`林川野`（Raymond）只在 Omni voice 列表。
- Omni 流式音频 chunk 可能是裸 PCM（非 WAV 容器）：按 `s16le`、`24000Hz`、单声道转后再重采样为项目 WAV。
- 流事件可能含空 `choices`：防御性解析，跳过非音频事件。
- 文案变了就 `--force-tts` 重生成对应场景缓存。
- edge-tts 用户：`python -m edge_tts` 调用；部分音色（如 XiaochenNeural/XiaohanNeural）可能 NoAudioReceived，先 `--list-voices` 确认。

## 交付

上报：HTML 审阅路径、场景数据路径、配音来源、渲染分辨率、成片路径、两个封面路径； provisional TTS 音色要明确说明待替换。旧构建保留。

## 待补充内容与规划 (TODO / Backlog)

> [!NOTE]
> 制作标准流程已定，以下配套工程资产待封装补充：

- [ ] **渲染器代码模板**：开箱即用的 Python + Pillow + ffmpeg 最小可运行渲染器脚手架（如 `scripts/render_lesson.py`）。
- [ ] **场景配置文件范例**：分集/分场景配置 YAML/JSON 模板（如 `configs/scene_plan.example.yaml`）。
- [ ] **通用字体与素材包**：开源合规中文字体引用指引、转场/BGM 推荐配置示例。
- [ ] **分镜头规划模板**：`assets/scene-plan.example.json` 示例结构与字段定义。
- [ ] **HTML 故事板模板**：轻量单文件 `assets/review-template.html` 快速预览。
- [ ] **Remotion 示例工程**：可复用的 `Root.tsx` 与封面（16:9 / 4:3）Composition 范例代码。

---
*2026-10-08：由 `dl-ai-lesson-create`（Python/Pillow/ffmpeg 确定性渲染）与 `dl-ai-lesson-remotion`（Remotion 审阅优先）合并为 `dl-ai-lesson`（渲染器分支 A/B 二选一；references 三份原样保留）。*
