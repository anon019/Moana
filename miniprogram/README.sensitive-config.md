# 敏感配置文件说明

## 微信小程序配置

为了保护敏感信息，以下配置文件已从 Git 仓库中排除：

### 需要本地创建的文件

1. **project.config.json**
   - 复制 `project.config.json.template` 为 `project.config.json`
   - 将 `YOUR_WECHAT_APPID_HERE` 替换为你的微信小程序 AppID

2. **project.private.config.json**
   - 复制 `project.private.config.json.template` 为 `project.private.config.json`
   - 根据需要调整项目名称和设置

3. **src/manifest.json**
   - 复制 `src/manifest.json.template` 为 `src/manifest.json`
   - 将 `mp-weixin.appid` 的 `YOUR_WECHAT_APPID_HERE` 替换为你的微信小程序 AppID

### 快速设置

```bash
# 在 miniprogram 目录下执行
cd miniprogram

# 复制配置模板
cp project.config.json.template project.config.json
cp project.private.config.json.template project.private.config.json
cp src/manifest.json.template src/manifest.json

# 使用你喜欢的编辑器修改 AppID
# 1. 编辑 project.config.json，将 YOUR_WECHAT_APPID_HERE 替换为真实 AppID
# 2. 编辑 src/manifest.json，将 mp-weixin.appid 的 YOUR_WECHAT_APPID_HERE 替换为真实 AppID
```

### 重要提示

- ⚠️ **永远不要提交包含真实 AppID 的配置文件到 Git**
- ✅ 这些文件已经添加到 `.gitignore`，不会被 Git 跟踪
- 📝 如果需要分享配置，请使用模板文件（`.template` 后缀）

### 获取微信小程序 AppID

1. 登录[微信公众平台](https://mp.weixin.qq.com/)
2. 进入「开发」->「开发管理」->「开发设置」
3. 在「开发者ID」部分找到 AppID
