# DeepLearning.AI 课程端到端制作与多端发布指南

本指南整合自原 `deeplearn-vp-create` 技能，涵盖针对 DeepLearning.AI 课程从字幕提取、旁白翻译、HTML 故事板审阅、TTS 配音、Remotion 渲染到小红书 3:4 宣发图文卡片的端到端完整管线。

---

## 阶段一：提取原始字幕 (Phase 1)

**前提**：浏览器已登录 `learn.deeplearning.ai`。

1. 导航到目标课程页面（如 `/courses/ai-agents-in-langgraph/lesson/c1l2c/build-an-agent-from-scratch`）。
2. 在开发者工具 Console 执行以下代码提取字幕纯文本：

```javascript
(() => {
  const el = document.getElementById('__NEXT_DATA__');
  const data = JSON.parse(el.textContent);
  return data.props.pageProps.captions; // 纯文本字符串
})()
```

3. 每节课为独立 URL，需逐页导航提取。课程目录链接可通过 `document.querySelectorAll('a[href*="/lesson/"]')` 获取。

> **注意**：提取的 captions 是纯文本（无时间戳），需按语义分段。
>
> **浏览器超时恢复策略**：
> - 自动化浏览器工具超时（如 `V2 command timeout`）时，不要在同一 tab 反复重试；
> - 恢复步骤：新建 tab → 导航到目标页 → 重新执行；
> - 将大段脚本拆分执行，降低单次调用耗时。

---

## 阶段二：7 场景结构化翻译与旁白划分 (Phase 2)

将原始字幕按讲稿逻辑切分为标准的 7 个场景结构：

| 场景 | 内容 | 典型时长 |
|------|------|----------|
| 1 Intro | 标题卡 + 课程引入 | 18–20s |
| 2 核心概念 | 本课核心模式/概念图解 | 27–30s |
| 3 代码结构 | 第一段代码走读 | 28–30s |
| 4 提示词/工具 | 第二段代码走读 | 27–29s |
| 5 运行示例 | 执行 trace 展示 | 40–45s |
| 6 自动化/进阶 | 第三段代码走读 | 33–35s |
| 7 Outro | 总结 + 下集预告 + 系列导航 | 16–18s |

**翻译原则**：
- 忠实于讲师原话，口语化但不拟人化、不自由发挥；
- 每场景旁白按句切分为字幕行（每行 15–25 字）；
- 每场景旁白存为独立文件（如 `narration/epXX/s1.txt` ~ `s7.txt`）。

---

## 阶段三：HTML 故事板预览审阅门禁 (Phase 2.5)

**强制规则：渲染前必须生成 HTML 故事板供用户确认，确认后方可进入配音与渲染阶段。**

每课生成一个单文件 HTML（如 `preview/ep01-storyboard.html`），纵向卡片式排列所有场景帧：
- 场景编号与标题（如 "Scene 1 · Intro"）；
- 完整中文翻译旁白；
- 视觉描述（布局、动画、代码走读高亮说明）；
- 预估时长（秒）；
- 场景间提供清晰分隔线。

---

## 阶段四：TTS 配音与时长测量 (Phase 3)

**首选音色**：`zh-CN-YunyangNeural`（云扬，男声，新闻主播腔，专业稳重）。

```bash
python -m edge_tts --voice zh-CN-YunyangNeural --rate=+0% --file narration/ep01/s1.txt --write-media public/audio/ep01/s1.mp3
```

**音色备选**：
- `YunyangNeural`（男，专业，首选）
- `XiaoxiaoNeural`（女，温暖）/ `XiaoyiNeural`（女，活泼）
- `YunxiNeural`（男，阳光）/ `YunjianNeural`（男，激情）
- *注：部分音色可能返回 NoAudioReceived，生成前先 `--list-voices` 检查。*

**音频时长测量**：
- 独立安装 ffmpeg 直接探测：`ffprobe -v error -show_entries format=duration -of csv=p=0 audio.mp3`；
- Node v24 下 `npx remotion ffprobe` 可能报错，建议使用独立 ffmpeg 或 Node v20/v22 LTS。

---

## 阶段五：小红书 3:4 宣发图文卡片 (Phase 5)

除视频本身外，同步交付小红书竖版宣发图文套件：
- **尺寸**：1080×1440（3:4 竖版比例）；
- **标准 6 张套件**：
  1. 封面（爆款标题 + 讲师/主题视觉）；
  2. 核心概念图（架构/流程/思维导图）；
  3. 职责与逻辑拆解；
  4. 关键代码片段（高亮等宽语法块）；
  5. 金句与关键洞察；
  6. 系列导航与下期预告。
- **渲染实现**：在 Remotion 项目中注册 `durationInFrames=1` 的 1080×1440 Composition，直接通过 `npx remotion still` 渲染为静态 PNG。

---

## 多集批量工作流 (Batch Workflow)

发布编号规则：课程原始 lesson 编号 ≠ 发布集数。从第一个实质内容课开始编号为 `EP.01 + 标题`。

### 批量目录与音频初始化 (PowerShell 范例)

```powershell
1..7 | ForEach-Object {
    $ep = $_.ToString('00')
    New-Item -ItemType Directory -Force -Path "narration\ep$ep" | Out-Null
    New-Item -ItemType Directory -Force -Path "public\audio\ep$ep" | Out-Null
}
```

### 批量渲染命令

```bash
# 顺序执行渲染，避免并行打包冲突
for /L %i in (1,1,7) do npx remotion render src/index.ts Lesson0%i out/ep0%i.mp4 --codec=h264
```

---

## 常见踩坑与解决方案速查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `typescript.sys.readFile undefined` | TypeScript 7.x API 不兼容 | 锁定 `typescript@5.8` |
| esbuild 语法报错 | 中文字符/引号嵌套在 JS 双引号内 | 字符串字面量外层改用单引号 `'...'` |
| edge-tts 报 `NoAudioReceived` | 目标音色在服务节点临时不可用 | 先通过 `--list-voices` 确认在线音色 |
| PowerShell 变量 `$` 被 bash 误吞 | bash 先行转义变量 | 将脚本写入 `.ps1` 文件或用 `cmd.exe /c` 执行 |
| Remotion 进程锁或 bundle 冲突 | 多进程并发调用 | 顺序执行各集渲染，不盲目并发 |
