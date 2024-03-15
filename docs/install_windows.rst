.. _windows-install-guide:

=========================
Installing Red on Windows
=========================

---------------
Needed Software
---------------

The following software dependencies can all be installed quickly and easily through PowerShell,
using a trusted package manager for Windows called `Chocolatey <https://chocolatey.org>`_

We also provide instructions for manually installing all of the dependencies.

******************************************
Installing using powershell and chocolatey
******************************************

To install via PowerShell, search "powershell" in the Windows start menu,
right-click on it and then click "Run as administrator"

Then run each of the following commands:

.. code-block:: none

    Set-ExecutionPolicy Bypass -Scope Process -Force
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    choco install git --params "/GitOnlyOnPath /WindowsTerminal" -y
    choco install visualstudio2019-workload-vctools -y
    choco install python3 -y

For Audio support, you should also run the following command before exiting:

.. code-block:: none

    choco install adoptopenjdk11jre -y


From here, exit the prompt then continue onto `installing Red <installing-red-windows>`.

********************************
Manually installing dependencies
********************************

.. attention:: There are additional configuration steps required which are
               not documented for installing dependencies manually.
               These dependencies are only listed seperately here for
               reference purposes.

* `MSVC Build tools <https://www.visualstudio.com/downloads/#build-tools-for-visual-studio-2019>`_

* `Python <https://www.python.org/downloads/>`_ - Red needs Python 3.8.1 or greater

.. attention:: Please make sure that the box to add Python to PATH is CHECKED, otherwise
               you may run into issues when trying to run Red.

* `Git <https://git-scm.com/download/win>`_

.. attention:: Please choose the option to "Git from the command line and also from 3rd-party software" in Git's setup.

* `Java <https://adoptopenjdk.net/?variant=openjdk11&jvmVariant=hotspot>`_ - needed for Audio


.. _installing-red-windows:

------------------------------
Creating a Virtual Environment
------------------------------

We require installing Red into a virtual environment. Don't be scared, it's very
straightforward. See the section `installing-in-virtual-environment`.

--------------
Installing Red
--------------

.. attention:: You may need to restart your computer after installing dependencies
               for the PATH changes to take effect.

1. Open a command prompt (open Start, search for "command prompt", then click it)
2. Run **one** of the following set of commands, depending on what extras you want installed

  * Normal installation:

    .. code-block:: none

        python -m pip install -U pip setuptools wheel
        python -m pip install -U Red-DiscordBot

  * With PostgreSQL support:

    .. code-block:: none

        python -m pip install -U pip setuptools wheel
        python -m pip install -U Red-DiscordBot[postgres]


.. note::

    These commands are also used for updating Red

--------------------------
Setting Up and Running Red
--------------------------

After installation, set up your instance with the following command:

.. code-block:: none

    redbot-setup

This will set the location where data will be stored, as well as your
storage backend and the name of the instance (which will be used for
running the bot).

Once done setting up the instance, run the following command to run Red:

.. code-block:: none

    redbot <your instance name>

It will walk through the initial setup, asking for your token and a prefix.
You can find out how to obtain a token with
:dpy_docs:`this guide <discord.html#creating-a-bot-account>`,
section "Creating a Bot Account".

.. tip::
   If it's the first time you're using Red, you should check our `getting-started` guide
   that will walk you through all essential information on how to interact with Red.
