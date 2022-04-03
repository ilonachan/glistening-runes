import logging

from hikari import KnownCustomEmoji

import runicbabble.discord as dc
import re
from kagaconf import cfg

log = logging.getLogger(__name__)


def mdj_format(message):
    message = message.replace('a\'', 'á').replace('A\'', 'á') \
        .replace('e\'', 'é').replace('E\'', 'é') \
        .replace('i\'', 'í').replace('I\'', 'í') \
        .replace('o\'', 'ó').replace('O\'', 'ó') \
        .replace('u\'', 'ú').replace('U\'', 'ú') \
        .replace('y\'', 'ý').replace('Y\'', 'ý') \
        .replace('w\'', '\xb5').replace('W\'', '\xb5')
    return message


emotes = dict()


async def init_emotes():
    standard_characters = 'uoaeyiwUOAEYIWpbtdkgmnqjrlRfFsSxhvVzZ'
    special_mappings = {'ú': 'u_', 'ó': 'o_','á': 'a_','é':'e_','ý': 'y_','í': 'i_','\xb5': 'w_',
                        ' ': 'space', '.': 'dot', ',': 'comma', '?': 'question', '#': 'direction'}

    home_emotes = await dc.bot.rest.fetch_guild_emojis(cfg.discord.home_guild(0))
    emotes_by_name: dict[str, KnownCustomEmoji] = {e.name: e for e in home_emotes}

    for c in standard_characters:
        emotes[c] = emotes_by_name[f'mdj_{c}'].mention
    for c, v in special_mappings.items():
        emotes[c] = emotes_by_name[f'mdj_{v}'].mention
    log.info("reloaded emotes from the home server")


def mdj_emote_format(message):
    return ''.join(emotes[c] if c in emotes else c for c in message)


def render(message: str):
    def handle_mdj(m: re.Match):
        return mdj_emote_format(mdj_format(m.group(1)))

    pattern = r'(?<!\\)`mdj\s([^`]*)`'
    if re.search(pattern, message, re.DOTALL) is None:
        return None

    return {'content': re.sub(pattern, handle_mdj, message, flags=re.DOTALL)}
