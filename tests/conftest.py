from collections import namedtuple
from pathlib import Path

import pytest
import random

from core.bot import Red
from _pytest.monkeypatch import MonkeyPatch
from core.drivers import red_json
from core import Config


@pytest.fixture(scope="session")
def monkeysession(request):
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture()
def json_driver(tmpdir_factory):
    import uuid
    rand = str(uuid.uuid4())
    path = Path(str(tmpdir_factory.mktemp(rand)))
    driver = red_json.JSON(
        "PyTest",
        data_path_override=path
    )
    return driver


@pytest.fixture()
def config(json_driver):
    import uuid
    conf = Config(
        cog_name="PyTest",
        unique_identifier=str(uuid.uuid4()),
        driver_spawn=json_driver)
    yield conf
    conf._defaults = {}


@pytest.fixture()
def config_fr(json_driver):
    """
    Mocked config object with force_register enabled.
    """
    import uuid
    conf = Config(
        cog_name="PyTest",
        unique_identifier=str(uuid.uuid4()),
        driver_spawn=json_driver,
        force_registration=True
    )
    yield conf
    conf._defaults = {}


#region Dpy Mocks
@pytest.fixture()
def guild_factory():
    mock_guild = namedtuple("Guild", "id members")

    class GuildFactory:
        def get(self):
            return mock_guild(random.randint(1, 999999999), [])

    return GuildFactory()


@pytest.fixture()
def empty_guild(guild_factory):
    return guild_factory.get()


@pytest.fixture(scope="module")
def empty_channel():
    mock_channel = namedtuple("Channel", "id")
    return mock_channel(random.randint(1, 999999999))


@pytest.fixture(scope="module")
def empty_role():
    mock_role = namedtuple("Role", "id")
    return mock_role(random.randint(1, 999999999))


@pytest.fixture()
def member_factory(guild_factory):
    mock_member = namedtuple("Member", "id guild display_name")

    class MemberFactory:
        def get(self):
            return mock_member(
                random.randint(1, 999999999),
                guild_factory.get(),
                'Testing_Name')

    return MemberFactory()


@pytest.fixture()
def empty_member(member_factory):
    return member_factory.get()


@pytest.fixture()
def user_factory():
    mock_user = namedtuple("User", "id")

    class UserFactory:
        def get(self):
            return mock_user(
                random.randint(1, 999999999))

    return UserFactory()


@pytest.fixture()
def empty_user(user_factory):
    return user_factory.get()


@pytest.fixture(scope="module")
def empty_message():
    mock_msg = namedtuple("Message", "content")
    return mock_msg("No content.")


@pytest.fixture()
def ctx(empty_member, empty_channel, red):
    mock_ctx = namedtuple("Context", "author guild channel message bot")
    return mock_ctx(empty_member, empty_member.guild, empty_channel,
                    empty_message, red)
#endregion


#region Red Mock
@pytest.fixture()
def red(config_fr):
    from core.cli import parse_cli_flags
    cli_flags = parse_cli_flags()

    description = "Red v3 - Alpha"

    Config.get_core_conf = (lambda *args, **kwargs: config_fr)

    red = Red(cli_flags, description=description, pm_help=None)

    yield red

    red.http._session.close()
#endregion