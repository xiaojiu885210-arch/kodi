# -*- coding: utf-8 -*-
"""Local likes / follows stored on this Kodi box."""
from __future__ import annotations

import json
import os
import time

LIKES_NAME = "likes.json"
FOLLOWS_NAME = "follows.json"
QUEUE_NAME = "queue.json"
SEEN_NAME = "seen.json"


def _path(profile_dir, name):
    return os.path.join(profile_dir, name)


def _load_list(profile_dir, name):
    path = _path(profile_dir, name)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def _save_list(profile_dir, name, rows):
    os.makedirs(profile_dir, exist_ok=True)
    path = _path(profile_dir, name)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False)
    os.replace(tmp, path)


def likes(profile_dir):
    return _load_list(profile_dir, LIKES_NAME)


def is_liked(profile_dir, aweme_id):
    aweme_id = str(aweme_id or "")
    return any(str(row.get("aweme_id") or "") == aweme_id for row in likes(profile_dir))


def toggle_like(profile_dir, item):
    aweme_id = str((item or {}).get("aweme_id") or "")
    if not aweme_id:
        return False
    rows = [row for row in likes(profile_dir) if str(row.get("aweme_id") or "") != aweme_id]
    liked = len(rows) != len(likes(profile_dir))
    if liked:
        _save_list(profile_dir, LIKES_NAME, rows)
        return False
    row = dict(item)
    row["saved_at"] = int(time.time())
    rows.insert(0, row)
    _save_list(profile_dir, LIKES_NAME, rows[:400])
    return True


def follows(profile_dir):
    return _load_list(profile_dir, FOLLOWS_NAME)


def is_followed(profile_dir, sec_uid):
    sec_uid = str(sec_uid or "")
    return any(str(row.get("sec_uid") or "") == sec_uid for row in follows(profile_dir))


def toggle_follow(profile_dir, item):
    sec_uid = str((item or {}).get("sec_uid") or "")
    if not sec_uid:
        return False
    rows = [row for row in follows(profile_dir) if str(row.get("sec_uid") or "") != sec_uid]
    followed = len(rows) != len(follows(profile_dir))
    if followed:
        _save_list(profile_dir, FOLLOWS_NAME, rows)
        return False
    rows.insert(
        0,
        {
            "sec_uid": sec_uid,
            "uid": str((item or {}).get("uid") or ""),
            "nickname": (item or {}).get("author") or (item or {}).get("nickname") or "抖音用户",
            "avatar": (item or {}).get("avatar") or "",
            "saved_at": int(time.time()),
        },
    )
    _save_list(profile_dir, FOLLOWS_NAME, rows[:200])
    return True


def save_queue(profile_dir, items):
    _save_list(profile_dir, QUEUE_NAME, items or [])


def load_queue(profile_dir):
    return _load_list(profile_dir, QUEUE_NAME)


def remember(profile_dir, items):
    if not items:
        return
    seen = _load_list(profile_dir, SEEN_NAME)
    index = {str(row.get("aweme_id") or ""): i for i, row in enumerate(seen)}
    for item in reversed(items):
        aweme_id = str(item.get("aweme_id") or "")
        if not aweme_id:
            continue
        if aweme_id in index:
            seen.pop(index[aweme_id])
            index = {str(row.get("aweme_id") or ""): i for i, row in enumerate(seen)}
        seen.insert(0, item)
    _save_list(profile_dir, SEEN_NAME, seen[:800])


def videos_by_author(profile_dir, sec_uid):
    sec_uid = str(sec_uid or "")
    if not sec_uid:
        return []
    out = []
    seen = set()
    for row in likes(profile_dir) + load_queue(profile_dir) + _load_list(profile_dir, SEEN_NAME):
        if str(row.get("sec_uid") or "") != sec_uid:
            continue
        aweme_id = str(row.get("aweme_id") or "")
        if not aweme_id or aweme_id in seen:
            continue
        seen.add(aweme_id)
        out.append(row)
    return out
