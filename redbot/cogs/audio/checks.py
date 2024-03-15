from redbot.core import Config, commands

from .apis import HAS_SQL

_config = None


def _pass_config_to_checks(config: Config):
    global _config
    if _config is None:
        _config = config


def roomlocked():
    """Deny the command if the bot has been room locked."""

    async def predicate(ctx: commands.Context):
        if ctx.guild is None:
            return False
        if await ctx.bot.is_mod(member=ctx.author):
            return True

        room_id = await _config.guild(ctx.guild).room_lock()
        if room_id is None or ctx.channel.id == room_id:
            return True
        return False

    return commands.check(predicate)


def can_have_caching():
    """Check to disable Caching commands if SQLite is not avaliable."""

    async def predicate(ctx: commands.Context):
        return HAS_SQL

    return commands.check(predicate)
