# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import sys

import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_PATH = xbmcvfs.translatePath(ADDON.getAddonInfo("path"))
sys.path.insert(0, os.path.join(ADDON_PATH, "resources", "lib"))

from account import do_login, do_logout, show_account, show_cookie_help  # noqa: E402
from browse import do_search, home, show_feed, show_hot, show_hot_videos  # noqa: E402
from mine import do_toggle_follow, do_toggle_like, show_author, show_favorite, show_following  # noqa: E402
from player import do_open, play_item  # noqa: E402
from plugin import get_params  # noqa: E402


def router():
    params = get_params()
    action = params.get("action") or ""
    if action == "feed":
        show_feed()
    elif action == "hot":
        show_hot()
    elif action == "hot_videos":
        show_hot_videos(params.get("word") or "", params.get("sentence_id") or "")
    elif action == "search":
        do_search(params.get("q"))
    elif action == "open":
        do_open()
    elif action == "play":
        play_item(params.get("aweme_id") or "", params.get("video_id") or "", params.get("title") or "")
    elif action == "following":
        show_following()
    elif action == "favorite":
        show_favorite()
    elif action == "author":
        show_author(params.get("sec_uid") or "", params.get("uid") or "", params.get("nickname") or "")
    elif action == "toggle_like":
        do_toggle_like(params)
    elif action == "toggle_follow":
        do_toggle_follow(params)
    elif action == "login":
        do_login()
    elif action == "logout":
        do_logout()
    elif action == "account":
        show_account()
    elif action == "cookie_help":
        show_cookie_help()
        from plugin import finish as _finish

        _finish(succeeded=False)
    else:
        home()


if __name__ == "__main__":
    router()
