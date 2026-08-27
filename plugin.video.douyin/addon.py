# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys
import urllib.parse

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo("id")
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))
HANDLE = int(sys.argv[1])
BASE_URL = sys.argv[0]
ICON = os.path.join(ADDON_PATH, "resources", "media", "icon.png")
FANART = os.path.join(ADDON_PATH, "resources", "media", "fanart.png")

sys.path.insert(0, os.path.join(ADDON_PATH, "resources", "lib"))
from api import DouyinAPI, DouyinError  # noqa: E402

PLAY_UA = (
    "com.ss.android.ugc.aweme/190500 "
    "(Linux; U; Android 13; zh_CN; Pixel 7; Build/TQ3A; Cronet/58.0.2991.0)"
)


def _ensure_device_id():
    device_id = ADDON.getSetting("device_id")
    if not device_id:
        import random

        device_id = str(random.randint(10**14, 10**15 - 1))
        ADDON.setSetting("device_id", device_id)
    return device_id


def client():
    quality = ADDON.getSetting("quality") or "1080p"
    try:
        count = int(ADDON.getSetting("count") or "20")
    except ValueError:
        count = 20
    return DouyinAPI(device_id=_ensure_device_id(), count=count, quality=quality)


def plugin_url(query):
    return BASE_URL + "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})


def get_params():
    raw = sys.argv[2][1:] if len(sys.argv) > 2 else ""
    parsed = urllib.parse.parse_qs(raw)
    return {k: v[0] for k, v in parsed.items()}


def notify(message, icon=xbmcgui.NOTIFICATION_INFO, ms=4000):
    xbmcgui.Dialog().notification("抖音", message, icon, ms)


def add_dir(title, query, icon=ICON, plot="", is_folder=True):
    li = xbmcgui.ListItem(label=title, offscreen=True)
    li.setArt({"icon": icon, "thumb": icon, "fanart": FANART})
    li.setInfo("video", {"title": title, "plot": plot, "mediatype": "video"})
    xbmcplugin.addDirectoryItem(HANDLE, plugin_url(query), li, is_folder)


def add_video(item):
    li = xbmcgui.ListItem(label=item["title"], offscreen=True)
    art = item.get("cover") or ICON
    li.setArt({"icon": art, "thumb": art, "poster": art, "fanart": item.get("cover") or FANART})
    li.setInfo(
        "video",
        {
            "title": item["title"],
            "plot": item.get("plot") or item["title"],
            "duration": int(item.get("duration") or 0),
            "mediatype": "video",
        },
    )
    li.setProperty("IsPlayable", "true")
    li.setProperty("mimeType", "video/mp4")
    url = plugin_url(
        {
            "action": "play",
            "aweme_id": item.get("aweme_id") or "",
            "video_id": item.get("video_id") or "",
            "title": item.get("title") or "",
        }
    )
    xbmcplugin.addDirectoryItem(HANDLE, url, li, False)


def finish(content="videos", succeeded=True, cache=False):
    xbmcplugin.setContent(HANDLE, content)
    xbmcplugin.endOfDirectory(HANDLE, succeeded=succeeded, cacheToDisc=cache, updateListing=False)


def home():
    add_dir("推荐", {"action": "feed"}, plot="抖音推荐视频，每次进入都会换一批")
    add_dir("连续播放推荐", {"action": "autoplay"}, plot="加载一波推荐并立刻连续播放")
    add_dir("热搜榜", {"action": "hot"}, plot="今日热搜，点进去看相关视频")
    add_dir("今日热搜视频", {"action": "hot_mix"}, plot="把热搜话题里的视频合成一列")
    add_dir("搜索", {"action": "search"}, plot="搜热搜词，或直接粘贴抖音分享链接")
    add_dir("打开链接", {"action": "open"}, plot="粘贴 v.douyin.com 或 douyin.com/video 链接播放")
    finish("files")


def _list_videos(title, loader, empty_msg):
    xbmcplugin.setPluginCategory(HANDLE, title)
    try:
        items = loader()
    except DouyinError as exc:
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
        finish(succeeded=False)
        return
    if not items:
        notify(empty_msg)
        finish(succeeded=True)
        return
    for item in items:
        add_video(item)
    return items


def show_feed():
    items = _list_videos("推荐", lambda: client().feed(pull_type=0), "暂时没有拉到推荐，再进一次试试")
    if items:
        add_dir("换一批", {"action": "feed", "t": str(xbmc.getInfoLabel("System.Time"))}, plot="再刷一页推荐")
        finish(cache=False)


def show_hot():
    xbmcplugin.setPluginCategory(HANDLE, "热搜榜")
    try:
        words = client().hot_words()
    except DouyinError as exc:
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
        finish(succeeded=False)
        return
    labels = {0: "", 1: "新", 3: "热"}
    for word in words:
        tag = labels.get(word.get("label") or 0, "")
        prefix = "%02d. " % word["rank"]
        if tag:
            prefix += "[%s] " % tag
        title = prefix + word["word"]
        plot = "热度 %s · %s 条视频" % (word.get("hot_value") or "-", word.get("video_count") or "-")
        add_dir(
            title,
            {
                "action": "hot_videos",
                "word": word["word"],
                "sentence_id": word.get("sentence_id") or "",
            },
            icon=word.get("cover") or ICON,
            plot=plot,
        )
    finish("files")


def show_hot_videos(word, sentence_id=""):
    items = _list_videos(
        word or "热搜视频",
        lambda: client().hot_videos(word, sentence_id),
        "这个热搜暂时没有可播视频",
    )
    if items:
        finish(cache=False)


def show_hot_mix():
    items = _list_videos("今日热搜视频", lambda: client().hot_mix(), "暂时没有热搜视频")
    if items:
        finish(cache=False)


def keyboard(heading, default=""):
    kb = xbmc.Keyboard(default, heading, False)
    kb.doModal()
    if not kb.isConfirmed():
        return None
    return (kb.getText() or "").strip()


def do_search(query=None):
    if not query:
        query = keyboard("搜索抖音 / 粘贴分享链接")
        if query is None:
            finish(succeeded=False)
            return
        if not query:
            notify("请输入关键词或链接")
            finish(succeeded=False)
            return
    items = _list_videos(
        "搜索：%s" % query,
        lambda: client().search(query),
        "没搜到视频。试试热搜榜，或粘贴抖音分享链接",
    )
    if items:
        finish(cache=False)


def do_open():
    text = keyboard("粘贴抖音分享链接或口令")
    if text is None:
        finish(succeeded=False)
        return
    if not text:
        notify("没有输入内容")
        finish(succeeded=False)
        return
    try:
        item = client().from_share(text)
    except DouyinError as exc:
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
        finish(succeeded=False)
        return
    play_item(item.get("aweme_id") or "", item.get("video_id") or "", item.get("title") or "")


def kodi_play_path(url):
    headers = urllib.parse.urlencode(
        {
            "User-Agent": PLAY_UA,
            "Referer": "https://www.douyin.com/",
        }
    )
    return url + "|" + headers


def play_item(aweme_id, video_id="", title=""):
    api = client()
    try:
        path = api.play_url(video_id=video_id, aweme_id=aweme_id)
    except DouyinError as exc:
        xbmcplugin.setResolvedUrl(HANDLE, False, xbmcgui.ListItem())
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
        return
    li = xbmcgui.ListItem(label=title or "抖音视频", path=kodi_play_path(path), offscreen=True)
    li.setArt({"icon": ICON, "thumb": ICON, "fanart": FANART})
    li.setInfo("video", {"title": title or "抖音视频", "mediatype": "video"})
    li.setMimeType("video/mp4")
    li.setContentLookup(False)
    li.setProperty("IsPlayable", "true")
    xbmcplugin.setResolvedUrl(HANDLE, True, li)


def autoplay():
    xbmcplugin.setPluginCategory(HANDLE, "连续播放")
    try:
        items = client().feed(pull_type=0)
    except DouyinError as exc:
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
        finish(succeeded=False)
        return
    if not items:
        notify("暂时没有可播放的推荐")
        finish(succeeded=True)
        return
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()
    for item in items:
        add_video(item)
        path = plugin_url(
            {
                "action": "play",
                "aweme_id": item.get("aweme_id") or "",
                "video_id": item.get("video_id") or "",
                "title": item.get("title") or "",
            }
        )
        li = xbmcgui.ListItem(label=item["title"], offscreen=True)
        art = item.get("cover") or ICON
        li.setArt({"icon": art, "thumb": art, "fanart": FANART})
        li.setInfo(
            "video",
            {"title": item["title"], "plot": item.get("plot") or "", "mediatype": "video"},
        )
        li.setProperty("IsPlayable", "true")
        playlist.add(path, li)
    xbmc.Player().play(playlist)
    finish(cache=False)


def router():
    params = get_params()
    action = params.get("action") or ""
    if action == "feed":
        show_feed()
    elif action == "hot":
        show_hot()
    elif action == "hot_videos":
        show_hot_videos(params.get("word") or "", params.get("sentence_id") or "")
    elif action == "hot_mix":
        show_hot_mix()
    elif action == "search":
        do_search(params.get("q"))
    elif action == "open":
        do_open()
    elif action == "play":
        play_item(params.get("aweme_id") or "", params.get("video_id") or "", params.get("title") or "")
    elif action == "autoplay":
        autoplay()
    else:
        home()


if __name__ == "__main__":
    router()
