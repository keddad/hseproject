from utils import BadID, ParsedData
from .utils import get_page, get_file
from bs4 import BeautifulSoup
from loguru import logger

BASE_LINK = "https://ok.ru/profile/{}"


def _get_link(user_id: str) -> str:
    if not user_id.isdigit():
        raise BadID

    if int(user_id) <= 0:
        raise BadID

    return BASE_LINK.format(user_id)


async def ok(user_id: str) -> ParsedData:
    page_link = _get_link(user_id)

    page = BeautifulSoup(await get_page(page_link), features="html.parser")

    if page.find("h1", {"tsid": "page-not-found"}):
        logger.debug(f"404 for {page_link}")
        raise BadID

    image_element = page.find("img", {"id": "viewImageLinkId"})

    return ParsedData(
        face=await get_file("https:" + image_element["src"]),
        traits={
            "name": [" ".join([x.title() for x in image_element["alt"].split()])],
            "ok_url": [page_link]
        }
    )
