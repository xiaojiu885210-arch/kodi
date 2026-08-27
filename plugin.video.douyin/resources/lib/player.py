# -*- coding: utf-8 -*-
from __future__ import annotations

import urllib.parse

import xbmc
import xbmcgui
import xbmcplugin

from api import DouyinError
from library import load_queue
from plugin import FANART, HANDLE, ICON, PLAY_UA, PROFILE, client, finish, notify, plugin_url


def kodi_play_path(url):
    headers = urllib.parse.urlencode({"User-Agent": PLAY_UA, "Referer": "https://www.douyin.com/"})
    return url + "|" + headers


def play_item(aweme_id, video_id="", title=""):
    try:
        path = client().play_url(video_id=video_id, aweme_id=aweme_id)
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
    queue_next(aweme_id)


def queue_next(aweme_id):
    queue = load_queue(PROFILE)
    idx = -1
    for i, item in enumerate(queue):
        if str(item.get("aweme_id") or "") == str(aweme_id or ""):
            idx = i
            break
    if idx < 0:
        return
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    for item in queue[idx + 1 :]:
        path = plugin_url(
            {
                "action": "play",
                "aweme_id": item.get("aweme_id") or "",
                "video_id": item.get("video_id") or "",
                "title": item.get("title") or "",
            }
        )
        nli = xbmcgui.ListItem(label=item.get("title") or "抖音视频", offscreen=True)
        nli.setProperty("IsPlayable", "true")
        nli.setInfo("video", {"title": item.get("title") or "抖音视频", "mediatype": "video"})
        playlist.add(path, nli)


def do_open():
    from browse import keyboard

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
