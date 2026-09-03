---
name: deeplearn-vp-create
description: 从 DeepLearning.AI 课程提取字幕、翻译为中文、用 Remotion 生成带中文字幕和云扬配音的教学视频及小红书图文卡片。当用户提到 DeepLearning.AI 课程搬运、课程视频制作、Remotion 教学视频、课程翻译配音时使用。
version: 1.1.0
---

# DeepLearning.AI 课程视频制作流程

## 总览

完整流水线：提取原始字幕 → 翻译分场景旁白 → **HTML 故事板预览审阅** → edge-tts 生成配音 → Remotion 渲染视频（中文字幕+动画联动）→ 小红书卡片 PNG。

**多集模式**：每课独立一条视频（EP.01~EP.N），不做单条总览。

## Phase 1：提取原始字幕

**前提**：浏览器已登录 learn.deeplearning.ai。

1. 导航到目标课程页面（如 `/courses/ai-agents-in-langgraph/lesson/c1l2c/build-an-agent-from-scratch`）
2. 用浏览器 JS 工具执行：

```javascript
(() => {
  const el = document.getElementById('__NEXT_DATA__');
  const data = JSON.parse(el.textContent);
  return data.props.pageProps.captions; // 纯文本字符串
})()
```

3. 每节课独立 URL，需逐页导航提取。课程目录链接可通过 `document.querySelectorAll('a[href*="/lesson/"]')` 获取。

**注意**：返回的 captions 是纯文本（无时间戳），需按内容语义分段。

**浏览器超时恢复策略**：
- 浏览器 JS 工具超时时（报 `V2 command timeout: tools/invoke`），不要反复重试同一 tab
- 恢复步骤：`tabs_create` 新建 tab → `navigate` 到目标页 → 重新执行 JS
- 大段 JS 拆分为小步骤（先获取 DOM 结构，再提取数据），降低单次执行时间
- 若连续超时 2 次，先 `tabs_context` 检查 tab 状态，关闭异常 tab 再重建

## Phase 2：翻译 + 分场景旁白

将原始字幕按讲稿逻辑分为 7 个场景（跟随讲稿结构，非自由发挥）：

| 场景 | 内容 | 典型时长 |
|------|------|----------|
| 1 Intro | 标题卡 + 课程引入 | 18-20s |
| 2 核心概念 | 本课核心模式/概念图解 | 27-30s |
| 3 代码结构 | 第一段代码走读 | 28-30s |
| 4 提示词/工具 | 第二段代码走读 | 27-29s |
| 5 运行示例 | 执行 trace 展示 | 40-45s |
| 6 自动化/进阶 | 第三段代码走读 | 33-35s |
| 7 Outro | 总结 + 下集预告 + 系列导航 | 16-18s |

**翻译原则**：忠实于讲师原话，口语化但不拟人化/不自由发挥。每场景旁白按句切分为字幕行（每行 15-25 字）。

每场景旁白存为独立 txt 文件（`narration/epXX/s1.txt` ~ `s7.txt`）。

## Phase 2.5：HTML 故事板预览（必须）

**渲染前必须先生成 HTML 故事板供用户审阅，用户确认后再进入配音/渲染阶段。**

每课生成一个 HTML 文件（如 `preview/ep01-storyboard.html`），包含该课所有场景帧，纵向排列方便滚动审阅。

每个场景帧包含：
- 场景编号与标题（如 "Scene 1 · Intro"）
- 旁白文本（完整中文翻译）
- 视觉描述（布局、动画、代码内容概述）
- 预估时长（秒）
- 场景间用分隔线区隔

样式要求：简洁白底、卡片式布局、场景间有明显分隔线（注意 `.divider` 宽度不要溢出容器）。

用户审阅通过后，再进入 Phase 3 配音生成。

## Phase 3：配音生成

**工具**：`python -m edge_tts`（Scripts 目录不在 PATH，必须用 `python -m` 调用）

**Python 路径注意**：
- 若 `python` 不在系统 PATH（常见于 Windows），需用完整路径调用，如 `C:\Python314\python.exe -m edge_tts`
- bash 环境下 Windows 路径反斜杠会被转义，推荐用 `cmd.exe /c "C:\Python314\python.exe -m edge_tts ..."` 或写 `.ps1` 脚本文件执行
- 首次使用需先安装：`C:\Python314\python.exe -m pip install edge-tts`

**音色**：`zh-CN-YunyangNeural`（云扬，男声，新闻主播腔，专业稳重）

```bash
cmd.exe /c "C:\Python314\python.exe -m edge_tts --voice zh-CN-YunyangNeural --rate=+0% --file narration/ep01/s1.txt --write-media public/audio/ep01/s1.mp3"
```

**可用音色**（用 `python -m edge_tts --list-voices | grep zh-CN` 确认）：
- XiaoxiaoNeural（女，温暖）/ XiaoyiNeural（女，活泼）
- YunyangNeural（男，专业）✓ 首选 / YunxiNeural（男，阳光）/ YunjianNeural（男，激情）

**坑**：XiaochenNeural、XiaohanNeural 等部分音色会返回 NoAudioReceived，生成前先 `--list-voices` 确认。

**测时长**：

`npx remotion ffprobe` 在 Node v24 下会报 `Class extends value undefined is not a constructor or null`，需用替代方案：

- **方案 A（推荐）**：独立安装 ffmpeg，直接调用 `ffprobe.exe -v error -show_entries format=duration -of csv=p=0 audio.mp3`
- **方案 B**：写 PowerShell 脚本获取时长：
  ```powershell
  Add-Type -AssemblyName PresentationCore
  $f = [System.Windows.Media.MediaPlayer]::new()
  $f.Open([Uri]::new("E:\path\to\audio.mp3"))
  Start-Sleep -Milliseconds 500
  $f.NaturalDuration.TimeSpan.TotalSeconds
  ```
- **方案 C**：降级 Node 到 v20/v22 LTS 后 `npx remotion ffprobe` 可正常使用

## Phase 4：Remotion 项目

### 环境要求

- Node.js 18+（v20/v22 LTS 最稳定；v24 可用但 Remotion CLI 的 ffprobe 子命令有兼容问题）
- **TypeScript 必须 5.x**（7.x 与 Remotion bundler 的 esbuild-loader 不兼容，报 `typescript.sys.readFile undefined`）
- 依赖：`remotion @remotion/cli @remotion/transitions react react-dom typescript@5.8`

### 项目结构（多集模式）

```
video/
├── src/
│   ├── index.ts              # registerRoot
│   ├── Root.tsx              # 注册所有 Composition（Lesson01~Lesson07）
│   ├── theme.ts              # 设计 token + 场景时长
│   ├── subtitles.ts          # 字幕数据 + 时长计算
│   ├── Lesson01/index.tsx    # EP.01 TransitionSeries 主合成
│   ├── Lesson02/index.tsx    # EP.02 ...
│   ├── components/
│   │   ├── animations.tsx    # FadeIn/SlideInLeft/PopIn/Typewriter/SceneHeader/Watermark
│   │   ├── Subtitles.tsx     # 底部字幕条组件
│   │   └── CodePanel.tsx     # 代码面板（macOS 风格标题栏 + 语法高亮行）
│   ├── scenes/               # 7 个场景组件（可跨集复用）
│   └── cards/                # 小红书卡片组件（1080×1440）
├── public/audio/
│   ├── ep01/                 # 每课独立音频目录
│   ├── ep02/
│   └── ...
├── narration/
│   ├── ep01/                 # 每课独立旁白目录
│   ├── ep02/
│   └── ...
└── preview/                  # HTML 故事板预览文件
    ├── ep01-storyboard.html
    └── ...
```

### 设计规范

```typescript
THEME = {
  bg: "#FAFBFC",        // 浅灰白背景
  text: "#1A2332",      // 深蓝黑主文字
  accent: "#0D9488",    // teal-600 强调色
  secondary: "#64748B", // slate 次要文字
  codeBg: "#1E293B",    // 代码区深底
  codeText: "#E2E8F0",  // 代码区浅字
  blue: "#2563EB",      // LLM 标签色
}
```

- 分辨率：1920×1080 / 30fps
- 字体：微软雅黑（正文）+ Cascadia Code（代码）
- 水印：仅左下角 `AI Agents in LangGraph · EP.XX`
- 字幕：中文-only，底部深色半透明条，按句淡入淡出

### 场景时长计算

```
场景帧数 = 音频秒数 × 30 + 约 60 帧缓冲（2s）
总帧数 = Σ场景帧数 - (场景数-1) × 转场帧数(15)
```

### 字幕时间轴

按字符数比例分配到音频时长上（中文 TTS 语速近似恒定）：

```typescript
function computeSubtitleTiming(lines: string[], audioSeconds: number) {
  const audioFrames = audioSeconds * 30;
  const totalChars = lines.reduce((s, l) => s + l.length, 0);
  let cursor = 0;
  return lines.map(line => {
    const dur = (line.length / totalChars) * audioFrames;
    const result = { text: line, start: cursor - 6, end: cursor + dur };
    cursor += dur;
    return result;
  });
}
```

### 动画与旁白联动

- ReAct 流程图：节点在旁白讲到"思考/行动/观察"时依次点亮（spring 动画）
- 代码面板：行逐行出现（interpolate opacity），高亮行用 teal 背景
- 双栏布局：工具栏在旁白讲到工具时才 FadeIn（delay 对齐字幕时间）

### 渲染命令

```bash
# 单集视频
npx remotion render src/index.ts Lesson01 out/ep01.mp4 --codec=h264

# 批量渲染（顺序执行，不并行，文件名称叫epxx-{title}）
for /L %i in (1,1,7) do npx remotion render src/index.ts Lesson0%i out/ep0%i{title}.mp4 --codec=h264

# 单帧（调试）
npx remotion still src/index.ts Lesson01 out/frame.png --frame=200

# 小红书卡片（1080×1440 静态 Composition）
npx remotion still src/index.ts Card1 out/xhs-card-1.png
```

## Phase 5：小红书卡片

- 尺寸：1080×1440（3:4 竖版）
- 张数：6 张（封面 / 核心概念图 / 职责或代码 / 代码片段 / 金句洞察 / 系列导航）
- 实现：同一 Remotion 项目内注册 1080×1440 的 Composition，`durationInFrames=1`，渲染 still PNG
- 风格与视频统一（同色板、同字体、同水印）

## 发布编号规则

- 课程原始 lesson 编号 ≠ 发布集数
- 从第一个实质课程开始编号为 EP.01 + 标题
- 例：课程 lesson02（Build an Agent from Scratch）= 发布 EP.01

## 多集批量工作流

每课独立一条视频（EP.01~EP.N），完整流程：

1. **批量提取字幕**：逐课导航提取（Phase 1），每课存为 `captions/epXX.txt`
2. **批量翻译旁白**：每课 7 个场景文件，存入 `narration/epXX/s1.txt ~ s7.txt`
3. **批量生成故事板**：每课一个 HTML 预览文件，提交用户审阅（Phase 2.5）
4. **用户确认后**，批量生成 TTS 配音（Phase 3）
5. **构建 Remotion 源码**：每课一个 `LessonXX/index.tsx`，在 `Root.tsx` 中注册所有 Composition
6. **顺序渲染**：逐集渲染视频，不并行（避免 bundle 冲突）
7. **小红书卡片**：每课 6 张或全系列统一封面

批量目录创建推荐用 PowerShell 脚本：
```powershell
1..7 | ForEach-Object {
    $ep = $_.ToString('00')
    New-Item -ItemType Directory -Force -Path "narration\ep$ep" | Out-Null
    New-Item -ItemType Directory -Force -Path "public\audio\ep$ep" | Out-Null
}
```

## 踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| `typescript.sys.readFile undefined` | TS 7.x API 变更 | 降级 `typescript@5.8` |
| esbuild 报 `Expected "}" but found "xxx"` | 中文引号 `"..."` 嵌套在 JS 双引号字符串内 | 外层改用单引号 `'...'` |
| bash `for i in ...; do ... $i ...` 失败 | Win 环境 bash 变量展开问题 | 逐条执行或用 `&&` 串联 |
| edge-tts 返回 NoAudioReceived | 部分音色在当前服务不可用 | 先 `--list-voices` 确认 |
| 系统无 ffprobe | 未单独安装 ffmpeg | 用 `npx remotion ffprobe` 替代（Node v22 以下） |
| edge-tts 命令找不到 | Scripts 目录不在 PATH | 用 `python -m edge_tts` |
| Remotion still 批量渲染 | 多进程同时 bundle 可能冲突 | 顺序执行，不并行 |
| `python` 命令找不到 | Python 安装在 `C:\Python314\`，未加入 PATH | 用完整路径 `C:\Python314\python.exe`，通过 `cmd.exe /c` 调用避免 bash 路径转义 |
| `npx remotion ffprobe` 报 `Class extends value undefined` | Node v24 与 Remotion CLI 内置 ffprobe 不兼容 | 独立安装 ffmpeg 直接调用 `ffprobe.exe`；或写 PowerShell 脚本获取时长；或降级 Node 到 v20/v22 |
| 浏览器 JS 工具频繁超时（`V2 command timeout`） | 页面 JS 执行时间过长或 tab 状态异常 | 关闭当前 tab → `tabs_create` 新建 tab → `navigate` 重新导航 → 重试；大段 JS 拆分为小步骤 |
| PowerShell 脚本中 `$` 变量被 bash 吞掉 | bash 先于 PowerShell 解释 `$` | 将 PowerShell 代码写入 `.ps1` 文件再执行，或用 `cmd.exe /c` 包裹 |

## 用户偏好备忘

- 配音：云扬男声，语速 +0%，不拟人化，忠实翻译风格
- 字幕：中文-only（不要中英双语）
- 水印：仅左下角
- 旁白内容：基于原始字幕翻译，不自由发挥
- 多集模式：每课独立一条视频（EP.01~EP.N），不做单条总览
- 审阅流程：先出 HTML 故事板预览 → 用户确认 → 再配音渲染
- 工作流：先出分镜脚本 markdown 供审阅 → 确认后渲染
- 产出保存：当前项目目录，独立文件夹存储，或由用户指定

## 待补充内容与规划 (TODO / Backlog)

> [!NOTE]
> 本技能包含详尽的实战流程与避坑记录，以下自动化与工程脚本建议后续补充沉淀：

- [ ] **字幕提取脚本库**：封装无头浏览器一键提取多课字幕的自动化脚本（如 `scripts/extract_captions.js`）。
- [ ] **批量配音与时长计算脚本**：提供 PowerShell/Python 一键批量调用 edge-tts 并自动输出音频时长的通用脚本（如 `scripts/batch_tts.py`）。
- [ ] **HTML 故事板通用预览器**：提取一套独立的纯前端 HTML 故事板预览模板（如 `templates/storyboard_preview.html`）。
- [ ] **Remotion 起步脚手架**：提供预置好的 7 场景模版与小红书 3:4 卡片模版的 Remotion 最小化种子工程。
