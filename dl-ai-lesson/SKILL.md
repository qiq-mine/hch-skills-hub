---
name: dl-ai-lesson
description: "AI 技术讲解与 DeepLearning.AI 课程视频制作全流程。涵盖外网字幕提取、7 场景旁白翻译、HTML 故事板审阅门禁、TTS 语音合成（edge-tts/DashScope）、双渲染引擎（分支 A：Python/Pillow/ffmpeg 确定性渲染；分支 B：Remotion/React 审阅优先）以及小红书 3:4 竖版图文卡片与多集批量渲染。Triggers: dl-ai-lesson, /dl-ai-lesson, deeplearn-vp-create, 视频制作, AI课程视频, 课程视频, Remotion视频, 课程翻译配音, 课程搬运, 小红书图文卡片."
---

# DL.AI 课程视频制作与端到端发布管线

从截图、讲稿、大纲或 DeepLearning.AI 原始页面制作面向中文学习者的 AI 技术讲解视频及多渠道宣发物料。同一套制作标准，双渲染引擎二选一（用户指定 Remotion 走分支 B，默认分支 A）。

- **分支 A：Python/Pillow/ffmpeg 确定性渲染** — 可复用场景函数、CLI 驱动、逐帧可控。
- **分支 B：Remotion/React 审阅优先** — 先出 `review.html` 故事板供用户确认，再进 Remotion 渲染。
- **多端资产交付**：1080p 视频成片 + 双尺寸封面（16:9 / 4:3）+ 小红书 3:4 竖版图文卡片（1080×1440）。

**合规约束**：BGM 采用原创或 license-safe 素材；字体禁止自动下载商用字体（OPPO Sans 仅当本地已安装时使用）。

---

## 端到端工作流 (End-to-End Workflow)

```
[素材/页面提取] ──> [7 场景结构化切分] ──> [HTML 故事板审阅] ──> [TTS 配音缓存] ──> [双渲染引擎] ──> [多端成片交付]
   (Phase 1)           (Phase 2)             (Phase 2.5)          (Phase 3)         (Phase 4)          (Phase 5)
```

### 1. 素材与字幕输入 (Phase 1)
- **本地素材路径**：`image/` 截图定风格、`docs/` 查大纲、`captions/` 拿旁白、旧 `output/` 看已有渲染器。
- **DeepLearning.AI 在线提取**：已登录课程页面在 Console 执行 `document.getElementById('__NEXT_DATA__')` 提取 `captions` 纯文本；批量多课逐页提取并存为 `captions/epXX.txt`。详细脚本与超时恢复见 [references/deeplearning-ai-pipeline.md](references/deeplearning-ai-pipeline.md)。

### 2. 7 场景结构化翻译与分镜规划 (Phase 2)
短视频合并为学习者友好的章节；可见标题用学习者语言（如 `第一章：RAG 全景入门`），不暴露内部编号。按讲稿逻辑切为经典 7 场景：
1. **Intro (18–20s)**：标题卡 + 课程引入
2. **核心概念 (27–30s)**：核心模式/原理图解
3. **代码结构 (28–30s)**：第一段代码走读
4. **提示词/工具 (27–29s)**：第二段代码走读
5. **运行示例 (40–45s)**：执行 trace 展示
6. **自动化/进阶 (33–35s)**：第三段代码走读
7. **Outro (16–18s)**：总结 + 下集预告 + 系列导航

每场景旁白按句切分（每行 15–25 字），忠实原意不自由发挥，存为 `narration/epXX/s1.txt` ~ `s7.txt`。

### 3. HTML 故事板预览审阅门禁 (Phase 2.5，必须)
**全量渲染前必须生成 HTML 故事板供用户确认，确认配色、版式、镜头数、封面后再进入 TTS 与最终渲染：**
- 分支 A：先渲染 contact sheet + 至少一帧全尺寸预览；
- 分支 B：先出单文件 `preview/epXX-storyboard.html` 或 `review.html`。

### 4. TTS 语音合成与混音 (Phase 3)
- 文案定稿后再生成配音；TTS 按场景缓存源音频，归一化为统一 WAV 后再拼接。
- **edge-tts**：首选 `zh-CN-YunyangNeural`（云扬男声，新闻主播腔，专业稳重），通过 `python -m edge_tts` 调用；备选 `XiaoxiaoNeural` / `YunxiNeural`。
- **DashScope**：Omni 的 `林川野` 对应 voice 名 `Raymond`；API Key 严禁硬编码，走环境变量；裸 PCM 按 `s16le/24000Hz` 转换。
- **混音原则**：人声绝对优先，BGM 低衬（0.04–0.06 音量），淡入淡出。

---

## 分支 A：Python/Pillow/ffmpeg 确定性渲染

构建或复用确定性渲染器（Python + Pillow + ffmpeg）：可复用的场景函数、共享字体/配色常量、CLI 参数（`--version`、`--res`、`--tts-backend`、`--force-tts`、`--preview-only`、`--audio-only`）。

### 生产规则
- 1080p 必须原生渲染，禁止 720p 放大（消除锯齿与文字发虚）。
- 坐标/字号/线宽/贴图尺寸全部用可缩放写法；用 `--preview-only --res 1080p` 验证。
- TTS 后加场景停顿：普通 0.55s、提问 0.72s、转场 0.90s、结尾 0.65s。
- 字幕放底部、最多两行、白字深色描边；用户不喜欢就不加进度条。
- 片尾按给定结尾截图风格：下集标题 + 课程 chips + 底部简短 callout。
- OPPO Sans 4.0 只从本地字体路径读取，不自动下载商用字体。

实现与排错读 [references/rag-video-pipeline.md](references/rag-video-pipeline.md)。

---

## 分支 B：Remotion/React 审阅优先

### 强制顺序
1. 读取 `image/`、字幕、文档、已有音频与旧产出。
2. `scene-plan.json` 定义每个场景：学习者标题、视觉意图、时长、音频、字幕、是否允许狗讲师。
3. **先建 `review.html`**，用户确认配色、字体、版式、场景数、片尾、封面后再写 Remotion。
4. React/Remotion 实现：动画只用 `useCurrentFrame()`、`interpolate()`、`spring()`、`Sequence`；禁用 CSS 动画/过渡。
5. 每场景挂缓存旁白、BGM 服从人声；先渲染关键帧 + 低分辨率带声预览，再原生 1080p。
6. 交付两个封面：16:9（视频平台）与 4:3（课程/目录），都存进项目输出目录。

工程规范读 [references/production.md](references/production.md)；Remotion 迁移与渲染排错读 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 多端物料交付与宣发卡片 (Phase 5)

1. **成片校验**：用 ffmpeg 校验分辨率（1920×1080）、帧率（30fps）、音频流、响度与时长。保留历史版本，`--version` 递增不覆盖。
2. **小红书 3:4 宣发图文卡片**：
   - 尺寸：1080×1440（3:4 竖版）；
   - 6 张标准套件：封面 / 核心概念图 / 职责逻辑 / 代码走读 / 金句洞察 / 系列导航；
   - 由 Remotion 静态 Composition 或 Pillow 导出为 PNG。
3. **多集批量流水线**：每课独立 URL 与独立发布编号（如 `EP.01+标题`），采用 PowerShell 脚本进行批量音频与目录脚手架初始化，顺序执行渲染命令。

批量工作流与避坑清单详见 [references/deeplearning-ai-pipeline.md](references/deeplearning-ai-pipeline.md)。

---

## 创意与风格默认值（两分支通用）

- 中文技术讲解动画：浅灰白底、扁平卡片/图标、简单流程图、代码/应用窗口、底部中文字幕。
- 狗讲师只出现在提问/提示场景，不每页都用。
- 字体：OPPO Sans 4.0（本地有才用，引用前先验文件）；代码用等宽。
- 标题/标签用学习者语言（如 `信息检索增强`）；用户否决过的装饰词（如 `小课堂`）不再用。
- 示例本地化：地名用人话（如深圳）；真人示例非必要不用。
- 转场：大主题之间加过渡场景、让旁白停顿；不要从头到尾 uninterrupted 念稿。
- 屏幕示例：用通用应用 mockup，除非用户给了真实截图或点名品牌。

---

## 交付清单

上报：HTML 故事板审阅路径、场景数据路径、配音来源与音色说明、渲染分辨率、成片 MP4 路径、16:9 / 4:3 双封面路径、小红书 3:4 宣发卡片路径。

---
*2026-10-08：深度合并 `deeplearn-vp-create`（字幕提取、7场景分镜、云扬配音、小红书卡片全流程）与 `dl-ai-lesson`（Pillow/Remotion 双渲染引擎规范），统一为端到端技术视频制作与多端发布完整管线。*
