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

Moana 是一个 **AI 原生** 的早期教育内容生成平台，专为 1-6 岁儿童设计。通过先进的多模态 AI 技术，系统能够根据每个孩子的年龄、兴趣和教育需求，自动生成个性化的绘本故事、原创儿歌和教育视频。

### 为什么选择 Moana？

- **个性化内容**：根据孩子的年龄（月龄）和教育主题自动调整内容难度和风格
- **多种艺术风格**：支持 30+ 种艺术风格，从皮克斯 3D 到水彩、国画等
- **AI 智能创作**：只需用自然语言描述需求，AI 自动理解并生成完整内容
- **寓教于乐**：涵盖习惯养成、认知启蒙、情感成长等六大教育主题

---

## 核心功能

### 📚 AI 绘本生成

为孩子生成图文并茂的个性化绘本故事。

- **6 大主题分类**：习惯养成、认知启蒙、情感成长、冒险探索、社交能力、节日故事
- **100+ 教育话题**：涵盖刷牙、分享、认识颜色、勇敢面对等具体场景
- **30+ 艺术风格**：
  - 3D 风格：皮克斯、迪士尼、梦工厂、粘土、手办
  - 插画风格：水彩、蜡笔、彩铅、扁平
  - 动漫风格：日漫、吉卜力、新海诚、Q版萌系
  - 艺术风格：油画、印象派、水墨画、波普艺术
  - 手工风格：剪纸、折纸、不织布、刺绣
- **9 种主角形象**：小兔子、小熊、小猫咪、熊猫、小狐狸等
- **智能 TTS 配音**：多种音色可选，自然流畅的故事朗读

### 🎵 AI 儿歌创作

生成原创儿歌，包含歌词和配乐。

- **多种音乐风格**：欢快、温馨、摇篮曲、教育向等
- **自定义歌词主题**：根据教育场景生成相关歌词
- **AI 作曲配乐**：使用 Suno 或 MiniMax 音乐模型生成原创旋律

### 🎬 AI 视频生成

将静态绘本转化为动态视频内容。

- **两种创作模式**：
  - 基于绘本：将已生成的绘本转化为视频
  - 独立创作：直接根据描述生成视频
- **多种时长**：支持 5/6/8 秒视频片段
- **风格一致性**：保持与绘本相同的艺术风格

### 🧒 孩子档案管理

- 支持多孩子档案
- 根据月龄智能推荐内容
- 播放历史和收藏管理

### 📊 学习报告

- 内容播放统计
- 主题偏好分析
- 学习进度追踪

---

## 技术架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端                                   │
├──────────────────────────┬──────────────────────────────────────┤
│   微信小程序 (uni-app)    │       Web 管理后台 (Vue 3)           │
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
│  Gemini       │  MiniMax       │  Gemini TTS  │  Suno Music       │
│  Claude       │  阿里万相      │  Qwen TTS    │  阿里万相视频      │
│  Qwen         │  Flux          │  MiniMax TTS │  MiniMax Music    │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       基础设施                                   │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (数据存储)  │  阿里云 OSS (媒体存储)  │  Redis (缓存) │
└─────────────────────────────────────────────────────────────────┘
```

### 技术栈详情

| 模块 | 技术选型 |
|------|----------|
| **后端框架** | Python 3.11+, FastAPI, Pydantic |
| **数据库** | PostgreSQL + SQLAlchemy (async) |
| **数据库迁移** | Alembic |
| **小程序前端** | 微信小程序 (uni-app 编译) |
| **Web 前端** | Vue 3 + TypeScript + Tailwind CSS |
| **构建工具** | Vite |
| **LLM 服务** | Google Gemini (主力), Claude, Qwen |
| **图像生成** | MiniMax, 阿里万相, Flux |
| **语音合成** | Gemini TTS, Qwen TTS, MiniMax TTS |
| **音乐生成** | Suno (主力), MiniMax Music |
| **视频生成** | 阿里万相, MiniMax Hailuo |
| **对象存储** | 阿里云 OSS |

---

## 快速开始

### 环境要求

- Python 3.11+
- PostgreSQL 14+
- Node.js 18+ (Web 前端)
- 微信开发者工具 (小程序开发)

### 后端部署

```bash
# 1. 进入后端目录
cd backend

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -e ".[dev]"

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 5. 创建数据库
createdb moana

# 6. 运行数据库迁移
alembic upgrade head

# 7. 启动开发服务器
uvicorn moana.main:app --reload --host 0.0.0.0 --port 8000
```

### Web 管理后台

```bash
# 1. 进入 Web 目录
cd backend/web

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm run dev
```

### 微信小程序

1. 打开微信开发者工具
2. 导入 `miniprogram` 目录
3. 在 `project.config.json` 中配置你的 AppID
4. 在 `api/request.js` 中配置后端 API 地址

---

## 配置说明

### 必需的 API 密钥

在 `backend/.env` 中配置以下 API 密钥：

```bash
# 数据库连接
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/moana

# Google Gemini (推荐 - 支持 LLM + TTS + 图像)
GOOGLE_API_KEY=your_google_api_key

# 阿里云 DashScope (视频生成 + 备选 TTS)
DASHSCOPE_API_KEY=your_dashscope_api_key

# MiniMax (图像 + 音乐生成)
MINIMAX_API_KEY=your_minimax_api_key

# 阿里云 OSS (媒体文件存储)
OSS_ACCESS_KEY=your_oss_access_key
OSS_SECRET_KEY=your_oss_secret_key
OSS_BUCKET=your_bucket_name
OSS_ENDPOINT=https://oss-cn-hangzhou.aliyuncs.com
```

### Provider 切换

系统支持运行时切换不同的 AI 服务提供商：

```bash
# LLM 提供商: gemini | claude | qwen
LLM_PROVIDER=gemini

# 图像生成: minimax | qwen | flux
IMAGE_PROVIDER=minimax

# 语音合成: gemini | qwen | minimax | fish_speech
TTS_PROVIDER=gemini

# 音乐生成: suno | minimax
MUSIC_PROVIDER=suno

# 视频生成: wanx | minimax
VIDEO_PROVIDER=wanx
```

---

## 项目结构

```
Moana/
├── README.md                    # 项目说明
├── .gitignore                   # Git 忽略规则
│
├── backend/                     # Python 后端
│   ├── .env.example            # 环境变量模板
│   ├── alembic/                # 数据库迁移
│   │   └── versions/           # 迁移版本
│   ├── src/moana/              # 核心代码
│   │   ├── agents/             # AI Agent 模块
│   │   │   ├── intent.py       # 意图识别
│   │   │   ├── planner.py      # 内容规划
│   │   │   ├── story.py        # 故事生成
│   │   │   └── review.py       # 内容审核
│   │   ├── api/                # REST API 端点
│   │   │   ├── auth.py         # 认证
│   │   │   ├── content.py      # 内容管理
│   │   │   ├── child.py        # 孩子档案
│   │   │   └── play.py         # 播放记录
│   │   ├── models/             # 数据模型
│   │   ├── pipelines/          # 生成流水线
│   │   │   ├── picture_book.py # 绘本生成
│   │   │   ├── nursery_rhyme.py# 儿歌生成
│   │   │   └── video.py        # 视频生成
│   │   ├── services/           # 外部服务集成
│   │   │   ├── llm/            # 大语言模型
│   │   │   ├── image/          # 图像生成
│   │   │   ├── tts/            # 语音合成
│   │   │   ├── music/          # 音乐生成
│   │   │   ├── video/          # 视频生成
│   │   │   └── storage/        # 对象存储
│   │   ├── config.py           # 配置管理
│   │   ├── themes.py           # 主题定义
│   │   └── main.py             # 应用入口
│   ├── tests/                  # 测试用例
│   └── web/                    # Vue 管理后台
│       ├── src/
│       │   ├── views/          # 页面组件
│       │   ├── components/     # 通用组件
│       │   ├── api/            # API 封装
│       │   └── stores/         # Pinia 状态
│       └── package.json
│
└── miniprogram/                # 微信小程序
    ├── api/                    # API 请求封装
    ├── components/             # 小程序组件
    │   ├── ContentCard/        # 内容卡片
    │   ├── GeneratingProgress/ # 生成进度
    │   └── CreationModeSelector/# 创作模式选择
    ├── pages/                  # 页面
    │   ├── index/              # 首页
    │   ├── create/             # 创作页面
    │   │   ├── picture-book    # 绘本创作
    │   │   ├── nursery-rhyme   # 儿歌创作
    │   │   ├── video           # 视频创作
    │   │   └── smart           # 智能创作
    │   ├── play/               # 播放页面
    │   ├── library/            # 内容库
    │   ├── child/              # 孩子管理
    │   └── profile/            # 个人中心
    ├── stores/                 # 状态管理
    ├── utils/                  # 工具函数
    └── project.config.json     # 小程序配置
```

---

## API 文档

启动后端服务后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 主要 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/v1/auth/login` | POST | 微信登录 |
| `/api/v1/children` | GET/POST | 孩子档案管理 |
| `/api/v1/content/picture-book` | POST | 生成绘本 |
| `/api/v1/content/nursery-rhyme` | POST | 生成儿歌 |
| `/api/v1/content/video` | POST | 生成视频 |
| `/api/v1/library` | GET | 获取内容库 |
| `/api/v1/play/{content_id}` | POST | 记录播放 |

---

## 开发指南

### 添加新的艺术风格

1. 在 `backend/src/moana/styles/__init__.py` 中定义风格
2. 在 `backend/src/moana/services/prompt/templates.py` 中添加 Prompt 模板
3. 在小程序 `pages/create/picture-book.js` 中添加 UI 选项

### 添加新的教育主题

1. 在 `backend/src/moana/themes.py` 中定义主题
2. 在小程序对应页面添加主题选项

### 集成新的 AI 服务

1. 在 `backend/src/moana/services/` 下创建新的服务模块
2. 实现对应的 base 类接口
3. 在 `config.py` 中添加配置项

---

## 运行测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/api/test_content.py

# 运行并显示覆盖率
pytest --cov=moana
```

---

## 部署

### 生产环境建议

1. 使用 Gunicorn + Uvicorn workers 运行 FastAPI
2. 配置 Nginx 反向代理
3. 启用 HTTPS
4. 配置 PostgreSQL 连接池
5. 设置合适的日志级别

---

## 许可证

MIT License

---

## 贡献

欢迎提交 Issue 和 Pull Request！

在提交 PR 之前，请确保：

1. 代码通过所有测试
2. 遵循现有的代码风格
3. 更新相关文档

---

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系。
