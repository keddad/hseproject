import youtube_dl
import tempfile
from loguru import logger


def download_vid(url: str, mp_q, task_id: int) -> None:
    file = tempfile.mkdtemp() + "/vid"

    YDL_OPTS = {
        "quiet": False,
        "cachedit": False,
        "outtmpl": file
    }

    try:
        with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
            ydl.download([url])
            logger.debug(f"Downloaded, {(task_id, True, file)}")
            mp_q.put((task_id, True, file))
    except Exception as e:
        logger.warning(e)
        mp_q.put((task_id, False, str(e)))
