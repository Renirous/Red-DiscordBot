import pkgutil
from importlib import invalidate_caches
from importlib.machinery import ModuleSpec
from pathlib import Path
from typing import Tuple, Union, List

from . import checks
from .config import Config
from .i18n import CogI18n
from .data_manager import cog_data_path
from discord.ext import commands

from .utils.chat_formatting import box

__all__ = ["CogManager"]


class CogManager:
    """Directory manager for Red's cogs.

    This module allows you to load cogs from multiple directories and even from
    outside the bot directory. You may also set a directory for downloader to
    install new cogs to, the default being the :code:`cogs/` folder in the root
    bot directory.
    """
    def __init__(self, paths: Tuple[str]=()):
        self.conf = Config.get_conf(self, 2938473984732, True)
        tmp_cog_install_path = cog_data_path(self) / "cogs"
        tmp_cog_install_path.mkdir(parents=True, exist_ok=True)
        self.conf.register_global(
            paths=(),
            install_path=str(tmp_cog_install_path)
        )

        self._paths = list(paths)

    async def paths(self) -> Tuple[Path, ...]:
        """Get all currently valid path directories.

        Returns
        -------
        `tuple` of `pathlib.Path`
            All valid cog paths.

        """
        conf_paths = await self.conf.paths()
        other_paths = self._paths

        all_paths = set(list(conf_paths) + list(other_paths))

        paths = [Path(p) for p in all_paths]
        if self.install_path not in paths:
            paths.insert(0, await self.install_path())
        return tuple(p.resolve() for p in paths if p.is_dir())

    async def install_path(self) -> Path:
        """Get the install path for 3rd party cogs.

        Returns
        -------
        pathlib.Path
            The path to the directory where 3rd party cogs are stored.

        """
        p = Path(await self.conf.install_path())
        return p.resolve()

    async def set_install_path(self, path: Path) -> Path:
        """Set the install path for 3rd party cogs.

        Note
        ----
        The bot will not remember your old cog install path which means
        that **all previously installed cogs** will no longer be found.

        Parameters
        ----------
        path : pathlib.Path
            The new directory for cog installs.

        Returns
        -------
        pathlib.Path
            Absolute path to the new install directory.

        Raises
        ------
        ValueError
            If :code:`path` is not an existing directory.

        """
        if not path.is_dir():
            raise ValueError("The install path must be an existing directory.")
        resolved = path.resolve()
        await self.conf.install_path.set(str(resolved))
        return resolved

    @staticmethod
    def _ensure_path_obj(path: Union[Path, str]) -> Path:
        """Guarantee an object will be a path object.

        Parameters
        ----------
        path : `pathlib.Path` or `str`

        Returns
        -------
        pathlib.Path

        """
        try:
            path.exists()
        except AttributeError:
            path = Path(path)
        return path

    async def add_path(self, path: Union[Path, str]):
        """Add a cog path to current list.

        This will ignore duplicates. Does have a side effect of removing all
        invalid paths from the saved path list.

        Parameters
        ----------
        path : `pathlib.Path` or `str`
            Path to add.

        Raises
        ------
        ValueError
            If :code:`path` does not resolve to an existing directory.

        """
        path = self._ensure_path_obj(path)

        # This makes the path absolute, will break if a bot install
        # changes OS/Computer?
        path = path.resolve()

        if not path.is_dir():
            raise ValueError("'{}' is not a valid directory.".format(path))

        if path == await self.install_path():
            raise ValueError("Cannot add the install path as an additional path.")

        all_paths = set(await self.paths() + (path, ))
        # noinspection PyTypeChecker
        await self.set_paths(all_paths)

    async def remove_path(self, path: Union[Path, str]) -> Tuple[Path, ...]:
        """Remove a path from the current paths list.

        Parameters
        ----------
        path : `pathlib.Path` or `str`
            Path to remove.

        Returns
        -------
        `tuple` of `pathlib.Path`
            Tuple of new valid paths.

        """
        path = self._ensure_path_obj(path)
        all_paths = list(await self.paths())
        if path in all_paths:
            all_paths.remove(path)  # Modifies in place
            await self.set_paths(all_paths)
        return tuple(all_paths)

    async def set_paths(self, paths_: List[Path]):
        """Set the current paths list.

        Parameters
        ----------
        paths_ : `list` of `pathlib.Path`
            List of paths to set.

        """
        str_paths = [str(p) for p in paths_]
        await self.conf.paths.set(str_paths)

    async def find_cog(self, name: str) -> ModuleSpec:
        """Find a cog in the list of available paths.

        Parameters
        ----------
        name : str
            Name of the cog to find.

        Returns
        -------
        importlib.machinery.ModuleSpec
            A module spec to be used for specialized cog loading.

        Raises
        ------
        RuntimeError
            If there is no cog with the given name.

        """
        resolved_paths = [str(p.resolve()) for p in await self.paths()]
        for finder, module_name, _ in pkgutil.iter_modules(resolved_paths):
            if name == module_name:
                spec = finder.find_spec(name)
                if spec:
                    return spec

        raise RuntimeError("No module by the name of '{}' was found"
                           " in any available path.".format(name))

    @staticmethod
    def invalidate_caches():
        """Re-evaluate modules in the py cache.

        This is an alias for an importlib internal and should be called
        any time that a new module has been installed to a cog directory.
        """
        invalidate_caches()


_ = CogI18n("CogManagerUI", __file__)


class CogManagerUI:
    @commands.command()
    @checks.is_owner()
    async def paths(self, ctx: commands.Context):
        """
        Lists current cog paths in order of priority.
        """
        install_path = await ctx.bot.cog_mgr.install_path()
        cog_paths = await ctx.bot.cog_mgr.paths()
        cog_paths = [p for p in cog_paths if p != install_path]

        msg = _("Install Path: {}\n\n").format(install_path)

        partial = []
        for i, p in enumerate(cog_paths, start=1):
            partial.append("{}. {}".format(i, p))

        msg += "\n".join(partial)
        await ctx.send(box(msg))

    @commands.command()
    @checks.is_owner()
    async def addpath(self, ctx: commands.Context, path: Path):
        """
        Add a path to the list of available cog paths.
        """
        if not path.is_dir():
            await ctx.send(_("That path is does not exist or does not"
                             " point to a valid directory."))
            return

        try:
            await ctx.bot.cog_mgr.add_path(path)
        except ValueError as e:
            await ctx.send(str(e))
        else:
            await ctx.send(_("Path successfully added."))

    @commands.command()
    @checks.is_owner()
    async def removepath(self, ctx: commands.Context, path_number: int):
        """
        Removes a path from the available cog paths given the path_number
            from !paths
        """
        cog_paths = await ctx.bot.cog_mgr.paths()
        try:
            to_remove = cog_paths[path_number]
        except IndexError:
            await ctx.send(_("That is an invalid path number."))
            return

        await ctx.bot.cog_mgr.remove_path(to_remove)
        await ctx.send(_("Path successfully removed."))

    @commands.command()
    @checks.is_owner()
    async def reorderpath(self, ctx: commands.Context, from_: int, to: int):
        """
        Reorders paths internally to allow discovery of different cogs.
        """
        # Doing this because in the paths command they're 1 indexed
        from_ -= 1
        to -= 1

        all_paths = list(await ctx.bot.cog_mgr.paths())
        try:
            to_move = all_paths.pop(from_)
        except IndexError:
            await ctx.send(_("Invalid 'from' index."))
            return

        try:
            all_paths.insert(to, to_move)
        except IndexError:
            await ctx.send(_("Invalid 'to' index."))
            return

        await ctx.bot.cog_mgr.set_paths(all_paths)
        await ctx.send(_("Paths reordered."))

    @commands.command()
    @checks.is_owner()
    async def installpath(self, ctx: commands.Context, path: Path=None):
        """
        Returns the current install path or sets it if one is provided.
            The provided path must be absolute or relative to the bot's
            directory and it must already exist.

        No installed cogs will be transferred in the process.
        """
        if path:
            if not path.is_absolute():
                path = (ctx.bot.main_dir / path).resolve()
            try:
                await ctx.bot.cog_mgr.set_install_path(path)
            except ValueError:
                await ctx.send(_("That path does not exist."))
                return

        install_path = await ctx.bot.cog_mgr.install_path()
        await ctx.send(_("The bot will install new cogs to the `{}`"
                         " directory.").format(install_path))
