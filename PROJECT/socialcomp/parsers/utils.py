import aiohttp
import tldextract
import random


def _get_referer() -> str:
    return random.choice([
        "https://yandex.ru", "https://google.com", "https://mail.ru"
    ])


def _get_ua() -> str:
    return random.choice([
        "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
        "Mozilla/5.0 (Windows NT 6.3) AppleWebKit/537.43 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36 OPR/67.0.3575.137"
    ])


def _get_headers(host: str = "") -> dict:
    if host:
        uri_info = tldextract.extract(host)
        host = uri_info.domain + "." + uri_info.suffix

    return {
        "Referer": _get_referer(),
        "Connection": "keep-alive",
        "Accept": "*/*",
        "Host": host,
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": _get_ua()
    }


async def get_page(url: str) -> str:
    async with aiohttp.ClientSession(headers=_get_headers(url)) as sess:
        async with sess.get(url) as resp:
            html = await resp.text()
            return html


async def get_file(url: str) -> bytes:
    async with aiohttp.ClientSession(headers=_get_headers(url)) as sess:
        async with sess.get(url) as resp:
            bt = await resp.read()
            return bt
