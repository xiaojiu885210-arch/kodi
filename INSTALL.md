# Kodi 报「结构无效」怎么办

## 你现在看到的错误

```
无法从 zip 文件安装加载项
由于结构无效
```

这不是插件坏了，是 **zip 下错了**。

GitHub 绿色「代码」按钮 → 「下载 ZIP 文件」 会给你：

| 文件 | 大小 | Kodi 能不能装 |
| --- | --- | --- |
| `kodi-main.zip`（源码包） | 约 19 KB | 不能，一定报结构无效 |
| `plugin.video.douyin-1.1.0.zip`（发布包） | 约 190 KB | 能 |

## 下载正确的包

点这里：

**https://github.com/xiaojiu885210-arch/kodi/releases/download/v1.1.0/plugin.video.douyin-1.1.0.zip**

或者：打开仓库页面 → 右边 **发布** → 进最新一条 → 下载资产里的 `plugin.video.douyin-1.1.0.zip`。

## 装到 Kodi

1. 把 zip **原封不动** 拷到电视 / 盒子。最稳是 **U 盘**。
2. 不要解压，不要用 WinRAR 再压一次。
3. 尽量不要走 `smb://video:...` 这种网络路径（容易选错目录）。
4. Kodi → 设置 → 系统 → 插件 → **未知来源 = 开**。
5. 插件 → 从 zip 文件安装 → 选 `plugin.video.douyin-1.1.0.zip`。
6. 视频插件 → 抖音 → 推荐。

## 正确的 zip 结构

```text
plugin.video.douyin-1.1.0.zip
  plugin.video.douyin/
    addon.xml
    addon.py
    resources/
```

如果你解压后看到的第一层是 `kodi-main/`，说明下的是源码包，直接丢掉换正确的安装包。
