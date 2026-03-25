# Moana 微信小程序

Moana 儿童教育平台的微信小程序客户端，基于 uni-app + Vue 3 + TypeScript 开发。

## 📱 功能特性

### 内容创作
- **绘本生成** - 自定义主题、风格、角色的 AI 绘本创作
- **儿歌创作** - 智能生成儿歌歌词和音频，支持歌词同步高亮
- **视频生成** - AI 视频内容创作
- **智能创作** - 基于标签和灵感的智能创作助手

### 内容播放
- **绘本播放器** - 翻页动画、音频朗读、进度保存
- **儿歌播放器** - 音频播放、歌词同步、循环播放
- **视频播放器** - 视频播放、进度控制、全屏支持

### 内容管理
- **内容库** - 浏览所有创作内容，支持类型筛选
- **收藏管理** - 收藏喜欢的内容，快速访问
- **播放记录** - 自动记录播放进度，断点续播

### 儿童模式
- **简化界面** - 儿童友好的大图标界面
- **轻量浏览** - 直接进入内容播放，不限制单次阅读和观看时长
- **内容筛选** - 按内容类型快速筛选

### 用户功能
- **个人中心** - 账号入口、孩子信息管理
- **问题反馈** - 提交使用问题和产品建议

## 🛠️ 技术栈

- **框架**: uni-app 3.x
- **前端**: Vue 3 (Composition API) + TypeScript
- **UI 库**: Wot Design Uni
- **状态管理**: Pinia 3.x
- **国际化**: vue-i18n 9.x
- **样式**: Sass/SCSS
- **构建工具**: Vite 5.x

## 🚀 快速开始

### 环境要求

- Node.js >= 16.x
- npm >= 8.x
- 微信开发者工具

### 安装依赖

```bash
npm install
```

### 配置微信小程序 AppID

首次开发需要配置微信小程序 AppID：

```bash
# 自动补齐本地配置模板（只在缺文件时创建，不会覆盖已有配置）
npm run ensure:public-config

# 编辑以下文件，将 YOUR_WECHAT_APPID_HERE 替换为你的 AppID
# - project.config.json
# - src/manifest.json
```

详细配置说明请查看 [敏感配置指南](README.sensitive-config.md)

`npm run dev:mp-weixin` 和 `npm run build:mp-weixin` 会先自动执行一次 `npm run ensure:public-config`，确保首次下载仓库后可以直接本地编译；如果你已经填过自己的配置，脚本不会覆盖已有文件。

### 配置 API 地址

如果你要在本地真正跑通内容接口，而不只是完成编译，请先配置 API 地址：

```bash
cp .env.example .env.local
```

然后把 `.env.local` 里的 `VITE_API_URL` 改成你自己的后端地址。`.env.local` 不会被提交到仓库。

### 开发模式

```bash
# 编译到微信小程序
npm run dev:mp-weixin
```

编译完成后：
1. 打开微信开发者工具
2. 导入项目，选择 `dist/dev/mp-weixin` 目录
3. 开始调试

### 生产构建

```bash
# 生产模式编译
npm run build:mp-weixin
```

构建产物在 `dist/build/mp-weixin` 目录，用于真机测试和发布。

### 类型检查

```bash
npm run type-check
```

当前仓库的完整 `type-check` 仍有历史遗留问题，主要集中在 `src/components/ContentCard/ContentCard.vue`、`src/config/nurseryRhyme*.ts` 和 `src/pages/create/*`。首页、内容库、收藏页和播放器链路相关文件新增修改时，应保证不引入新的类型错误。

### 性能与加载约定

- 首页数据加载保持单飞，避免重复登录、重复拉孩子信息和重复拉播放历史
- 内容库列表只渲染封面/缩略图，不在列表阶段为每本绘本渲染整本预览轮播
- 收藏页返回前台优先复用缓存并按过期策略刷新，不要每次 `onShow` 强制全量请求
- 儿童模式先展示第一页内容，再后台补齐剩余分页
- 绘本播放器保持 image-first 首屏策略，不要让当前页音频预下载阻塞首图出现

## 📂 项目结构

```
miniprogram/
├── src/
│   ├── pages/                    # 页面目录
│   │   ├── index/               # 首页
│   │   ├── create/              # 创作相关页面
│   │   │   ├── index.vue        # 创作首页
│   │   │   ├── picture-book.vue # 绘本创作
│   │   │   ├── nursery-rhyme.vue # 儿歌创作
│   │   │   ├── video.vue        # 视频创作
│   │   │   └── smart.vue        # 智能创作
│   │   ├── play/                # 播放器页面
│   │   │   ├── picture-book.vue # 绘本播放器
│   │   │   ├── nursery-rhyme.vue # 儿歌播放器
│   │   │   └── video.vue        # 视频播放器
│   │   ├── library/             # 内容库
│   │   ├── favorites/           # 收藏
│   │   ├── child/               # 儿童模式
│   │   ├── feedback/            # 问题反馈
│   │   └── profile/             # 个人中心
│   │
│   ├── components/              # 公共组件
│   │   ├── ContentCard/         # 内容卡片
│   │   ├── LoadingState/        # 加载状态
│   │   └── ...
│   │
│   ├── api/                     # API 接口
│   │   ├── auth.ts              # 认证相关
│   │   ├── content.ts           # 内容相关
│   │   ├── favorite.ts          # 收藏相关
│   │   ├── feedback.ts          # 反馈相关
│   │   ├── play.ts              # 播放相关
│   │   └── request.ts           # 请求封装
│   │
│   ├── stores/                  # Pinia 状态管理
│   │   ├── user.ts              # 用户状态
│   │   ├── content.ts           # 内容状态
│   │   ├── favorite.ts          # 收藏状态
│   │   └── child.ts             # 儿童模式状态
│   │
│   ├── utils/                   # 工具函数
│   │   ├── cache.ts             # 缓存工具
│   │   ├── storage.ts           # 存储工具
│   │   ├── performance.ts       # 性能埋点/计时
│   │   └── url.ts               # URL 工具
│   │
│   ├── static/                  # 静态资源
│   │   └── tabbar/              # 底部导航图标
│   │
│   ├── App.vue                  # 应用入口
│   ├── manifest.json.template   # uni-app 配置模板
│   ├── pages.json               # 页面配置
│   └── uni.scss                 # 全局样式变量
│
├── dist/                        # 编译输出
│   ├── dev/                     # 开发模式
│   └── build/                   # 生产模式
│
├── project.config.json          # 微信小程序配置（.gitignore）
├── project.private.config.json  # 私有配置（.gitignore）
├── .env.example                 # API 地址示例配置
├── scripts/                     # 本地配置自举脚本
├── vite.config.ts              # Vite 配置
├── tsconfig.json               # TypeScript 配置
└── package.json                # 项目依赖
```

## 🎯 开发指南

### 页面路由

使用 `uni.navigateTo` 进行页面跳转：

```typescript
// 跳转到绘本播放器
uni.navigateTo({
  url: '/pages/play/picture-book?id=xxx'
})

// 跳转到儿歌播放器
uni.navigateTo({
  url: '/pages/play/nursery-rhyme?id=xxx'
})
```

### 内容类型

平台支持三种内容类型：

| 类型 | 标识 | 播放器路径 |
|------|------|-----------|
| 绘本 | `picture_book` | `/pages/play/picture-book` |
| 儿歌 | `nursery_rhyme` | `/pages/play/nursery-rhyme` |
| 视频 | `video` | `/pages/play/video` |

根据 `content_type` 字段路由到对应的播放器。

### API 调用

使用封装的 API 函数：

```typescript
import { getContentList, getContentDetail } from '@/api/content'

// 获取内容列表
const list = await getContentList({
  page: 1,
  page_size: 10,
  content_type: 'picture_book'
})

// 获取内容详情
const detail = await getContentDetail('content_id')
```

### 状态管理

使用 Pinia stores：

```typescript
import { useUserStore } from '@/stores/user'
import { useContentStore } from '@/stores/content'

const userStore = useUserStore()
const contentStore = useContentStore()

// 访问状态
console.log(userStore.userInfo)

// 调用 actions
await userStore.login(code)
```

### 数据临时存储

生成内容后跳转到播放页的流程：

```typescript
// 1. 存储临时数据
uni.setStorageSync('temp_picture_book', contentData)

// 2. 跳转到播放页
uni.redirectTo({
  url: '/pages/play/picture-book?fromGenerate=1'
})

// 3. 播放页读取数据
const tempData = uni.getStorageSync('temp_picture_book')
if (tempData) {
  // 使用数据
  uni.removeStorageSync('temp_picture_book') // 使用后清除
}
```

### CSS 兼容性注意

微信小程序对部分 CSS 属性支持不完整：

```css
/* ❌ 不支持 */
.container {
  inset: 0;
}

/* ✅ 使用这个 */
.container {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* ⚠️ 部分设备不支持 */
.overlay {
  backdrop-filter: blur(10px);
}
```

布局容器建议添加 `flex-shrink: 0` 防止被压缩。

## 🔄 异步生成流程

绘本和儿歌采用异步生成机制，避免超时问题：

```typescript
// 1. 发起异步生成请求
const { task_id } = await createPictureBookAsync(params)

// 2. 轮询获取生成状态
const checkStatus = async () => {
  const status = await getPictureBookStatus(task_id)

  if (status.status === 'completed') {
    // 生成完成
    const content = status.result
  } else if (status.status === 'failed') {
    // 生成失败
    console.error(status.error)
  } else {
    // 继续等待
    setTimeout(checkStatus, 2000)
  }
}

checkStatus()
```

生成阶段：
- `pending` / `waiting` - 任务已提交
- `processing` - 正在处理
- `text` - 文本生成完成（绘本）/ 歌词生成完成（儿歌）
- `image` - 图片生成完成（绘本）
- `first` - 第一首歌完成（儿歌）
- `completed` - 全部完成
- `failed` - 生成失败

## 📱 儿童模式

儿童模式的特点：

- **简化界面**: 大图标、纯图片导航
- **自由播放**: 不限制单次阅读和观看时长
- **类型筛选**: 绘本、儿歌、视频快速切换
- **防误操作**: 简化交互逻辑

进入儿童模式：

```typescript
uni.navigateTo({
  url: '/pages/child/index'
})
```

## 🐛 调试技巧

### 开发者工具调试

1. 打开微信开发者工具
2. 导入 `dist/dev/mp-weixin` 目录
3. 使用控制台、Network、Storage 等面板调试

### 真机调试

1. 编译生产模式：`npm run build:mp-weixin`
2. 在开发者工具中预览二维码
3. 使用手机微信扫码测试

### 查看生成日志

当内容生成失败时，可以调用生成日志 API 排查：

```typescript
import { getGenerationLogs } from '@/api/content'

const logs = await getGenerationLogs(contentId)
console.log('生成状态:', logs.status)
console.log('总耗时:', logs.total_duration_ms, 'ms')
logs.logs.forEach(log => {
  console.log(`[${log.stage}] ${log.message}`)
})
```

## 📋 开发规范

### 代码风格

- 使用 TypeScript，充分利用类型系统
- 使用 Vue 3 Composition API
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case
- 使用 `<script setup>` 语法

### 提交规范

遵循 Conventional Commits：

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式
refactor: 重构
perf: 性能优化
test: 测试
chore: 构建/工具
```

### 注意事项

- **编译规则**: 每次修改代码后，必须同时编译 dev 和 build 两个目录
- **敏感配置**: 永远不要提交包含真实 AppID 的配置文件
- **API 超时**: 绘本/儿歌生成使用异步 API，视频生成超时时间为 5 分钟
- **网络请求**: 所有 API 请求都需要通过 `request.ts` 统一封装

## 📚 相关文档

- [敏感配置说明](README.sensitive-config.md) - AppID 配置指南
- [.env.example](.env.example) - API 地址示例配置
- [`src/api/request.ts`](src/api/request.ts) - 基础请求封装
- [`src/api/`](src/api) - 业务接口定义

## 🔗 API 接口

**基础地址**: `VITE_API_URL`（通过 `.env.local` 配置）

主要接口：
- `POST /content/picture-book/async` - 绘本生成
- `POST /content/nursery-rhyme/async` - 儿歌生成
- `POST /content/video` - 视频生成
- `GET /content/list` - 内容列表
- `GET /content/{id}` - 内容详情
- `GET /favorite/list` - 收藏列表
- `POST /favorite/add` - 添加收藏

接口封装示例见 [`src/api/content.ts`](src/api/content.ts)、[`src/api/favorite.ts`](src/api/favorite.ts) 和 [`src/api/request.ts`](src/api/request.ts)。

## 🚀 发布流程

1. 更新版本号（`src/manifest.json`）
2. 编译生产版本：`npm run build:mp-weixin`
3. 在微信开发者工具中导入 `dist/build/mp-weixin`
4. 上传代码并填写版本说明
5. 提交审核
6. 审核通过后发布

## 📞 技术支持

如有问题，请查看：
- [敏感配置说明](README.sensitive-config.md)
- [.env.example](.env.example)
- [项目主 README](../README.md)
- 提交 Issue

---

Made with ❤️ using [uni-app](https://uniapp.dcloud.net.cn/)
