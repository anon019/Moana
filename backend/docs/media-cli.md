# ChatGPT CLI 与 Fish 在线语音

默认文本、附图分析使用已登录 ChatGPT 的 Codex CLI `gpt-6-luna`。图片由 CLI 的 `image_generation` 工具生成，请求型号为 `gpt-image-2.5-sunburst`。此型号是请求参数，工具没有回传底层型号时，实际来源记录为 `not_exposed_by_tool`，不能将请求参数当成已验证的实际型号。

语音使用 Fish Audio 在线托管模型 `s2.1-pro-free`，通过短生命周期 Python CLI 请求；不下载、不运行本地语音模型。视频暂时停用。Gemini、Vertex、Imagen、Veo 的共享客户端在读取凭据和建立连接前抛错；网关中的 Google/Gemini 路由也被拒绝。旧文本 provider 别名会映射到 Codex，旧 Google 媒体 provider 会明确报错。

## 配置与认证

安装 Python 项目依赖、FFmpeg 及支持 `image_generation` 的 Codex CLI，使用运行后端的同一用户执行 `codex login`。代码忽略 CLI 用户规则和配置，强制使用 ChatGPT 登录，不向子进程转发各家模型的 API Key。文本 CLI 禁用工具，图片 CLI 仅启用图片生成。

复制 `.env.example` 后，默认配置为：

```dotenv
LLM_PROVIDER=codex
CODEX_MODEL=gpt-6-luna
CODEX_TIMEOUT=180
IMAGE_PROVIDER=codex
CODEX_IMAGE_MODEL=gpt-image-2.5-sunburst
CODEX_IMAGE_TIMEOUT=240
CODEX_IMAGE_ISOLATE=true
TTS_PROVIDER=fish_free_cli
TTS_CLI_TIMEOUT=120
VIDEO_PROVIDER=disabled
```

`CODEX_BIN` 可指定 Codex 可执行文件。`TTS_CLI_PYTHON` 默认当前 Python 解释器；它只运行标准库 HTTP worker。`STORAGE_LOCAL_PATH` 默认 `./media`，部署时应配置可写路径和对应的 `STORAGE_BASE_URL`。

在终端执行以下命令，隐藏输入 Fish Key 并原子保存到 `.env`（权限 `0600`）：

```bash
python3 scripts/configure_fish_audio.py
```

不要把 Key 写进命令参数、Git 或聊天记录。修改配置后需重启后端。默认中文声音为公开音色“配音3”，ID 为 `cfe763b758ea496882bfae05808eb0c1`，可用 `FISH_SPEECH_VOICE_ID` 指定其他 32 位十六进制音色。旧客户端的 Kore 等历史预设会映射到配置音色；新生成结果记录实际 Fish 音色。试听只返回已经存在的预览文件，不在查询选项时产生合成请求。

## 免费期限与失败行为

Fish 请求固定发送 `model: s2.1-pro-free` 到 `https://api.fish.audio/v1/tts`，禁止重定向、不自动重试、不回退到收费型号。按照此次迁移核验的[Fish 官方免费政策](https://fish.audio/blog/s2-1-pro-free-api/)，代码在 **2026-12-01 00:00 UTC（北京时间 08:00）** 起拒绝新请求；后续需重新核实官方政策再决定是否调整。已有素材仍可播放和复用。免费服务仍可能有额度、并发限制或临时不可用。

Fish Key、音色和免费期限会在新绘本生成故事前校验。生成失败保留部分稿件；图片可按既有有限次数重试，语音修复只调用当前 Fish 服务。不要恢复旧批处理队列来验证配置。

## 资源与结果校验

图片任务通过独立的 Linux systemd transient unit 执行，设置 `MemoryMax=384M`、`CPUQuota=50%`、`TasksMax=96` 和运行超时，调用用户须有创建、停止该 unit 的权限。默认不在 API 进程所在 cgroup 内直接运行图片 CLI。开始前要求至少 384 MiB 可用内存，执行期间低于 256 MiB 则停止。图片与 Fish 使用跨进程锁串行执行；原有批次的 256 MiB/32 tasks 限额不能代替图片 worker 的独立限额。

只有本次成功会话目录下的有效 PNG 能被导入；失败事件、缺少完成事件、越界路径、符号链接和超限图片均被拒绝。取消、超时或内存检查失败会清理 worker。Fish 流式响应有字节上限，并验证 WAV 后转码为 MP3。

缓存签名须包含实际影响结果的提示词、风格、负面提示词、音色、语速及模型。历史素材只保留已记录的来源，未知记录标为 `unknown`；单页修复记录该页的实际模型及音色，不覆盖其他历史页的来源。

## 离线回归

以下测试使用模拟 CLI/HTTP，不发起真实生成：

```bash
pytest -q tests/services/test_codex_text.py tests/services/test_codex_image.py \
  tests/services/test_tts_cli.py tests/services/test_configure_fish_audio.py \
  tests/services/test_google_disabled.py tests/api/test_content_voice_migration.py \
  tests/pipelines/test_picture_book.py tests/services/test_audio_converter_lifecycle.py
```

生产密钥、生成素材、私有批次计划及运维日志不属于公开同步范围。
