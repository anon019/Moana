# Moana - AI 原生早教内容生成平台

<p align="center">
  <img width="2816" height="1536" alt="Gemini_Generated_Image_9fsv0b9fsv0b9fsv" src="https://github.com/user-attachments/assets/5a406c66-89e9-4158-bd83-9fa55122d1ff" />
</p>

<p align="center">
  <strong>为 1-6 岁儿童打造的 AI 个性化教育内容生成系统</strong>
</p>

<p align="center">
  <a href="#核心功能">核心功能</a> •
  <a href="#技术架构">技术架构</a> •
  <a href="#快速开始">快速开始</a> •
  <a href="#配置说明">配置说明</a> •
  <a href="#项目结构">项目结构</a>
</p>

---

## 项目简介

Moana 是一个 **AI 原生** 的早期教育内容生成平台，专为 1-6 岁儿童设计。项目采用 monorepo 结构，包含公开的后端代码、后台 Web 前端，以及微信小程序前端。系统能够根据孩子的年龄、兴趣和教育需求，自动生成个性化绘本、原创儿歌和教育视频，并记录播放历史、互动数据与学习统计。

### 为什么选择 Moana？

- **个性化内容**：根据孩子的年龄（月龄）和教育主题自动调整内容难度和风格
- **多模态生成**：支持绘本、儿歌、视频三类核心内容
- **AI 智能创作**：通过自然语言描述生成完整内容与配套素材
- **学习行为追踪**：记录播放、答题互动与学习统计，支持报告页展示
- **可配置部署**：运行时域名、回调地址、存储地址全部通过环境变量配置

---

## 核心功能

### 📚 AI 绘本生成

为孩子生成图文并茂的个性化绘本故事。

- **6 大主题分类**：习惯养成、认知启蒙、情感成长、冒险探索、社交能力、节日故事
- **100+ 教育话题**：涵盖刷牙、分享、认识颜色、勇敢面对等具体场景
- **30+ 艺术风格**：从皮克斯 3D 到水彩、国画、剪纸等多种风格
- **多主角配置**：支持不同动物主角、配色和配饰组合
- **TTS 配音**：支持为绘本和故事内容生成语音朗读

### 🎵 AI 儿歌创作

生成原创儿歌，包含歌词、旋律和音频输出。

- **多种音乐风格**：欢快、温馨、摇篮曲、教育向等
- **主题化歌词生成**：围绕教育场景生成适龄内容
- **多提供商支持**：可切换 Suno、MiniMax 等音乐服务

### 🎬 AI 视频生成

将绘本或提示词转化为动态视频内容。

- **两种创作模式**：基于绘本生成，或直接根据描述生成
- **多时长和分辨率配置**：通过后端配置切换不同视频参数
- **风格一致性**：保持与绘本或主题内容一致的视觉表达

### 🧒 孩子档案与内容库

- 支持多孩子档案
- 根据月龄推荐内容和主题
- 支持播放历史、内容库与基础偏好管理

### 📊 学习报告与播放追踪

- 内容播放记录
- 互动答题记录
- 学习时长、连续学习天数、主题偏好等统计
- 后台 Web 报表页展示学习数据

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端                                   │
├──────────────────────────┬──────────────────────────────────────┤
│       微信小程序          │       Web 管理后台 (Vue 3)           │
└──────────────────────────┴──────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI 后端服务                             │
├─────────────────────────────────────────────────────────────────┤
│  API 层    │  业务逻辑层  │  Pipeline 层  │  Service 层          │
│  ────────  │  ──────────  │  ───────────  │  ────────────        │
│  auth      │  agents/     │  picture_book │  llm/                │
│  content   │  - intent    │  nursery_rhyme│  image/              │
│  child     │  - planner   │  video        │  tts/                │
│  play      │  - story     │  standalone   │  music/              │
│  library   │  - review    │               │  video/              │
│  feedback  │              │               │  storage/            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AI 服务集成                                │
├─────────────────────────────────────────────────────────────────┤
│  LLM          │  图像生成      │  TTS         │  音乐/视频        │
│  ────────     │  ──────────    │  ────────    │  ────────────     │
│  OpenRouter   │ Gemini Nano Banana │  Gemini TTS  │  Suno / MiniMax   │
│  Gemini       │  通义万相      │  Qwen TTS    │  Google Veo 3.1   │
│  Claude       │  MiniMax       │  MiniMax TTS │  万相视频         │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       基础设施                                   │
├─────────────────────────────────────────────────────────────────┤
│ PostgreSQL (业务数据) │ Local / OSS (媒体存储) │ Env Config │
└─────────────────────────────────────────────────────────────────┘
```

### 技术栈详情

| 模块 | 技术选型 |
|------|----------|
| **后端框架** | Python 3.11+, FastAPI, Pydantic |
| **数据库** | PostgreSQL + SQLAlchemy (async) |
| **数据库迁移** | Alembic |
| **小程序前端** | 微信小程序 |
| **Web 前端** | Vue 3 + TypeScript + Tailwind CSS + ECharts |
| **构建工具** | Vite |
| **媒体存储** | 本地存储 / 阿里云 OSS |

### AI 服务配置

| 类别 | 首选服务 | 备选服务 | 环境变量 |
|------|----------|----------|----------|
| **图片生成** | Gemini Nano Banana (`gemini-3.1-flash-image-preview`) / 通义万相 | MiniMax、Flux | `IMAGE_PROVIDER` |
| **儿歌生成** | Suno V5 | MiniMax Music 2.0 | `MUSIC_PROVIDER` |
| **视频生成** | Google Veo 3.1 / 阿里云万相 | MiniMax Hailuo | `VIDEO_PROVIDER` |
| **LLM** | OpenRouter | Gemini、Claude | `LLM_PROVIDER` |
| **TTS 语音** | Gemini TTS / Qwen TTS | MiniMax、Fish Speech | `TTS_PROVIDER` |

---

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+（Web 前端）
- 微信开发者工具（小程序开发）

### 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 安装依赖
pip install -e ".[dev]"

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入数据库、Provider 密钥和运行时 URL

# 4. 运行数据库迁移
alembic upgrade head

# 5. 启动开发服务器
uvicorn moana.main:app --reload
```

详细后端说明见：

- `backend/README.md`
- `backend/alembic/README`

### Web 管理后台

```bash
# 1. 进入 Web 目录
cd backend/web

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

说明：

- `VITE_API_URL` 可直接指定后端 API 基础地址
- 本地开发时可使用 `VITE_DEV_PROXY_TARGET` 指向本地后端
- 公开代码默认不提交生产域名

### 微信小程序

1. 打开微信开发者工具
2. 导入 `miniprogram` 目录
3. 配置小程序 AppID 和本地开发参数
4. 将 API 地址配置为你的后端部署地址

---

## 配置说明

### 必需的后端配置

在 `backend/.env` 中至少配置以下内容：

```bash
# 数据库连接
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/moana

# Provider keys
OPENROUTER_API_KEY=your_openrouter_api_key
GOOGLE_API_KEY=your_google_api_key
GEMINI_IMAGE_MODEL=gemini-3.1-flash-image-preview
SUNO_API_KEY=your_suno_api_key
DASHSCOPE_API_KEY=your_dashscope_api_key
MINIMAX_API_KEY=your_minimax_api_key

# Runtime URLs
STORAGE_BASE_URL=http://localhost:8080/media
CALLBACK_BASE_URL=http://localhost:8080
ALLOWED_CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
OPENROUTER_SITE_URL=http://localhost:3000
```

原则：

- 不要把生产域名、密钥或私有地址提交到仓库
- 图片生成默认链路使用 Gemini，模型为 `gemini-3.1-flash-image-preview`（代码注释标为 Nano Banana）
- 存储地址、回调地址、CORS 白名单全部通过环境变量配置
- 公开仓库中的默认值仅用于本地开发示例

### Provider 切换

系统支持运行时切换不同的 AI 服务提供商：

```bash
# LLM 提供商: openrouter | gemini | claude
LLM_PROVIDER=openrouter

# 图像生成: gemini | wanx | minimax | flux
IMAGE_PROVIDER=gemini

# 语音合成: gemini | qwen | minimax | fish_speech
TTS_PROVIDER=gemini

# 音乐生成: suno | minimax
MUSIC_PROVIDER=suno

# 视频生成: veo | wanx | minimax
VIDEO_PROVIDER=veo
```

---

## 项目结构

```
Moana/
├── README.md                    # 仓库根说明
├── .gitignore                   # 仓库级忽略规则
│
├── backend/                     # 后端与后台 Web
│   ├── README.md                # 后端详细说明
│   ├── .env.example             # 环境变量模板
│   ├── alembic/                 # 数据库迁移
│   ├── src/moana/               # 后端核心代码
│   ├── tests/                   # 后端测试
│   └── web/                     # Vue 后台 Web 前端
│
└── miniprogram/                 # 微信小程序前端
```

---

## API 文档

启动后端服务后，可访问自动生成的接口文档：

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

如使用自定义端口，请按实际启动地址访问。

### 主要 API 模块

| 模块 | 路径前缀 | 描述 |
|------|----------|------|
| `auth` | `/api/v1/auth` | 登录、令牌刷新 |
| `child` | `/api/v1/child` | 孩子档案与设置 |
| `content` | `/api/v1/content` | 内容生成与管理 |
| `play` | `/api/v1/play` | 播放历史、互动记录、学习统计 |
| `library` | `/api/v1/library` | 内容库 |

---

## 开发指南

### 添加新的艺术风格

1. 在 `backend/src/moana/styles/__init__.py` 中定义风格
2. 在相关服务或提示词模块中补充生成逻辑
3. 在 `miniprogram/` 或 `backend/web/` 中补充对应的 UI 选项

### 添加新的教育主题

1. 在 `backend/src/moana/themes.py` 中定义主题
2. 在前端入口补充对应的选择项与展示逻辑

### 集成新的 AI 服务

1. 在 `backend/src/moana/services/` 下创建新的服务模块
2. 实现对应的 base 类接口
3. 在 `backend/src/moana/config.py` 中添加配置项

---

## 运行测试

```bash
cd backend

# 运行所有测试
pytest

# 运行 play API 回归测试
pytest tests/api/test_play.py -q
```

---

## 部署

### 生产环境建议

1. 使用 Gunicorn + Uvicorn workers 运行 FastAPI
2. 配置 Nginx 或其他网关做反向代理
3. 启用 HTTPS
4. 使用 PostgreSQL 连接池与定期备份
5. 将域名、回调地址和 CORS 白名单放在环境变量中维护

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request。提交 PR 前请确认：

1. 代码通过相关测试
2. 遵循现有代码风格
3. 更新相关文档
4. 不提交敏感信息、私有域名或本地素材数据

---

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
