# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmc
import xbmcgui

from api import DouyinError
from library import remember, save_queue
from plugin import HANDLE, ICON, PROFILE, add_dir, add_video, client, finish, notify


def list_videos(title, loader, empty_msg):
    import xbmcplugin

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
    remember(PROFILE, items)
    save_queue(PROFILE, items)
    for item in items:
        add_video(item)
    return items


def home():
    from auth import has_session
    from plugin import session

    sess = session()
    if has_session(sess.get("cookies")):
        nick = (sess.get("user") or {}).get("nickname") or "已登录"
        add_dir("已登录 · %s" % nick, {"action": "account"}, plot="重新登录或退出")
    else:
        add_dir("登录抖音账号", {"action": "login"}, plot="网页扫码后粘贴 Cookie，登录一次会记住")
    add_dir("推荐", {"action": "feed"}, plot="刷推荐。点进去播，播完自动下一条，长按 OK 进作者主页")
    add_dir("搜索", {"action": "search"}, plot="搜抖音视频，或粘贴分享链接")
    add_dir("我的关注", {"action": "following"}, plot="插件里关注的作者")
    add_dir("我喜欢", {"action": "favorite"}, plot="插件里点过喜欢的视频")
    add_dir("热搜榜", {"action": "hot"}, plot="今日热搜")
    add_dir("打开链接", {"action": "open"}, plot="粘贴 v.douyin.com 链接播放")
    finish("files")


def show_feed():
    items = list_videos("推荐", lambda: client().feed(pull_type=0), "暂时没有拉到推荐，再进一次试试")
    if items:
        add_dir("换一批", {"action": "feed", "t": str(xbmc.getInfoLabel("System.Time"))}, plot="再刷一页")
        finish(cache=False)


def show_hot():
    import xbmcplugin

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
        add_dir(
            prefix + word["word"],
            {"action": "hot_videos", "word": word["word"], "sentence_id": word.get("sentence_id") or ""},
            icon=word.get("cover") or ICON,
            plot="热度 %s" % (word.get("hot_value") or "-"),
        )
    finish("files")


def show_hot_videos(word, sentence_id=""):
    items = list_videos(word or "热搜视频", lambda: client().hot_videos(word, sentence_id), "这个热搜暂时没有可播视频")
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
    items = list_videos("搜索：%s" % query, lambda: client().search(query), "没搜到视频，换个词或去热搜榜")
    if items:
        finish(cache=False)
