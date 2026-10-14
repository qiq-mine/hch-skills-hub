# DeepLearning.AI Course Localization Engineering Standards

## 1. Subtitle Technical Specifications

- **SRT File Encoding**: UTF-8 without BOM. Line breaks: LF (`\n`).
- **Timing Accuracy**: Millisecond-level precision (`00:00:00,000 --> 00:00:00,000`).
- **Bilingual Font Styling**:
  - Primary (Chinese): `<font size="3">...</font>`
  - Secondary (English): `<font size="2" color="#cccccc">...</font>`
- **WebVTT Styling**:
  - `WEBVTT` header with CSS: `::cue { font-size: 80%; line-height: 1.25; }`
  - Body: `<small>{zh}<br/><span style="color:#cccccc;font-size:85%">{en}</span></small>`

## 2. Audio & Video Dubbing Specifications

- **Audio Sample Rate**: 48,000 Hz (48 kHz).
- **Audio Channels**: 2 Channels (Stereo).
- **Audio Codec**: AAC-LC.
- **Audio Bitrate**: 192 kbps.
- **Video Packaging**: Direct copy (`-c:v copy`), MP4 container (`isom/mp42`).
- **Track Layout**:
  - Stream 0 (Video): H.264 original stream (und/eng)
  - Stream 1 (Audio, Default): Chinese Neural TTS (`chi`)
  - Stream 2 (Audio, Secondary): Original English stream (`eng`)
  - Stream 3 (Subtitle, Default): Bilingual subtitle track (`chi`, `mov_text`)

## 3. Neural TTS Voice Reference

| Voice Identifier | Gender | Characteristics | Recommended Usage |
| :--- | :--- | :--- | :--- |
| `zh-TW-YunJheNeural` | Male | Calm, natural, modern, non-broadcast | Default for all developer courses |
| `zh-CN-YunxiNeural` | Male | Lively, tech vlogger style | Interactive demos, lightweight courses |
| `zh-CN-XiaoxiaoNeural` | Female | Warm, clear, academic | Tutorials requiring patient explanation |
| `zh-CN-YunyangNeural` | Male | News broadcast, formal | Documentary, formal announcements |

## 4. Phonetic & Lexical Mapping Table

| Source Expression | Pronunciation / Spoken Form | Rationale |
| :--- | :--- | :--- |
| `Andrew` | 吴恩达老师 | Well-recognized by Chinese developers |
| `Elie Schoppik` | Elie | Avoids TTS phonetic stumbling on rare surnames |
| `Claude Desktop` | Claude 桌面端 | Standard Chinese community naming |
| `大语言模型（LLM）` | 大模型 LLM | Eliminates repetitive tongue twister |
| `MCP` | M C P | Ensures discrete letter articulation |
| `FastMCP` | Fast M C P | Preserves distinct phonetic boundaries |
