import runicbabble.lang
import re


class Madouji(runicbabble.lang.Language):
    @property
    def name(self):
        return 'madouji'

    def is_responsible(self, message):
        return re.match(r'^```mdj(-\d+!?)?\s.*```$', message, re.DOTALL) is not None

    def format(self, message):
        m = re.match(r'^```mdj(?P<wrap>-\d+!?)?\s(?P<msg>.*)```$', message, re.DOTALL)
        txt = m.group('msg').strip()
        txt = txt.replace('a\'', 'á').replace('A\'', 'á')\
            .replace('e\'', 'é').replace('E\'', 'é')\
            .replace('i\'', 'í').replace('I\'', 'í')\
            .replace('o\'', 'ó').replace('O\'', 'ó')\
            .replace('u\'', 'ú').replace('U\'', 'ú')\
            .replace('y\'', 'ý').replace('Y\'', 'ý')\
            .replace('w\'', '\xb5').replace('W\'', '\xb5')

        if m.group('wrap') is not None:
            wrap = m.group('wrap')[1:]
            if wrap.endswith('!'):
                wrap = int(wrap[:-1])
                res = ''
                cursor = 0
                while cursor < len(txt):
                    skip = cursor+wrap
                    find = txt.find('\n', cursor, skip)
                    if find != -1:
                        skip = find+1
                    res += txt[cursor:skip]
                    cursor = skip
                    if find == -1 and cursor < len(txt)-1:
                        res += '\n'
                txt = res
            else:
                # TODO: implement clever word wrapping
                wrap = int(wrap)
                res = ''
                linestart = 0
                split1 = 0
                cursor = 0
                while cursor < len(txt):
                    if txt[cursor] == ' ' or txt[cursor] == '\n':
                        if cursor-linestart >= wrap:
                            res += '\n'
                            linestart = split1
                        res += txt[split1:cursor+1]
                        split1 = cursor+1
                        if txt[cursor] == '\n':
                            linestart = split1
                    cursor += 1
                if cursor - linestart >= wrap:
                    res += '\n'
                res += txt[split1:cursor]
                txt = res

        return txt

    def font_path(self, message):
        return 'config/res/fonts/Madouji.ttf'
