# -*- coding: utf-8 -*-
from __future__ import annotations

import xbmc
import xbmcgui
import xbmcvfs

from api import DouyinAPI, DouyinError
from auth import COOKIE_HELP, clear_session, has_session, parse_cookie_text, save_session
from browse import keyboard
from plugin import ADDON, HANDLE, PROFILE, add_dir, ensure_device_id, finish, notify, session


def show_cookie_help():
    try:
        xbmcgui.Dialog().textviewer("怎么获取 Cookie", COOKIE_HELP)
    except Exception:
        xbmcgui.Dialog().ok("怎么获取 Cookie", COOKIE_HELP[:900])


def apply_cookies(cookies):
    if not has_session(cookies):
        raise DouyinError("没识别到 sessionid。请复制 Cookies 里 sessionid 的值。")
    user = {"nickname": "抖音用户", "uid": "", "sec_uid": "", "avatar": ""}
    try:
        api = DouyinAPI(device_id=ensure_device_id(), cookies=cookies)
        if hasattr(api, "me"):
            user = api.me() or user
    except TypeError:
        save_session(PROFILE, cookies, user)
        ADDON.setSetting("cookie", cookies.get("sessionid") or "")
        return user
    except DouyinError:
        pass
    save_session(PROFILE, cookies, user)
    ADDON.setSetting("cookie", cookies.get("sessionid") or "")
    return user


def do_login():
    choice = xbmcgui.Dialog().select(
        "登录抖音账号",
        ["粘贴 Cookie / sessionid", "从文本文件读取", "怎么获取 Cookie"],
    )
    if choice < 0:
        finish(succeeded=False)
        return
    if choice == 2:
        show_cookie_help()
        finish(succeeded=False)
        return
    text = ""
    if choice == 0:
        text = keyboard("粘贴 sessionid 或整段 Cookie")
        if text is None:
            finish(succeeded=False)
            return
    elif choice == 1:
        path = xbmcgui.Dialog().browse(1, "选择 douyin_cookie.txt", "files", ".txt|.TXT")
        if not path:
            finish(succeeded=False)
            return
        try:
            fh = xbmcvfs.File(path)
            text = fh.read()
            fh.close()
        except Exception as exc:
            notify("读文件失败：%s" % exc, xbmcgui.NOTIFICATION_ERROR)
            finish(succeeded=False)
            return
    if not (text or "").strip():
        notify("没有输入内容")
        finish(succeeded=False)
        return
    try:
        user = apply_cookies(parse_cookie_text(text))
    except DouyinError as exc:
        notify(str(exc), xbmcgui.NOTIFICATION_ERROR)
        finish(succeeded=False)
        return
    notify("已登录 " + (user.get("nickname") or "抖音用户"))
    xbmc.executebuiltin("Container.Refresh")
    finish(succeeded=True)


def show_account():
    add_dir("重新登录", {"action": "login"}, plot="更换 Cookie")
    add_dir("怎么获取 Cookie", {"action": "cookie_help"}, plot="浏览器复制 sessionid")
    add_dir("退出登录", {"action": "logout"}, plot="删除本机保存的登录信息", is_folder=False)
    finish("files")


def do_logout():
    import xbmcplugin

    clear_session(PROFILE)
    ADDON.setSetting("cookie", "")
    notify("已退出登录")
    xbmc.executebuiltin("Container.Refresh")
    xbmcplugin.endOfDirectory(HANDLE, succeeded=True)
