---
name: deeplearning-ai-course-pipeline
description: >-
  Standardized engineering pipeline and operational manual for archiving, localizing, and producing DeepLearning.AI video courses.
  Use this skill when processing new DeepLearning.AI courses, extracting and formatting 4-format dual-language subtitles,
  synthesizing Chinese Neural TTS dubbing with elastic timeline alignment and FFmpeg multi-track packaging,
  verifying asset integrity, or writing comprehensive architectural summary guides.
---

# DeepLearning.AI 专题课程标准化工程规范与自动化流水线

本 Skill 沉淀了 DeepLearning.AI 系列前沿硬核技术课程（如 LangGraph Agent Memory、Advanced RAG、Agentic RAG、Anthropic MCP 等）的完整标准化本地化与归档工程规范。覆盖了从原始音视频抓取、双语字幕分层渲染、神经网络口播配音、音画无损封装，到万字架构指南撰写的全生命周期。

---

## 一、 标准化目录与资产拓扑规范 (Directory & Asset Topology)

每个课程必须遵循完全统一的目录结构与命名规范：

```text
{Course_Root_Directory}/
├── 01_introduction/
│   ├── 01_introduction.mp4         # [必需] 原始 1080p 高清视频 (英文原声)
│   ├── 01_introduction_zh.mp4      # [标准] 中文配音版 (Track 0: 画面, Track 1: 中文配音, Track 2: 英文原声, Track 3: 双语字幕)
│   ├── 01_introduction.en.srt      # [必需] 纯英文字幕 (SRT)
│   ├── 01_introduction.en.vtt      # [必需] 纯英文字幕 (WebVTT)
│   ├── 01_introduction.zh.srt      # [必需] 精校纯中文字幕 (SRT)
│   ├── 01_introduction.zh.vtt      # [必需] 精校纯中文字幕 (WebVTT)
│   ├── 01_introduction.zh_en.srt   # [必需] 中英双语分层样式字幕 (SRT)
│   └── 01_introduction.zh_en.vtt   # [必需] 中英双语分层样式字幕 (WebVTT)
├── 02_{lesson_topic}/
│   └── ...
├── {course_stem}_summary.md        # [必需] 万字架构级课程实战指南与全景认知
├── export_subtitles.py             # [工程脚本] 4格式字幕批量导出与样式渲染
├── verify.py                       # [工程脚本] 视频与字幕完整性与句数对齐校验
└── dub_course.py                   # [工程脚本] 神经网络中文口播配音与双音轨封装
```

---

## 二、 4 格式字幕提取与分层渲染规范 (Subtitle Standards)

为满足不同播放终端（网页、本地播放器、移动端）的最佳阅读体验，每个章节必须一次性生成 **4 种标准化字幕文件**：

### 1. 中英双语分层字幕 (`.zh_en.srt`)
采用 HTML 标签实现主次分明的视觉层次：
```srt
1
00:00:02,000 --> 00:00:05,200
<font size="3">欢迎学习构建富上下文 AI 应用：模型上下文协议 MCP 与 Anthropic。</font>
<font size="2" color="#cccccc">Welcome to Building Rich-Context AI Applications with the Model Context Protocol and Anthropic.</font>
```
- **中文（首行）**：字号较大，高亮纯白，优先捕获注意力；
- **英文（次行）**：字号略小（`size="2"`），低对比度灰字（`color="#cccccc"`），作为专业对照与辅助。

### 2. WebVTT 双语字幕 (`.zh_en.vtt`)
标准 WebVTT 格式，内嵌 CSS 伪类与行内样式：
```vtt
WEBVTT
STYLE
::cue {
  font-size: 80%;
  line-height: 1.25;
}

1
00:00:02.000 --> 00:00:05.200
<small>欢迎学习构建富上下文 AI 应用：模型上下文协议 MCP 与 Anthropic。<br/><span style="color:#cccccc;font-size:85%">Welcome to Building Rich-Context AI Applications with the Model Context Protocol and Anthropic.</span></small>
```

### 3. 单语纯文本字幕 (`.zh.srt` 与 `.en.srt`)
纯净字幕文本，不含任何 HTML 标签，专供：
- 播放器内置单语字幕切换；
- 自动化 TTS 语音合成读取；
- 文本向量检索与 RAG 知识库切片。

---

## 三、 神经网络口播配音规范 (Neural TTS Dubbing Protocol)

利用微软 Edge Neural 神经网络语音引擎，将英文口播替换为自然流利的中文配音。

### 1. 核心音色标准
- **标准首选**：`zh-TW-YunJheNeural`（云哲，男声）—— 平缓低沉、现代自然，无新闻联播播音腔，长视频听感舒适；
- **备选活力男声**：`zh-CN-YunxiNeural`（云希，男声）—— 科技区 UP 主风格，轻快生活化；
- **备选知性女声**：`zh-CN-XiaoxiaoNeural`（晓晓，女声）—— 极具亲和力，吐字清晰细腻。

### 2. 智能连贯断句合并 (Smart Sentence Merging)
- 字幕为了屏幕行宽排版，常常将一句话拆分成 2~3 个短行（如 0.6 秒短片段）。
- 配音前必须进行**语义连贯合并**：当相邻字幕间隔 $< 0.25$ 秒且前句未出现句终标点（`。！？`）时，自动合并为完整自然句合成，保障语调起伏与意群完整。

### 3. 专业术语与生僻词发音校准 (Phonetic Dictionary)
- **讲师人名**：将外来生僻姓名（如 `Elie Schoppik`）口播为地道的 `Elie`，将 `Andrew` 口播为国内熟知的 `吴恩达老师`，消除机械拼读生硬感；
- **专有名词**：
  - `MCP` $\rightarrow$ 清晰单字母读音 `M C P`；
  - `LLM` $\rightarrow$ 读作 `大模型 LLM`；
  - `Claude Desktop` $\rightarrow$ 读作 `Claude 桌面端`；
  - 自动剥离字幕中仅供视觉参考的英文括号注释（如 `（Model Context Protocol）` $\rightarrow$ `即 MCP`）。

### 4. 动态弹性时间轴平滑对齐 (Dynamic Elastic Timeline)
- 计算每句合成音频时长与原视频时间槽；
- 允许借用微小气口停顿（$\pm 0.3$ 秒），语速自适应控制在 **`1.00x ~ 1.28x`** 黄金区间，坚决禁止超速失真或吞音；
- 讲师操作、演示切换与中文口播严密同步。

### 5. 无损多音轨封装 (Lossless Multi-track Muxing)
使用 FFmpeg 进行无损容器封装：
```bash
ffmpeg -y -i original.mp4 -i chinese.wav -i bilingual.srt \
  -map 0:v:0 -map 1:a:0 -map 0:a:0 -map 2:s:0 \
  -c:v copy \
  -c:a:0 aac -b:a:0 192k -metadata:s:a:0 title="中文口播 (云哲)" -metadata:s:a:0 language=chi \
  -c:a:1 copy -metadata:s:a:1 title="English (Original)" -metadata:s:a:1 language=eng \
  -c:s mov_text -metadata:s:s:0 title="中英双语字幕" -metadata:s:s:0 language=chi \
  -disposition:a:0 default -disposition:a:1 0 -disposition:s:0 default \
  output_zh.mp4
```
- **画面**：`-c:v copy` 保持原始 1080p 高清，0 编码耗时，0 画质损失；
- **音轨 1 (默认)**：中文普通话配音；
- **音轨 2**：保留原始英文原声，支持播放器一键切换；
- **字幕轨**：内嵌双语字幕。

---

## 四、 万字课程架构实战指南编写规范 (Architecture Guide Standards)

每个课程必须沉淀一份架构级 Markdown 文档（`{course_stem}_summary.md`），结构必须严格包含：

1. **课程核心认知体系与全景架构**：
   - 传统方案瓶颈剖析（如 Naive RAG 的分块两难、传统无记忆 Agent 的上下文丢失、M×N 碎片化接口泥潭）；
   - 范式跃迁全景图（Mermaid 流程图/状态机）；
2. **核心原语与关键组件对比表格**：
   - 三大记忆模型（语义/情景/程序）、三元评估指标（相关性/忠实度）、三大 MCP 原语（Tools/Resources/Prompts）的标准定义与映射；
3. **生产级核心代码实现**：
   - 真实可运行的代码片段，包含命名空间设计、状态流转、错误重试与持久化存储；
4. **工业级踩坑与最佳实践建议**：
   - 生产环境高并发、Token 预算控制、上下文窗口压缩等避坑策略。

---

## 五、 自动化辅助工具箱使用指南 (Scripts Runbook)

本 Skill 配套提供了三大自动化生产级脚本：

1. **导出与生成 4 格式字幕**：
   ```bash
   python3 scripts/export_subtitles.py --input raw_cues.json --output-dir ./01_introduction
   ```
2. **全自动神经网络中文配音**：
   ```bash
   # 处理单节
   python3 scripts/dub_course.py --lesson 01_introduction --voice zh-TW-YunJheNeural
   # 批量全量处理课程全集
   python3 scripts/dub_course.py --all --voice zh-TW-YunJheNeural
   ```
3. **自动化资产质检与句数校验**：
   ```bash
   python3 scripts/verify_assets.py --course-dir /path/to/course
   ```
