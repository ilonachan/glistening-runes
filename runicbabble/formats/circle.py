from PIL import Image, ImageDraw, ImageFont
import math
from abc import ABC, abstractmethod


class CircleSegment(ABC):
    @property
    @abstractmethod
    def radius(self):
        pass

    @property
    def margin(self):
        return 4

    @abstractmethod
    def render(self, img, draw, circle, radius):
        pass


class CenterNgon(CircleSegment):
    def __init__(self, radius, n_sides, rotation=0.0, fill=None, outline=None, width=1):
        self._radius = radius
        self.n_sides = n_sides
        self.rotation = rotation
        self.fill = fill
        self.outline = outline
        self.width = width

    @property
    def radius(self):
        return self._radius

    @property
    def margin(self):
        return 0

    def render(self, img, draw, circle, radius):
        draw_stellated_regular_polygon(draw, (circle.center, self.radius), self.n_sides,
                                       self.rotation, self.fill, self.outline, self.width)


class TextRing(CircleSegment):
    def __init__(self, text, font, color, rotation=0.0, angle=None, upscale=4):
        self.text = text
        self.font = font
        self.color = color
        self.rotation = rotation
        self.angle = angle or 360 / len(text)
        self.upscale = upscale

    @property
    def radius(self):
        return self.font.size

    def render(self, img, draw, circle, radius):
        angle_rad = self.angle / 360 * 2 * math.pi

        bigger_size = (img.size[0] * self.upscale, img.size[1] * self.upscale)
        bigger_font = self.font.font_variant(size=self.font.size * self.upscale)

        ucx, ucy = circle.center[0] * self.upscale, circle.center[1] * self.upscale
        rad = radius * self.upscale + bigger_font.size / 2

        img2 = Image.new("RGBA", bigger_size, (0, 0, 0, 0))
        for i, c in enumerate(self.text):
            angled = angled_text(c, fill=self.color, font=bigger_font, angle=-90 - self.angle * i)
            text_origin = (ucx + rad * math.cos(angle_rad * i), ucy + rad * math.sin(angle_rad * i))
            img2.paste(angled, box=(int(text_origin[0] - angled.width / 2), int(text_origin[1] - angled.height / 2)))

        img2 = img2.rotate(self.rotation + 90, center=(ucx, ucy)).resize(img.size, resample=Image.LANCZOS)
        img.paste(img2, mask=img2)


class RingSeparator(CircleSegment):
    def __init__(self, style, color):
        self.style = style
        self.color = color

        self.calculate_widths()

    def calculate_widths(self):
        self._widths = []
        for line in self.style:
            try:
                width = int(line)
            except ValueError:
                width = 2
                if line == 's':
                    width = 4
                if line == 'm':
                    width = 7
                if line == 'l':
                    width = 10
            self._widths.append(width)
        self._radius = sum(self._widths) + 4*(len(self._widths)-1)

    @property
    def radius(self):
        return self._radius

    def render(self, img, draw, circle, radius):
        r = radius
        for width in self._widths:
            draw_circle(draw, (circle.center, r + width), width=width, outline=self.color)
            r += width + 4


class MagicCircle:
    def __init__(self, segments=None):
        self.segments = segments or []
        self.radius, self.center = None, None

    def render(self):
        self.radius = sum(seg.radius+seg.margin for seg in self.segments)
        self.center = (self.radius, self.radius)
        img = Image.new("RGBA", (2*self.radius, 2*self.radius), (0, 0, 0, 0))

        draw = ImageDraw.Draw(img)
        draw_circle(draw, (self.center, self.radius), fill=(0, 0, 0))

        r = 0
        for seg in self.segments:
            seg.render(img, draw, self, r)
            r += seg.radius+seg.margin
        return img


def _extract_circle(circle):
    if len(circle) == 3:
        return tuple(circle)
    elif len(circle) == 2 and len(circle[0]) == 2:
        return circle[0][0], circle[0][1], circle[1]
    else:
        raise ValueError


def draw_stellated_regular_polygon(draw, bounding_circle, n_sides, rotation=0.0, fill=None, outline=None, width=1):
    step = n_sides / 2 - (1 if n_sides % 2 == 0 else 1 / 2)

    cx, cy, r = _extract_circle(bounding_circle)

    def point_on_circle(k):
        return r*math.cos(k/n_sides*2*math.pi+rotation)+cx, r*math.sin(k/n_sides*2*math.pi+rotation)+cy

    if fill is not None:
        for i in range(n_sides):
            curr = point_on_circle(i)
            next = point_on_circle(i+step)
            draw.polygon([curr, next, (cx, cy)], fill=fill, outline=None)

    if outline is not None:
        for i in range(n_sides):
            curr = point_on_circle(i)
            next = point_on_circle(i+step)
            draw.line([curr, next], fill=outline, width=width)


def angled_text(text, fill=None, font=None, angle=0.0):
    size = font.getsize_multiline(text)
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    draw.text((0, 0), text, font=font, fill=fill)
    return im.rotate(angle, expand=True)


def circle_text(img, text, base_circle, rotation, font: ImageFont.FreeTypeFont, color, angle=None, upscale=4):
    if angle is None:
        angle = 360 / len(text)
    angle_rad = angle/360*2*math.pi

    bigger_size = (img.size[0]*upscale, img.size[1]*upscale)
    bigger_font = font.font_variant(size=font.size*upscale)

    cx, cy, r = _extract_circle(base_circle)
    ucx, ucy = cx*upscale, cy*upscale
    rad = r*upscale + bigger_font.size / 2

    img2 = Image.new("RGBA", bigger_size, (0, 0, 0, 0))
    for i, c in enumerate(text):
        angled = angled_text(c, fill=color, font=bigger_font, angle=-90-angle*i)
        text_origin = (ucx + rad*math.cos(angle_rad*i), ucy + rad*math.sin(angle_rad*i))
        img2.paste(angled, box=(int(text_origin[0]-angled.width/2), int(text_origin[1]-angled.height/2)))

    img2 = img2.rotate(rotation+90, center=(ucx, ucy)).resize(img.size, resample=Image.LANCZOS)
    img.paste(img2, mask=img2)

    return r + font.size + 4


def draw_circle(draw, bounding_circle, fill=None, outline=None, width=None):
    cx, cy, r = _extract_circle(bounding_circle)
    draw.ellipse([(cx-r, cy-r), (cx+r, cy+r)], fill, outline, width)


def draw_circle_separator(draw, base_circle, style, color):
    cx, cy, r = _extract_circle(base_circle)
    c = (cx, cy)

    for letter in style:
        width = 2
        if letter == 's':
            width = 4
        if letter == 'm':
            width = 7
        if letter == 'l':
            width = 10
        draw_circle(draw, (c, r + width), width=width, outline=color)
        r += width + 3
    return r


def main():
    msg1 = '#hey dok'
    color = (100, 200, 255)
    font = ImageFont.truetype("../../config/res/fonts/Madouji", 60)
    
    mc = MagicCircle([
        CenterNgon(380, len(msg1), rotation=-math.pi/2, outline=color, width=6),
        RingSeparator('m', color),
        TextRing(msg1, font.font_variant(size=120), color),
        RingSeparator('ss', color),
        TextRing('ayv ymprUvd may progrem, so naó yt dZenereýtz VIz swrklz Iseli. ', font.font_variant(size=30), color),
        RingSeparator('m', color),
        TextRing('Vetz pryti nyfti ay úud sey. ', font.font_variant(size=60), color),
        RingSeparator('sl', color)
    ])
    
    img = mc.render()
    img.show()
    img.save('output.png')


if __name__ == '__main__':
    main()
