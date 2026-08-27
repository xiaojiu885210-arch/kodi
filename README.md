# 抖音 Kodi 插件

在 Kodi 里看抖音推荐、热搜，以及登录自己的账号看「我的关注」「我喜欢」。

插件 ID：`plugin.video.douyin`  
当前版本：`1.2.0`

这是**非官方**插件，仅供个人学习使用。视频版权归抖音和创作者所有。

## 安装（从 zip）

直接下载安装包：

**[plugin.video.douyin-1.2.0.zip](https://github.com/xiaojiu885210-arch/kodi/releases/download/v1.2.0/plugin.video.douyin-1.2.0.zip)**

也可以打开仓库 [Releases](https://github.com/xiaojiu885210-arch/kodi/releases) 页面手动选最新 zip。

1. 把 zip 拷到装着 Kodi 的电视 / 电脑 / 盒子（U 盘也可以）。
2. 打开 Kodi → **设置** → **系统** → **插件** → 打开 **未知来源**。
3. 回到主页 → **插件** → 右上角打开盒子图标 → **从 zip 文件安装**。
4. 选中 `plugin.video.douyin-1.2.0.zip`，等提示安装成功。
5. 到 **插件 → 视频插件 → 抖音** 打开。

需要 **Kodi 19 Matrix 及以上**（带 Python 3）。Kodi 20 / 21 都可以。

zip 必须保持这种结构（不要自己把里面的文件再解压一层再压回去）：

```text
plugin.video.douyin-1.2.0.zip
└── plugin.video.douyin/
    ├── addon.xml
    ├── addon.py
    └── resources/
```

不要下载 GitHub 绿色「代码」按钮里的 `kodi-main.zip`，那个会报「结构无效」。

## 登录自己的账号（Cookie）

抖音的扫码 + 扫脸验证不适合直接做在 Kodi 里，插件改成和不少 B 站插件一样的 **Cookie 登录**：

1. 电脑浏览器打开 [https://www.douyin.com](https://www.douyin.com) 并登录（扫码、扫脸都在网页 / App 完成）。
2. 按 `F12` → **应用程序 / Application** → **Cookies** → `https://www.douyin.com`。
3. 找到 `sessionid`，复制它的**值**（或整段 Cookie）。
4. 在 Kodi 插件首页点 **登录抖音账号** → **粘贴 Cookie / sessionid**。
5. 也可以把内容存成 U 盘上的 `douyin_cookie.txt`，选 **从文本文件读取**。

登录一次会保存在本机，下次打开不用再贴。不要把 Cookie 发给任何人。

Cookie 过期后再按上面步骤换一个新的即可。

## 能做什么

| 入口 | 说明 |
| --- | --- |
| 登录抖音账号 | 粘贴 Cookie，登录一次会记住 |
| 我的关注 | 登录后看关注的人更新 |
| 我喜欢 | 登录后看点过赞的视频 |
| 推荐 | 刷抖音推荐流（一次大约 20 条） |
| 连续播放推荐 | 拉一波推荐并自动连播 |
| 热搜榜 | 今日热搜，点进去播相关视频 |
| 今日热搜视频 | 把热搜话题里的视频合成一列 |
| 搜索 | 搜热搜词，或直接粘贴分享链接 |
| 打开链接 | 粘贴 `v.douyin.com/...` 或 `douyin.com/video/...` |

点任意视频即可在 Kodi 播放器里全屏播放。

## 自己打包

```bash
python3 scripts/pack.py
# 生成 dist/plugin.video.douyin-1.2.0.zip
```

## 说明

- 需要能访问抖音（国内网络更稳）。
- 搜索接口会限制未登录账号，所以搜索主要走热搜词和分享链接。
- 画质、每次加载数量、Cookie 可在插件设置里改。
- 分享链接依赖抖音短链跳转；如果打不开，用「推荐」或「热搜」看视频。
