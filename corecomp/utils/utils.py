from PIL import Image
import io


def image_valid(in_image: bytes) -> bool:
    try:
        Image.open(io.BytesIO(in_image))
    except IOError:
        return False
    else:
        return True
