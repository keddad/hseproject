from utils import BadID, ParsedData
from .utils import get_page, get_file
from bs4 import BeautifulSoup
from loguru import logger

BASE_LINK = "https://vk.com/{}"


def _get_page_link(user_id: str) -> str:
    if user_id.isdigit():
        if int(user_id) <= 0:
            raise ValueError
        page_link = BASE_LINK.format(f"id{user_id}")
    else:
        page_link = BASE_LINK.format(user_id)

    return page_link


async def _get_quality_photo(page: BeautifulSoup) -> bytes:
    raise NotImplementedError # TODO: Отреверсить vk.com/al_photos.php
    if (ppl := page.find("a", {"id": "profile_photo_link"})) is not None:
        photo_page = BeautifulSoup(await get_page(BASE_LINK.format(ppl["href"][1:])))
        photo_link = photo_page.find("div", {"id": "pv_photo"}).find("img")["src"]

        return await get_file(photo_link)

    raise ValueError


async def vk(user_id: str) -> ParsedData:
    page_link = _get_page_link(user_id)

    page = BeautifulSoup(await get_page(page_link), features="html.parser")

    if page.find("img", {"src": "/images/pics/spamfight.gif"}) or (
            page.find("div", {"class": "message_page_title"}) and page.title == "Information"):
        logger.debug(f"Bad user {page_link}")
        raise BadID

    image_element = page.find("img", {"class": "page_avatar_img"})

    if image_element is None or "alt" not in image_element.attrs:
        logger.debug("Группа или недоступная страница")
        raise BadID

    user_name = image_element["alt"]
    image: bytes

    try:
        image = await _get_quality_photo(page)
    except Exception as e:
        logger.debug(f"Failed to fetch hires image for {page_link}")
        image = await get_file(image_element["src"])

    return ParsedData(face=image, traits={"name": [user_name], "vk_url": [page_link]})
