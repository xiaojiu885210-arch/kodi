# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmcplugin

from api import DouyinError
from library import follows, likes, remember, save_queue, toggle_follow, toggle_like, videos_by_author
from plugin import HANDLE, ICON, PROFILE, add_dir, add_video, client, finish, notify


def show_following():
    rows = follows(PROFILE)
    xbmcplugin.setPluginCategory(HANDLE, "我的关注")
    if not rows:
        notify("还没有关注。看视频时长按 OK → 关注作者")
        finish(succeeded=True)
        return
    for row in rows:
        add_dir(
            row.get("nickname") or "抖音用户",
            {
                "action": "author",
                "sec_uid": row.get("sec_uid") or "",
                "uid": row.get("uid") or "",
                "nickname": row.get("nickname") or "",
            },
            icon=row.get("avatar") or ICON,
            plot="点进去看他的视频",
        )
    finish("files")


def show_favorite():
    items = likes(PROFILE)
    xbmcplugin.setPluginCategory(HANDLE, "我喜欢")
    if not items:
        notify("还没有喜欢。看视频时长按 OK → 喜欢此视频")
        finish(succeeded=True)
        return
    save_queue(PROFILE, items)
    for item in items:
        add_video(item)
    finish(cache=False)


def show_author(sec_uid, user_id="", nickname=""):
    xbmcplugin.setPluginCategory(HANDLE, nickname or "作者主页")
    items = videos_by_author(PROFILE, sec_uid)
    try:
        api = client()
        if hasattr(api, "user_posts"):
            fresh = api.user_posts(sec_uid, user_id)
            if fresh:
                remember(PROFILE, fresh)
                seen = {str(x.get("aweme_id") or "") for x in items}
                for row in fresh:
                    if str(row.get("aweme_id") or "") not in seen:
                        items.append(row)
                        seen.add(str(row.get("aweme_id") or ""))
    except DouyinError:
        pass
    if not items:
        notify("暂时没有这个作者的视频，先从推荐里多刷几条再进主页")
        finish(succeeded=True)
        return
    remember(PROFILE, items)
    save_queue(PROFILE, items)
    for item in items:
        add_video(item)
    finish(cache=False)


def do_toggle_like(params):
    item = {
        "aweme_id": params.get("aweme_id") or "",
        "video_id": params.get("video_id") or "",
        "title": params.get("title") or "",
        "author": params.get("author") or "",
        "sec_uid": params.get("sec_uid") or "",
        "uid": params.get("uid") or "",
        "cover": params.get("cover") or "",
        "avatar": params.get("avatar") or "",
        "duration": int(params.get("duration") or 0),
        "plot": params.get("title") or "",
    }
    liked = toggle_like(PROFILE, item)
    notify("已喜欢" if liked else "已取消喜欢")
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True)


def do_toggle_follow(params):
    item = {
        "sec_uid": params.get("sec_uid") or "",
        "uid": params.get("uid") or "",
        "author": params.get("nickname") or "",
        "avatar": params.get("avatar") or "",
    }
    followed = toggle_follow(PROFILE, item)
    notify("已关注 %s" % (item.get("author") or "作者") if followed else "已取消关注")
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True)
