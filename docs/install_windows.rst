.. windows installation docs

=========================
Installing Red on Windows
=========================

---------------
Needed Software
---------------

* `Python <https://python.org/downloads/>`_ - Red needs at least Python 3.5

.. attention:: Please note that 3.6 has issues on some versions of Windows.
               If you try using Red with 3.6 and experience issues, uninstall
               Python 3.6 and install the latest version of Python 3.5

.. note:: Please make sure that the box to add Python to PATH is CHECKED, otherwise
          you may run into issues when trying to run Red

* `Git <https://git-scm.com/download/win>`_

.. attention:: Please choose the option to "Run Git from the Windows Command Prompt" in Git's setup

--------------
Installing Red
--------------

1. Open a command prompt (open Start, search for "command prompt", then click it)
2. Run the appropriate command, depending on if you want audio or not

  * No audio: :code:`python -m pip install -U --process-dependency-links Red-DiscordBot`
  * Audio: :code:`python -m pip install -U --process-dependency-links Red-DiscordBot[voice]`
  * Development version (without audio): :code:`python -m pip install -U --process-dependency-links git+https://github.com/Cog-Creators/Red-DiscordBot@V3/develop#egg=red-discordbot`
  * Development version (with audio): :code:`python -m pip install -U --process-dependency-links git+https://github.com/Cog-Creators/Red-DiscordBot@V3/develop#egg=red-discordbot[voice]`

3. Once that has completed, run :code:`redbot-setup` to set up your instance

  * This will set the location where data will be stored, as well as your
    storage backend and the name of the instance (which will be used for
    running the bot)

4. Once done setting up the instance, run :code:`redbot <your instance name>` to run Red.
   It will walk through the initial setup, asking for your token and a prefix