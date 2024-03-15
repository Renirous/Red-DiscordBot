import sys
import typing
import discord

# Let's do all the dumb version checking in one place.


if sys.version_info < (3, 5, 2):
    typing.TYPE_CHECKING = False

if discord.version_info.major < 1:
    print("You are not running the rewritten version of discord.py.\n\n"
          "In order to use Red v3 you MUST be running d.py version"
          " >= 1.0.0.")
    sys.exit(1)
