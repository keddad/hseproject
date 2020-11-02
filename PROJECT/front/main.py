import asyncio
from pathlib import Path
from base64 import b85encode
import shutil
from multiprocessing import Process, Queue

import aiohttp
from jinja2 import Environment, FileSystemLoader, select_autoescape
from loguru import logger
from mmh3 import hash128
from sanic import Sanic
from sanic.exceptions import abort
from sanic.request import Request
from sanic.response import html, redirect, text

from downloader import download_vid
from utils import *

env = Environment(
    loader=FileSystemLoader('./templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

app = Sanic(name="ff_front")
download_q = Queue()

wtf = False


async def fetch_downloader():
    cache = GlobalCache()
    loop = asyncio.get_event_loop()
    while True:
        await asyncio.sleep(1)  
        if not download_q.empty():
            msg = download_q.get()

            if msg[1] == True:
                loop.create_task(process_task(
                    msg[0], True, Path(msg[2]).read_bytes()))
                logger.debug(f"Passed {msg[2]} to process_task")
                shutil.rmtree(Path(msg[2]).parent)
            else:
                cache[msg[0]].status = TaskStatus.ERR
                cache[msg[0]].err = msg[2]


async def process_task(task_id: int, is_video: bool, file: bytes):
    cache = GlobalCache()

    if is_video:
        logger.debug(f"Video: {task_id}")
        file_key = "video"
        url = "http://ff_videocomp:3800/api/video"
    else:
        logger.debug(f"Photo: {task_id}")
        file_key = "face"
        url = "http://ff_corecomp:3800/api/core/recface"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={file_key: b85encode(file).decode()}) as resp:
            if resp.status != 200:
                cache[task_id].status = TaskStatus.ERR
                cache[task_id].err = (await resp.json())["detail"]
                logger.warning(f"Error for {cache[task_id]}")
            else:
                cache[task_id].status = TaskStatus.DONE
                cache[task_id].output = await resp.json()


@app.route("/task/<tag>")
async def fetch_task(request: Request, tag):
    cache = GlobalCache()
    tag = int(tag)

    if tag not in cache:
        abort(404)

    if cache[tag].status == TaskStatus.DONE:
        template = env.get_template("result.html")
        return html(template.render(data=cache[tag].output, round=round))
    elif cache[tag].status == TaskStatus.PENDING:
        template = env.get_template("pending.html")
        return html(template.render())
    else:
        template = env.get_template("error.html")
        return html(template.render(err_text=cache[tag].err))


@app.route('/', methods=["GET", "POST"])
async def welcome(request: Request):
    if request.method == "GET":
        template = env.get_template("main.html")
        return html(template.render())

    elif request.method == "POST":
        cache = GlobalCache()
        body = request.files["file"][0].body
        mime = request.files["file"][0].type

        file_hash = hash128(body)
        cache[file_hash] = Task()

        loop = asyncio.get_event_loop()
        loop.create_task(process_task(file_hash, "video" in mime, body))

        return redirect(f"./task/{file_hash}")


@app.route('/vid', methods=["POST"])
async def vid(request: Request):
    task_cache = GlobalCache()
    global wtf

    if not wtf:
        loop = asyncio.get_event_loop()
        loop.create_task(fetch_downloader())
        wtf = True

    vid_url = request.form.get('url')
    url_hash = hash128(vid_url)

    task_cache[url_hash] = Task()

    downloader_p = Process(target=download_vid, args=(
        vid_url, download_q, url_hash))
    downloader_p.start()

    return redirect(f"./task/{url_hash}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3800)
