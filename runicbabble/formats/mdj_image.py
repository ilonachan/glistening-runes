import io

import hikari
from PIL import Image, ImageDraw, ImageFont
from .mdj_emotes import mdj_format


def text_wrap(message, line_length=8, force=False):
    if force:
        res = ''
        cursor = 0
        while cursor < len(message):
            skip = cursor + line_length
            find = message.find('\n', cursor, skip)
            if find != -1:
                skip = find + 1
            res += message[cursor:skip]
            cursor = skip
            if find == -1 and cursor < len(message) - 1:
                res += '\n'
        message = res
    else:
        # TODO: implement clever word wrapping
        res = ''
        linestart = 0
        split1 = 0
        cursor = 0
        while cursor < len(message):
            if message[cursor] == ' ' or message[cursor] == '\n':
                if cursor - linestart >= line_length:
                    res += '\n'
                    linestart = split1
                res += message[split1:cursor + 1]
                split1 = cursor + 1
                if message[cursor] == '\n':
                    linestart = split1
            cursor += 1
        if cursor - linestart >= line_length:
            res += '\n'
        res += message[split1:cursor]
        message = res

    return message


def render(message: str, fontsize: int, wrap: str = 'none', line_length: int = 8):
    path = 'config/res/fonts/Madouji.ttf'
    msg = mdj_format(message)
    if wrap != 'none':
        msg = text_wrap(msg, line_length=line_length, force=(wrap == 'force'))

    font = ImageFont.truetype(path, fontsize)
    size = font.getsize_multiline(msg)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text((0, 0), msg, (255, 255, 255), font=font)

    with io.BytesIO() as image_binary:
        img.save(image_binary, 'PNG')
        image_binary.seek(0)
        img_file = hikari.files.Bytes(image_binary, 'mdj.png')

    return {'attachment': img_file}
