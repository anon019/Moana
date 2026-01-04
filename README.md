# Moana - AI 原生早教内容生成系统

[English](#english) | [中文](#中文)

---

## 中文

### 项目简介

Moana 是一个 AI 原生的早期教育内容生成系统，专为 1-6 岁儿童设计。通过先进的 AI 技术，为每个孩子生成个性化的绘本故事、儿歌童谣和教育视频。

### 核心特性

- **AI 绘本生成**：根据教育主题和孩子年龄，自动生成精美的儿童绘本
- **多种艺术风格**：支持皮克斯 3D、水彩、卡通、吉卜力等 30+ 种艺术风格
- **智能 TTS 配音**：使用 Google Gemini TTS 生成自然的故事朗读
- **主题式学习**：涵盖习惯养成、认知启蒙、情感成长、冒险探索、社交能力、节日故事等
- **个性化创作**：支持智能创作模式，根据用户描述生成定制内容

### 技术架构

```
Moana/
├── backend/           # Python 后端服务
│   ├── src/moana/    # 核心业务逻辑
│   │   ├── agents/   # AI Agent 模块
│   │   ├── api/      # REST API
│   │   ├── services/ # 业务服务层
│   │   └── models/   # 数据模型
│   ├── web/          # Web 管理后台 (Vue)
│   └── tests/        # 测试用例
└── miniprogram/      # 微信小程序前端
    ├── pages/        # 页面
    ├── components/   # 组件
    └── api/          # API 封装
```

### 技术栈

**后端**
- Python 3.11+
- FastAPI
- PostgreSQL + SQLAlchemy
- Alembic (数据库迁移)

**AI 服务**
- Google Gemini (LLM + TTS + 图像生成)
- 阿里万相 (视频生成)
- MiniMax (音乐生成)

**前端**
- 微信小程序 (uni-app)
- Vue 3 + TypeScript (Web 后台)
- Tailwind CSS

### 快速开始

#### 后端部署

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -e ".[dev]"

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API 密钥

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn moana.main:app --reload
```

#### 小程序开发

```bash
cd miniprogram

# 使用微信开发者工具打开此目录
# 在 project.config.json 中配置你的 appid
# 在 api/request.js 中配置你的后端 API 地址
```

### 配置说明

在 `backend/.env` 中配置以下必需的 API 密钥：

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/moana

# AI 服务 (至少配置一个 LLM Provider)
GOOGLE_API_KEY=your_google_api_key      # 推荐：支持 LLM + TTS + 图像
DASHSCOPE_API_KEY=your_dashscope_key    # 阿里云：视频生成
MINIMAX_API_KEY=your_minimax_key        # MiniMax：音乐生成

# 微信小程序
WECHAT_APP_ID=your_wechat_appid
WECHAT_APP_SECRET=your_wechat_secret
```

### 贡献指南

欢迎提交 Issue 和 Pull Request！

### 许可证

MIT License

---

## English

### Overview

Moana is an AI-native early childhood education content generation system designed for children ages 1-6. It uses advanced AI technology to generate personalized picture books, nursery rhymes, and educational videos for each child.

### Key Features

- **AI Picture Book Generation**: Automatically generates beautiful children's picture books based on educational themes and child's age
- **Multiple Art Styles**: Supports 30+ art styles including Pixar 3D, watercolor, cartoon, Ghibli, etc.
- **Smart TTS Narration**: Uses Google Gemini TTS for natural story narration
- **Theme-based Learning**: Covers habit formation, cognitive development, emotional growth, adventure exploration, social skills, and holiday stories
- **Personalized Creation**: Smart creation mode generates custom content based on user descriptions

### Tech Stack

**Backend**
- Python 3.11+ / FastAPI
- PostgreSQL + SQLAlchemy
- Alembic (Database migrations)

**AI Services**
- Google Gemini (LLM + TTS + Image Generation)
- Alibaba Wanx (Video Generation)
- MiniMax (Music Generation)

**Frontend**
- WeChat Mini Program (uni-app)
- Vue 3 + TypeScript (Web Admin)
- Tailwind CSS

### Quick Start

See the Chinese section above for detailed setup instructions.

### License

MIT License
