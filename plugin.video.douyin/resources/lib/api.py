# -*- coding: utf-8 -*-
"""Minimal Douyin client for Kodi (stdlib only)."""
from __future__ import annotations

import json
import random
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

APP_UA = (
    "com.ss.android.ugc.aweme/190500 "
    "(Linux; U; Android 13; zh_CN; Pixel 7; Build/TQ3A; Cronet/58.0.2991.0)"
)
WEB_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
)
HOSTS = (
    "https://aweme.snssdk.com",
    "https://aweme-hl.snssdk.com",
    "https://api5-normal-c-lq.amemv.com",
)
PLAY_TEMPLATE = "https://aweme.snssdk.com/aweme/v1/play/?video_id={vid}&ratio={ratio}&line=0"

_CTX = ssl.create_default_context()


class DouyinError(Exception):
    pass


class DouyinAPI:
    def __init__(self, device_id=None, count=20, quality="1080p"):
        self.device_id = device_id or _new_device_id()
        self.count = max(6, min(int(count or 20), 40))
        self.quality = quality if quality in ("720p", "1080p") else "1080p"

    def common_params(self):
        return {
            "aid": "1128",
            "app_name": "aweme",
            "version_code": "190500",
            "version_name": "19.5.0",
            "device_id": self.device_id,
            "iid": self.device_id,
            "os_api": "29",
            "os_version": "13",
            "device_type": "Pixel 7",
            "device_brand": "google",
            "language": "zh",
            "resolution": "1080*2400",
            "dpi": "420",
            "count": str(self.count),
        }

    def feed(self, pull_type=0):
        params = self.common_params()
        params.update(
            {
                "type": "0",
                "max_cursor": "0",
                "min_cursor": "0",
                "pull_type": str(pull_type),
                "volume": "0.2",
                "is_cold_start": "1" if pull_type == 0 else "0",
            }
        )
        data = self._get_json("/aweme/v1/feed/", params)
        return [_normalize(item) for item in data.get("aweme_list") or [] if _is_video(item)]

    def hot_words(self):
        url = "https://www.douyin.com/aweme/v1/web/hot/search/list/"
        data = self._request_json(
            url,
            headers={
                "User-Agent": WEB_UA,
                "Referer": "https://www.douyin.com/",
                "Accept": "application/json",
            },
        )
        words = ((data.get("data") or {}).get("word_list")) or data.get("word_list") or []
        out = []
        for i, row in enumerate(words, 1):
            word = (row.get("word") or "").strip()
            if not word:
                continue
            cover = ""
            urls = ((row.get("word_cover") or {}).get("url_list")) or []
            if urls:
                cover = urls[0]
            out.append(
                {
                    "rank": int(row.get("position") or i),
                    "word": word,
                    "hot_value": int(row.get("hot_value") or 0),
                    "sentence_id": str(row.get("sentence_id") or ""),
                    "video_count": int(row.get("video_count") or 0),
                    "cover": cover,
                    "label": int(row.get("label") or 0),
                }
            )
        return out

    def hot_videos(self, word, sentence_id=""):
        params = self.common_params()
        if word:
            params["hotword"] = word
        if sentence_id:
            params["sentence_id"] = sentence_id
        data = self._get_json("/aweme/v1/hot/search/video/list/", params)
        return [_normalize(item) for item in data.get("aweme_list") or [] if _is_video(item)]

    def search(self, keyword):
        keyword = (keyword or "").strip()
        if not keyword:
            return []
        if re.search(r"douyin\\.com|iesdouyin\\.com|v\\.douyin", keyword, re.I):
            item = self.from_share(keyword)
            return [item] if item else []
        items = self.hot_videos(keyword)
        if items:
            return items
        matches = [w for w in self.hot_words() if keyword in w["word"] or w["word"] in keyword]
        seen = set()
        out = []
        for w in matches[:5]:
            for item in self.hot_videos(w["word"], w.get("sentence_id") or ""):
                if item["aweme_id"] in seen:
                    continue
                seen.add(item["aweme_id"])
                out.append(item)
        return out

    def detail(self, aweme_id):
        params = self.common_params()
        params["aweme_id"] = str(aweme_id)
        data = self._get_json("/aweme/v1/aweme/detail/", params)
        item = data.get("aweme_detail") or {}
        if not item:
            raise DouyinError("视频不存在或已删除")
        return _normalize(item)

    def from_share(self, text):
        aweme_id = self.resolve_aweme_id(text)
        if not aweme_id:
            raise DouyinError("无法从链接里解析视频 ID")
        return self.detail(aweme_id)

    def resolve_aweme_id(self, text):
        text = (text or "").strip()
        if not text:
            return ""
        patterns = (
            r"douyin\\.com/video/(\\d{15,})",
            r"douyin\\.com/note/(\\d{15,})",
            r"iesdouyin\\.com/share/video/(\\d{15,})",
            r"modal_id=(\\d{15,})",
            r"aweme_id=(\\d{15,})",
            r"/(\\d{19})(?:[/?#]|$)",
        )
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1)
        short = re.search(r"https?://v\\.douyin\\.com/[A-Za-z0-9_\\-]+/?", text)
        if not short:
            short = re.search(r"(https?://v\\.douyin\\.com/[A-Za-z0-9_\\-]+)", text)
        if short:
            final = self._follow(short.group(0))
            for pat in patterns:
                m = re.search(pat, final)
                if m:
                    return m.group(1)
        return ""

    def play_url(self, item=None, video_id="", aweme_id=""):
        vid = video_id or (item or {}).get("video_id") or ""
        if vid:
            return PLAY_TEMPLATE.format(vid=urllib.parse.quote(vid, safe=""), ratio=self.quality)
        aid = aweme_id or (item or {}).get("aweme_id") or ""
        if not aid:
            raise DouyinError("缺少视频 ID")
        fresh = self.detail(aid)
        if not fresh.get("video_id"):
            raise DouyinError("没有可播放的视频地址")
        return PLAY_TEMPLATE.format(
            vid=urllib.parse.quote(fresh["video_id"], safe=""), ratio=self.quality
        )

    def _get_json(self, path, params):
        query = urllib.parse.urlencode(params)
        last_err = None
        for host in HOSTS:
            try:
                return self._request_json(
                    host + path + "?" + query,
                    headers={
                        "User-Agent": APP_UA,
                        "Accept-Language": "zh-CN",
                        "Accept": "application/json",
                    },
                )
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                continue
        raise DouyinError("网络请求失败：%s" % last_err)

    def _request_json(self, url, headers=None, timeout=20):
        raw = self._request_bytes(url, headers=headers, timeout=timeout)
        if not raw:
            raise DouyinError("接口返回为空")
        try:
            data = json.loads(raw.decode("utf-8"))
        except ValueError as exc:
            raise DouyinError("接口返回不是 JSON") from exc
        code = data.get("status_code")
        if code not in (0, None):
            msg = data.get("status_msg") or ("错误码 %s" % code)
            raise DouyinError(str(msg))
        return data

    def _request_bytes(self, url, headers=None, timeout=20):
        req = urllib.request.Request(url, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as resp:
                return resp.read(2_000_000)
        except urllib.error.HTTPError as exc:
            body = exc.read(400) if exc.fp else b""
            raise DouyinError("HTTP %s %s" % (exc.code, body[:120])) from exc
        except urllib.error.URLError as exc:
            raise DouyinError("连接失败：%s" % exc.reason) from exc

    def _follow(self, url):
        class _Capture(urllib.request.HTTPRedirectHandler):
            last = url

            def redirect_request(self, req, fp, code, msg, headers, newurl):
                _Capture.last = newurl
                return urllib.request.HTTPRedirectHandler.redirect_request(
                    self, req, fp, code, msg, headers, newurl
                )

        opener = urllib.request.build_opener(_Capture)
        req = urllib.request.Request(
            url,
            headers={"User-Agent": WEB_UA, "Accept": "text/html,*/*"},
        )
        try:
            with opener.open(req, timeout=15) as resp:
                return resp.geturl() or _Capture.last
        except urllib.error.HTTPError as exc:
            loc = exc.headers.get("Location") if exc.headers else None
            return loc or _Capture.last
        except Exception:  # noqa: BLE001
            return _Capture.last


def _new_device_id():
    return str(random.randint(10**14, 10**15 - 1))


def _is_video(item):
    if not item:
        return False
    video = item.get("video") or {}
    play = video.get("play_addr") or {}
    return bool((play.get("uri") or (play.get("url_list") or [None])[0]) and item.get("aweme_id"))


def _first_url(node):
    if not isinstance(node, dict):
        return ""
    urls = node.get("url_list") or []
    return urls[0] if urls else ""


def _normalize(item):
    author = item.get("author") or {}
    video = item.get("video") or {}
    play = video.get("play_addr") or video.get("play_addr_h264") or {}
    cover = video.get("origin_cover") or video.get("cover") or {}
    stats = item.get("statistics") or {}
    desc = (item.get("desc") or "").strip()
    nick = (author.get("nickname") or "抖音用户").strip()
    title = desc if desc else ("@%s 的视频" % nick)
    if len(title) > 80:
        title = title[:77] + "…"
    duration_ms = int(video.get("duration") or item.get("duration") or 0)
    duration = duration_ms // 1000 if duration_ms > 1000 else duration_ms
    likes = int(stats.get("digg_count") or 0)
    comments = int(stats.get("comment_count") or 0)
    plot_bits = [desc or title, "@%s" % nick]
    if likes:
        plot_bits.append("赞 %s" % _human(likes))
    if comments:
        plot_bits.append("评 %s" % _human(comments))
    return {
        "aweme_id": str(item.get("aweme_id") or ""),
        "video_id": str(play.get("uri") or ""),
        "title": title,
        "plot": "  ·  ".join(plot_bits),
        "author": nick,
        "sec_uid": str(author.get("sec_uid") or ""),
        "cover": _first_url(cover),
        "duration": duration,
        "width": int(video.get("width") or 0),
        "height": int(video.get("height") or 0),
        "likes": likes,
        "create_time": int(item.get("create_time") or time.time()),
    }


def _human(n):
    n = int(n or 0)
    if n >= 100000000:
        return "%.1f亿" % (n / 100000000.0)
    if n >= 10000:
        return "%.1f万" % (n / 10000.0)
    return str(n)
