# 抖音 Kodi 插件

在 Kodi 里看抖音推荐视频、热搜，以及打开抖音分享链接。

插件 ID：`plugin.video.douyin`  
当前版本：`1.0.0`

这是**非官方**插件，仅供个人学习使用。视频版权归抖音和创作者所有。

## 安装（从 zip）

1. 打开仓库 [Releases](https://github.com/xiaojiu885210-arch/kodi/releases) 页面，下载 `plugin.video.douyin-1.0.0.zip`。
2. 打开 Kodi → **设置** → **系统** → **插件** → 打开 **未知来源**。
3. 回到主页 → **插件** → 右上角打开盒子图标 → **从 zip 文件安装**。
4. 选中刚下载的 `plugin.video.douyin-1.0.0.zip`。
5. 安装完成后到 **插件 → 视频插件 → 抖音** 打开。

zip 必须保持这种结构（不要自己把里面的文件再解压一层）：

```text
plugin.video.douyin-1.0.0.zip
└── plugin.video.douyin/
    ├── addon.xml
    ├── addon.py
    └── resources/
```

## 能做什么

| 入口 | 说明 |
| --- | --- |
| 推荐 | 刷抖音推荐流，点「换一批」刷新 |
| 热搜榜 | 今日热搜，点进去播相关视频 |
| 搜索 | 搜热搜词，或直接粘贴分享链接 |
| 打开链接 | 粘贴 `v.douyin.com/...` 或 `douyin.com/video/...` |
| 连续播放推荐 | 拉一波推荐并自动连播 |

点任意视频即可在 Kodi 播放器里全屏播放。

## 自己打包

```bash
python3 scripts/pack.py
# 生成 dist/plugin.video.douyin-1.0.0.zip
```

## 说明

- 需要能访问抖音（国内网络更稳）。
- 搜索接口会限制未登录账号，所以搜索主要走热搜词和分享链接。
- 画质、每次加载数量可在插件设置里改。
