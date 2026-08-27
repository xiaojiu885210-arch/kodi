# -*- coding: utf-8 -*-
from __future__ import annotations

import urllib.parse

from api import APP_UA, HOSTS, DouyinAPI, DouyinError, _is_video, _normalize

_orig_init = DouyinAPI.__init__


def _init(self, device_id=None, count=20, quality="1080p", cookies=None, **kwargs):
    try:
        _orig_init(self, device_id=device_id, count=count, quality=quality)
    except TypeError:
        _orig_init(self)
        self.device_id = device_id or getattr(self, "device_id", "")
        self.count = count or 20
        self.quality = quality or "1080p"
    self.cookies = dict(cookies or {})


DouyinAPI.__init__ = _init


def _cookie(self):
    cookies = getattr(self, "cookies", None) or {}
    return "; ".join("%s=%s" % (k, v) for k, v in cookies.items() if k and v)


def _json_app(self, path, params):
    headers = {"User-Agent": APP_UA, "Accept": "application/json", "Accept-Language": "zh-CN"}
    ck = _cookie(self)
    if ck:
        headers["Cookie"] = ck
    query = urllib.parse.urlencode({k: v for k, v in params.items() if v not in (None, "")})
    last = None
    for host in HOSTS:
        try:
            return self._request_json(host + path + "?" + query, headers=headers)
        except Exception as exc:
            last = exc
            continue
    if last:
        raise DouyinError(str(last))
    return {}


def _collect(rows, sec_uid, nickname, seen, out):
    for row in rows or []:
        aid = str(row.get("aweme_id") or "")
        if not aid or aid in seen:
            continue
        author_sec = str(row.get("sec_uid") or "")
        author_name = (row.get("author") or "").strip()
        if sec_uid and author_sec and author_sec != sec_uid:
            continue
        if nickname and author_name and author_sec != sec_uid and author_name != nickname:
            continue
        seen.add(aid)
        out.append(row)


def user_posts(self, sec_uid, user_id="", nickname=""):
    sec_uid = (sec_uid or "").strip()
    nickname = (nickname or "").strip()
    seen = set()
    out = []
    params = self.common_params()
    params.update({"max_cursor": "0", "source": "0", "count": str(self.count)})
    if sec_uid:
        params["sec_user_id"] = sec_uid
    if user_id:
        params["user_id"] = str(user_id)
    try:
        data = _json_app(self, "/aweme/v1/aweme/post/", params)
        _collect(
            [_normalize(item) for item in data.get("aweme_list") or [] if _is_video(item)],
            sec_uid,
            nickname,
            seen,
            out,
        )
    except DouyinError:
        pass
    if len(out) >= 8:
        return out[: self.count]
    if nickname:
        try:
            data = _json_app(
                self,
                "/aweme/v1/general/search/single/",
                dict(self.common_params(), keyword=nickname, offset="0", count="20"),
            )
            rows = []
            for row in data.get("data") or data.get("aweme_list") or []:
                if not isinstance(row, dict):
                    continue
                aweme = row.get("aweme_info") or row.get("aweme") or row
                if isinstance(aweme, dict) and _is_video(aweme):
                    rows.append(_normalize(aweme))
            _collect(rows, sec_uid, nickname, seen, out)
        except DouyinError:
            pass
        try:
            _collect(self.hot_videos(nickname), sec_uid, nickname, seen, out)
        except DouyinError:
            pass
        try:
            _collect(self.search(nickname), sec_uid, nickname, seen, out)
        except DouyinError:
            pass
    return out[: max(self.count, 20)]


DouyinAPI.user_posts = user_posts
