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
from auth import (  # noqa: E402
    COOKIE_HELP,
    clear_session,
    has_session,
    load_session,
    parse_cookie_text,
    save_session,
)

PROFILE = xbmcvfs.translatePath(ADDON.getAddonInfo("profile"))

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


def _session():
    if not os.path.isdir(PROFILE):
        xbmcvfs.mkdirs(PROFILE)
    sess = load_session(PROFILE)
    if has_session(sess.get("cookies")):
        return sess
    raw = ADDON.getSetting("cookie") or ""
    cookies = parse_cookie_text(raw)
    if has_session(cookies):
        return {"cookies": cookies, "user": sess.get("user") or {}}
    return {"cookies": {}, "user": {}}


def client():
    quality = ADDON.getSetting("quality") or "1080p"
    try:
        count = int(ADDON.getSetting("count") or "20")
    except ValueError:
        count = 20
    sess = _session()
    return DouyinAPI(
        device_id=_ensure_device_id(),
        count=count,
        quality=quality,
        cookies=sess.get("cookies") or {},
    )


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
    sess = _session()
    user = sess.get("user") or {}
    if has_session(sess.get("cookies")):
        nick = user.get("nickname") or "已登录"
        add_dir("已登录 · %s" % nick, {"action": "account"}, plot="重新登录或退出")
        add_dir("我的关注", {"action": "following"}, plot="关注的人更新的视频")
    else:
        add_dir("登录抖音账号", {"action": "login"}, plot="粘贴 Cookie，登录一次会记住")
    add_dir("推荐", {"action": "feed"}, plot="抖音推荐")
    finish("files")
