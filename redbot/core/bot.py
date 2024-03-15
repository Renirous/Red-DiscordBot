import asyncio
import os
from collections import Counter
from enum import Enum
from importlib.machinery import ModuleSpec
from pathlib import Path

import discord
from discord.ext.commands.bot import BotBase
from discord.ext.commands import GroupMixin

from .cog_manager import CogManager
from . import Config, i18n, RedContext


class RedBase(BotBase):
    """Mixin for the main bot class.

    This exists because `Red` inherits from `discord.AutoShardedClient`, which
    is something other bot classes (namely selfbots) may not want to have as
    a parent class.
    
    Selfbots should inherit from this mixin along with `discord.Client`.
    """
    def __init__(self, cli_flags, bot_dir: Path=Path.cwd(), **kwargs):
        self._shutdown_mode = ExitCodes.CRITICAL
        self.db = Config.get_core_conf(force_registration=True)
        self._co_owners = cli_flags.co_owner

        self.db.register_global(
            token=None,
            prefix=[],
            packages=[],
            owner=None,
            whitelist=[],
            blacklist=[],
            enable_sentry=None,
            locale='en'
        )

        self.db.register_guild(
            prefix=[],
            whitelist=[],
            blacklist=[],
            admin_role=None,
            mod_role=None
        )

        async def prefix_manager(bot, message):
            if not cli_flags.prefix:
                global_prefix = await bot.db.prefix()
            else:
                global_prefix = cli_flags.prefix
            if message.guild is None:
                return global_prefix
            server_prefix = await bot.db.guild(message.guild).prefix()
            return server_prefix if server_prefix else global_prefix

        if "command_prefix" not in kwargs:
            kwargs["command_prefix"] = prefix_manager

        if cli_flags.owner and "owner_id" not in kwargs:
            kwargs["owner_id"] = cli_flags.owner

        if "owner_id" not in kwargs:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._dict_abuse(kwargs))

        self.counter = Counter()
        self.uptime = None

        self.main_dir = bot_dir

        self.cog_mgr = CogManager(paths=(str(self.main_dir / 'cogs'),))

        super().__init__(**kwargs)

    async def _dict_abuse(self, indict):
        """
        Please blame <@269933075037814786> for this.

        :param indict:
        :return:
        """

        indict['owner_id'] = await self.db.owner()
        i18n.set_locale(await self.db.locale())

    async def is_owner(self, user):
        if user.id in self._co_owners:
            return True
        return await super().is_owner(user)

    async def get_context(self, message, *, cls=RedContext):
        return await super().get_context(message, cls=cls)

    def list_packages(self):
        """Lists packages present in the cogs the folder"""
        return os.listdir("cogs")

    async def save_packages_status(self, packages):
        await self.db.packages.set(packages)

    async def add_loaded_package(self, pkg_name: str):
        curr_pkgs = await self.db.packages()
        if pkg_name not in curr_pkgs:
            curr_pkgs.append(pkg_name)
            await self.save_packages_status(curr_pkgs)

    async def remove_loaded_package(self, pkg_name: str):
        curr_pkgs = await self.db.packages()
        if pkg_name in curr_pkgs:
            await self.save_packages_status([p for p in curr_pkgs if p != pkg_name])

    def load_extension(self, spec: ModuleSpec):
        name = spec.name.split('.')[-1]
        if name in self.extensions:
            return

        lib = spec.loader.load_module()
        if not hasattr(lib, 'setup'):
            del lib
            raise discord.ClientException('extension does not have a setup function')

        lib.setup(self)
        self.extensions[name] = lib

    def unload_extension(self, name):
        lib = self.extensions.get(name)
        if lib is None:
            return

        lib_name = lib.__name__  # Thank you

        # find all references to the module

        # remove the cogs registered from the module
        for cogname, cog in self.cogs.copy().items():
            if cog.__module__.startswith(lib_name):
                self.remove_cog(cogname)

        # first remove all the commands from the module
        for cmd in self.all_commands.copy().values():
            if cmd.module.startswith(lib_name):
                if isinstance(cmd, GroupMixin):
                    cmd.recursively_remove_all_commands()
                self.remove_command(cmd.name)

        # then remove all the listeners from the module
        for event_list in self.extra_events.copy().values():
            remove = []
            for index, event in enumerate(event_list):
                if event.__module__.startswith(lib_name):
                    remove.append(index)

            for index in reversed(remove):
                del event_list[index]

        try:
            func = getattr(lib, 'teardown')
        except AttributeError:
            pass
        else:
            try:
                func(self)
            except:
                pass
        finally:
            # finally remove the import..
            del lib
            del self.extensions[name]
            # del sys.modules[name]


class Red(RedBase, discord.AutoShardedClient):
    """
    You're welcome Caleb.
    """
    async def shutdown(self, *, restart: bool=False):
        """Gracefully quit Red.
        
        The program will exit with code :code:`0` by default.

        Parameters
        ----------
        restart : bool
            If :code:`True`, the program will exit with code :code:`26`. If the
            launcher sees this, it will attempt to restart the bot.

        """
        if not restart:
            self._shutdown_mode = ExitCodes.SHUTDOWN
        else:
            self._shutdown_mode = ExitCodes.RESTART

        await self.logout()


class ExitCodes(Enum):
    CRITICAL = 1
    SHUTDOWN = 0
    RESTART  = 26
