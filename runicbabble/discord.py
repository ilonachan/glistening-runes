import logging

from typing import Any, Sequence, Union, Optional

import hikari
import lightbulb
from hikari import Embed, Resourceish, UNDEFINED, UndefinedOr, PartialRole, URL, \
    UndefinedType, Message
from hikari.presences import Status, Activity, ActivityType
from hikari.errors import NotFoundError, ForbiddenError
from hikari.api import ComponentBuilder
from hikari.snowflakes import Snowflakeish, SnowflakeishOr, SnowflakeishSequence
from hikari.webhooks import IncomingWebhook, ExecutableWebhook
from hikari.channels import *
from hikari.users import *
from hikari.events import *

import runicbabble.formats.mdj_image
import runicbabble.formats.mdj_emotes
from kagaconf import cfg

log = logging.getLogger(__name__)


class CustomHelp(lightbulb.DefaultHelpCommand):
    async def send_bot_help(self, ctx: lightbulb.Context) -> None:
        await ctx.respond("**Runic Babble** converts ASCII text into the constructed writing system Madouji, "
                          "created by the Cult of 74.\n\n"
                          "To learn more, visit the official server: https://discord.gg/mg4mCZGFq9")


guild_ids = cfg.discord.slash_command_guilds(None)
if cfg.discord.global_slash_commands(False):
    guild_ids = None

bot = lightbulb.BotApp(intents=hikari.Intents.ALL_UNPRIVILEGED | hikari.Intents.MESSAGE_CONTENT, banner=None,
                       token=cfg.discord.bot_token(),
                       help_class=CustomHelp,
                       default_enabled_guilds=guild_ids)


@bot.listen(hikari.events.ShardReadyEvent)
async def on_ready(event):
    log.info('Logged on as {0}!'.format(bot.get_me()))
    await runicbabble.formats.mdj_emotes.init_emotes()

webhooks: dict[Snowflakeish, ExecutableWebhook] = {}


async def send_as_webhook(
        channel: SnowflakeishOr[TextableChannel],
        content: UndefinedOr[Any] = UNDEFINED, *,
        user: UndefinedOr[SnowflakeishOr[User]] = UNDEFINED,
        username: UndefinedOr[str] = UNDEFINED, avatar_url: Union[UndefinedType, str, URL] = UNDEFINED,
        attachment: UndefinedOr[Resourceish] = UNDEFINED, attachments: UndefinedOr[Sequence[Resourceish]] = UNDEFINED,
        component: UndefinedOr[ComponentBuilder] = UNDEFINED,
        components: UndefinedOr[Sequence[ComponentBuilder]] = UNDEFINED,
        embed: UndefinedOr[Embed] = UNDEFINED, embeds: UndefinedOr[Sequence[Embed]] = UNDEFINED,
        tts: UndefinedOr[bool] = UNDEFINED, mentions_everyone: UndefinedOr[bool] = UNDEFINED,
        user_mentions: UndefinedOr[Union[SnowflakeishSequence[PartialUser], bool]] = UNDEFINED,
        role_mentions: UndefinedOr[Union[SnowflakeishSequence[PartialRole], bool]] = UNDEFINED) -> Optional[Message]:

    if user is not UNDEFINED:
        if username is UNDEFINED or avatar_url is UNDEFINED:
            if not isinstance(user, User):
                user = await bot.rest.fetch_user(user)
            if username is UNDEFINED:
                username = user.username
            if avatar_url is UNDEFINED:
                avatar_url = user.make_avatar_url()

    try:
        if int(channel) not in webhooks:
            try:
                whs = await bot.rest.fetch_channel_webhooks(channel)
            except NotFoundError:
                log.info("Hikari has not yet implemented threads, and possibly webhooks can't be used in threads")
                return None
            for wh in whs:
                if isinstance(wh, IncomingWebhook) and wh.name == f'runicbabble-{int(channel)}':
                    log.info(f'Webhook for channel {int(channel)} was found, reusing')
                    webhooks[int(channel)] = wh
                    break
            else:
                log.info(f'No existing webhook for channel {int(channel)} was found, creating')
                webhooks[int(channel)] = await bot.rest.create_webhook(channel, f'runicbabble-{int(channel)}')
        webhook: ExecutableWebhook = webhooks[int(channel)]

        try:
            return await webhook.execute(content=content, username=username, avatar_url=avatar_url,
                                         attachment=attachment, attachments=attachments,
                                         component=component, components=components,
                                         embed=embed, embeds=embeds, tts=tts,
                                         mentions_everyone=mentions_everyone,
                                         user_mentions=user_mentions, role_mentions=role_mentions)
        except NotFoundError:
            log.info(f'Previously known webhook for channel {int(channel)} was deleted, recreating')
            webhooks[int(channel)] = await bot.rest.create_webhook(channel, f'runicbabble-{int(channel)}')
            return await webhook.execute(content=content, username=username, avatar_url=avatar_url,
                                         attachment=attachment, attachments=attachments,
                                         component=component, components=components,
                                         embed=embed, embeds=embeds, tts=tts,
                                         mentions_everyone=mentions_everyone,
                                         user_mentions=user_mentions, role_mentions=role_mentions)
    except ForbiddenError:
        log.warning(f'Insufficient permissions for creating fancy webhooks')
        return None


@bot.listen()
async def on_message(event: GuildMessageCreateEvent):
    if event.content is None:
        return
    params = runicbabble.formats.mdj_emotes.render(event.content)
    if params is not None:
        await event.message.delete()
        if await send_as_webhook(event.channel_id, user=event.author, **params) is None:
            # if webhooks don't work, just send it yourself~
            await bot.rest.create_message(event.channel_id, **params)


@bot.command
@lightbulb.option("content", "The message to be rendered", str, required=True)
@lightbulb.option("wrap", "What line wrapping model to use", str, choices=["none", "flow", "force"], default="none")
@lightbulb.option("line_width", "max amount of characters in a line", int, default=8)
@lightbulb.command("mdj", description="Render the entire message as Madouji", ephemeral=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def slash_mdj(ctx: lightbulb.SlashContext):
    content = ctx.options.content
    wrap = ctx.options.wrap
    line_width = ctx.options.line_width
    params = runicbabble.formats.mdj_image.render(content, 32, wrap, line_width)
    if await send_as_webhook(ctx.channel_id, user=ctx.user, **params):
        await ctx.respond('\u200d', delete_after=1)
    else:
        # if webhooks don't work, just send it yourself
        await bot.rest.create_message(ctx.channel_id, **params)
        #await ctx.respond(**params)


def start():
    try:
        bot.run(status=Status.ONLINE, activity=Activity(type=ActivityType.LISTENING, name="the whispers of the otherworld"))
    except KeyError:
        log.error('No bot token was specified; the Discord bot can not be started.')
