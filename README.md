# 抖音 Kodi 插件

> **不要点绿色「代码 / Code」按钮里的「下载 ZIP 文件」。**
> 那个会得到 `kodi-main.zip`（大约 19KB），Kodi 会报：
> **无法从 zip 文件安装加载项 · 由于结构无效**

`kodi-main.zip` 是仓库源码，不是插件安装包。Kodi 只认下面这个文件。

## 正确安装包（请点这个）

**[↓ 下载 plugin.video.douyin-1.1.0.zip](https://github.com/xiaojiu885210-arch/kodi/releases/download/v1.1.0/plugin.video.douyin-1.1.0.zip)**

-文件名必须是 `plugin.video.douyin-1.1.0.zip`
- 大小约 **190 KB**（如果只有 19KB，就是下错了）
- 也可以打开仓库右边 **发布 / Releases** 手动选最新 zip

详细步骤见 [INSTALL.md](INSTALL.md)。

插件 ID：`plugin.video.douyin`  
当前版本：`1.1.0`

这是**非官方**插件，仅供个人学习使用。视频版权归抖音和创作者所有。

## 安装（从 zip）

1. 把 **plugin.video.douyin-1.1.0.zip** 拷到装着 Kodi 的电视 / 电脑 / 盒子（**U 盘最稳**，尽量不要走乱掉的 `smb://` 网络路径）。
2. 打开 Kodi → **设置** → **系统** → **插件** → 打开 **未知来源**。
3. 回到主页 → **插件** → 右上角打开盒子图标 → **从 zip 文件安装**。
4. 选中 `plugin.video.douyin-1.1.0.zip`，等提示安装成功。
5. 到 **插件 → 视频插件 → 抖音** 打开，点「推荐」就能播。

需要 **Kodi 19 Matrix 及以上**（带 Python 3）。Kodi 20 / 21 都可以。

**不要解压再重新压回去。** zip 里第一层必须是 `plugin.video.douyin/` 文件夹：

```text
plugin.video.douyin-1.1.0.zip
  plugin.video.douyin/
    addon.xml
    addon.py
    resources/
```

## 能做什么

| 入口 | 说明 |
| --- | --- |
| 推荐 | 刷抖音推荐流（一次大约 20 条），点「换一批」刷新 |
| 连续播放推荐 | 拉一波推荐并自动连播 |
| 热搜榜 | 今日热搜，点进去播相关视频 |
| 今日热搜视频 | 把热搜话题里的视频合成一列 |
| 搜索 | 搜热搜词，或直接粘贴分享链接 |
| 打开链接 | 粘贴 `v.douyin.com/...` 或 `douyin.com/video/...` |

点任意视频即可在 Kodi 播放器里全屏播放。

## 自己打包

```bash
python3 scripts/pack.py
# 生成 dist/plugin.video.douyin-1.1.0.zip
```

## 说明

- 需要能访问抖音（国内网络更稳）。
- 搜索接口会限制未登录账号，所以搜索主要走热搜词和分享链接。
- 画质、每次加载数量可在插件设置里改。
- 分享链接依赖抖音短链跳转；如果打不开，用「推荐」或「热搜」看视频。
