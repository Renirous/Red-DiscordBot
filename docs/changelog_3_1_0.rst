.. v3.1.0 Changelog

================
v3.1.0 Changelog
================

-----
Audio
-----

 * Bot will no longer complain about permissions when trying to connect to user-limited channel, if it has "Move Members" permission (`#2525`_)

----
Core
----

 * ``redbot --version`` will now give you current version of Red (`#2567`_)

------
Config
------

 * Updated Mongo driver to support large guilds (`#2536`_)
 * Introduced ``init_custom`` method on Config objects (`#2545`_)
 * We now record custom group primary key lengths in the core config object (`#2550`_)
 * Migrated internal UUIDs to maintain cross platform consistency (`#2604`_)

----------
discord.py
----------

----------
Downloader
----------

 * ``[p]cog install`` will now tell user that cog has to be loaded (`#2523`_)
 * Fixed bug, that caused Downloader to include submodules on cog list (`#2590`_)
 * ``[p]cog uninstall`` allows to uninstall multiple cogs now (`#2592`_)
 * ``[p]cog uninstall`` will now remove cog from installed cogs even if it can't find the cog in install path anymore (`#2595`_)

---
Mod
---

 * Admins can now decide how many times message has to be repeated before ``deleterepeats`` removes it (`#2437`_)

-------------
Setup Scripts
-------------

 * ``redbot-setup`` now uses the click CLI library (`#2579`_)
 * ``redbot-setup convert`` now used to convert between libraries (`#2579`_)
 * Backup support for Mongo is currently broken (`#2579`_)

-----
Tests
-----

 * Test for ``trivia`` cog uses explicitly utf-8 encoding for checking yaml files (`#2565`_)

------
Trivia
------

 * Fix of dead image link for Sao Tome and Principe in ``worldflags`` trivia (`#2540`_)

-----------------
Utility Functions
-----------------

 * ``Tunnel`` - Spelling correction of method name - changed ``files_from_attatch`` to ``files_from_attach`` (old name is left for backwards compatibility) (`#2496`_)
 * ``Tunnel`` - fixed behavior of ``react_close()``, now when tunnel closes message will be sent to other end (`#2507`_)

.. _#2437: https://github.com/Cog-Creators/Red-DiscordBot/pull/2437
.. _#2496: https://github.com/Cog-Creators/Red-DiscordBot/pull/2496
.. _#2507: https://github.com/Cog-Creators/Red-DiscordBot/pull/2507
.. _#2523: https://github.com/Cog-Creators/Red-DiscordBot/pull/2523
.. _#2525: https://github.com/Cog-Creators/Red-DiscordBot/pull/2525
.. _#2536: https://github.com/Cog-Creators/Red-DiscordBot/pull/2536
.. _#2540: https://github.com/Cog-Creators/Red-DiscordBot/pull/2540
.. _#2545: https://github.com/Cog-Creators/Red-DiscordBot/pull/2545
.. _#2550: https://github.com/Cog-Creators/Red-DiscordBot/pull/2550
.. _#2565: https://github.com/Cog-Creators/Red-DiscordBot/pull/2565
.. _#2567: https://github.com/Cog-Creators/Red-DiscordBot/pull/2567
.. _#2579: https://github.com/Cog-Creators/Red-DiscordBot/pull/2579
.. _#2590: https://github.com/Cog-Creators/Red-DiscordBot/pull/2590
.. _#2592: https://github.com/Cog-Creators/Red-DiscordBot/pull/2592
.. _#2595: https://github.com/Cog-Creators/Red-DiscordBot/pull/2595
.. _#2604: https://github.com/Cog-Creators/Red-DiscordBot/pull/2604
