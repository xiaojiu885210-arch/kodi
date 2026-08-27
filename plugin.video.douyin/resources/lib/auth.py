# -*- coding: utf-8 -*-
"""Cookie session for the Douyin Kodi add-on."""
from __future__ import annotations

import json
import os
import re

SESSION_NAME = "session.json"
KEEP = (
    "sessionid",
    "sessionid_ss",
    "sid_guard",
    "sid_tt",
    "uid_tt",
    "uid_tt_ss",
    "ssid_ucp_v1",
    "odin_tt",
    "passport_csrf_token",
    "ttwid",
)

COOKIE_HELP = """电脑浏览器打开 https://www.douyin.com 并登录。
扫码、扫脸都在网页或抖音 App 里完成，插件不再弹二维码。

然后按 F12 打开开发者工具：
1. 点「应用程序」或 Application
2. 左侧 Cookies → https://www.douyin.com
3. 找到 sessionid，复制它的「值」
   （也可以复制整段 Cookie）

回到 Kodi：
· 选「粘贴 Cookie / sessionid」
· 或把内容存成 U 盘上的 douyin_cookie.txt，选「从文本文件读取」

登录一次会保存在本机，下次打开不用再贴。
不要把 Cookie 发给任何人。
"""


def parse_cookie_text(text):
    text = (text or "").strip()
    text = text.replace("\r", "").replace("\n", "; ")
    if text.lower().startswith("cookie:"):
        text = text.split(":", 1)[1].strip()
    cookies = {}
    if "=" in text:
        for part in re.split(r";\s*", text):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"')
            if key:
                cookies[key] = value
    elif re.fullmatch(r"[A-Za-z0-9._-]{16,128}", text):
        cookies["sessionid"] = text
        cookies["sessionid_ss"] = text
    slim = {k: cookies[k] for k in KEEP if cookies.get(k)}
    if cookies.get("sessionid") and "sessionid" not in slim:
        slim["sessionid"] = cookies["sessionid"]
    if not slim.get("sessionid") and cookies.get("sessionid_ss"):
        slim["sessionid"] = cookies["sessionid_ss"]
        slim["sessionid_ss"] = cookies["sessionid_ss"]
    return slim


def has_session(cookies):
    sid = (cookies or {}).get("sessionid") or (cookies or {}).get("sessionid_ss") or ""
    return len(sid) >= 16


def session_path(profile_dir):
    return os.path.join(profile_dir, SESSION_NAME)


def load_session(profile_dir):
    path = session_path(profile_dir)
    if not os.path.isfile(path):
        return {"cookies": {}, "user": {}}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return {"cookies": {}, "user": {}}
    if not isinstance(data, dict):
        return {"cookies": {}, "user": {}}
    cookies = data.get("cookies") if isinstance(data.get("cookies"), dict) else {}
    user = data.get("user") if isinstance(data.get("user"), dict) else {}
    return {"cookies": cookies, "user": user}


def save_session(profile_dir, cookies, user=None):
    os.makedirs(profile_dir, exist_ok=True)
    payload = {
        "cookies": dict(cookies or {}),
        "user": dict(user or {}),
    }
    path = session_path(profile_dir)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)
    return payload


def clear_session(profile_dir):
    path = session_path(profile_dir)
    try:
        if os.path.isfile(path):
            os.remove(path)
    except OSError:
        pass
