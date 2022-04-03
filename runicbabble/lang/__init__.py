from PIL import Image, ImageDraw, ImageFont
from abc import ABC, abstractmethod
import logging
log = logging.getLogger(__name__)

langs = []


class Language(ABC):
    def register(self):
        langs.append(self)
        log.info(f'Registered language {self.name}')

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def is_responsible(self, message):
        pass

    @abstractmethod
    def format(self, message):
        pass

    @abstractmethod
    def font_path(self, message):
        pass

    def render_message(self, message, fontsize):
        if not self.is_responsible(message):
            return None
        path = self.font_path(message)
        msg = self.format(message)

        font = ImageFont.truetype(path, fontsize)
        size = font.getsize_multiline(msg)
        img = Image.new("RGBA", size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.text((0, 0), msg, (255, 255, 255), font=font)
        return img


def render(message, fontsize=32):
    img = None
    for lang in langs:
        img = lang.render_message(message, fontsize)
        if img is not None:
            break

    return img
