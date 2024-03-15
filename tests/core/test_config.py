import pytest


#region Register Tests
def test_config_register_global(config):
    config.register_global(enabled=False)
    assert config.defaults["GLOBAL"]["enabled"] is False
    assert config.enabled() is False


def test_config_register_global_badvalues(config):
    with pytest.raises(RuntimeError):
        config.register_global(**{"invalid var name": True})


def test_config_register_guild(config, empty_guild):
    config.register_guild(enabled=False, some_list=[], some_dict={})
    assert config.defaults[config.GUILD]["enabled"] is False
    assert config.defaults[config.GUILD]["some_list"] == []
    assert config.defaults[config.GUILD]["some_dict"] == {}

    assert config.guild(empty_guild).enabled() is False
    assert config.guild(empty_guild).some_list() == []
    assert config.guild(empty_guild).some_dict() == {}


def test_config_register_channel(config, empty_channel):
    config.register_channel(enabled=False)
    assert config.defaults[config.CHANNEL]["enabled"] is False
    assert config.channel(empty_channel).enabled() is False


def test_config_register_role(config, empty_role):
    config.register_role(enabled=False)
    assert config.defaults[config.ROLE]["enabled"] is False
    assert config.role(empty_role).enabled() is False


def test_config_register_member(config, empty_member):
    config.register_member(some_number=-1)
    assert config.defaults[config.MEMBER]["some_number"] == -1
    assert config.member(empty_member).some_number() == -1


def test_config_register_user(config, empty_user):
    config.register_user(some_value=None)
    assert config.defaults[config.USER]["some_value"] is None
    assert config.user(empty_user).some_value() is None


def test_config_force_register_global(config_fr):
    with pytest.raises(AttributeError):
        config_fr.enabled()

    config_fr.register_global(enabled=True)
    assert config_fr.enabled() is True
#endregion


# Test nested registration
def test_nested_registration(config):
    config.register_global(foo__bar__baz=False)
    assert config.foo.bar.baz() is False


def test_nested_registration_asdict(config):
    defaults = {'bar': {'baz': False}}
    config.register_global(foo=defaults)

    assert config.foo.bar.baz() is False


@pytest.mark.asyncio
async def test_nested_registration_and_changing(config):
    defaults = {'bar': {'baz': False}}
    config.register_global(foo=defaults)

    assert config.foo.bar.baz() is False

    with pytest.raises(ValueError):
        await config.foo.set(True)


def test_doubleset_default(config):
    config.register_global(foo=True)
    config.register_global(foo=False)

    assert config.foo() is False


def test_nested_registration_multidict(config):
    defaults = {
        "foo": {
            "bar": {
                "baz": True
            }
        },
        "blah": True
    }
    config.register_global(**defaults)

    assert config.foo.bar.baz() is True
    assert config.blah() is True


def test_nested_group_value_badreg(config):
    config.register_global(foo=True)
    with pytest.raises(KeyError):
        config.register_global(foo__bar=False)


def test_nested_toplevel_reg(config):
    defaults = {'bar': True, 'baz': False}
    config.register_global(foo=defaults)

    assert config.foo.bar() is True
    assert config.foo.baz() is False


def test_nested_overlapping(config):
    config.register_global(foo__bar=True)
    config.register_global(foo__baz=False)

    assert config.foo.bar() is True
    assert config.foo.baz() is False


def test_nesting_nofr(config):
    config.register_global(foo={})
    assert config.foo.bar() is None
    assert config.foo() == {}


#region Default Value Overrides
def test_global_default_override(config):
    assert config.enabled(True) is True


def test_global_default_nofr(config):
    assert config.nofr() is None
    assert config.nofr(True) is True


def test_guild_default_override(config, empty_guild):
    assert config.guild(empty_guild).enabled(True) is True


def test_channel_default_override(config, empty_channel):
    assert config.channel(empty_channel).enabled(True) is True


def test_role_default_override(config, empty_role):
    assert config.role(empty_role).enabled(True) is True


def test_member_default_override(config, empty_member):
    assert config.member(empty_member).enabled(True) is True


def test_user_default_override(config, empty_user):
    assert config.user(empty_user).some_value(True) is True
#endregion


#region Setting Values
@pytest.mark.asyncio
async def test_set_global(config):
    await config.enabled.set(True)
    assert config.enabled() is True


@pytest.mark.asyncio
async def test_set_guild(config, empty_guild):
    await config.guild(empty_guild).enabled.set(True)
    assert config.guild(empty_guild).enabled() is True

    curr_list = config.guild(empty_guild).some_list([1, 2, 3])
    assert curr_list == [1, 2, 3]
    curr_list.append(4)

    await config.guild(empty_guild).some_list.set(curr_list)
    assert config.guild(empty_guild).some_list() == curr_list


@pytest.mark.asyncio
async def test_set_channel(config, empty_channel):
    await config.channel(empty_channel).enabled.set(True)
    assert config.channel(empty_channel).enabled() is True


@pytest.mark.asyncio
async def test_set_channel_no_register(config, empty_channel):
    await config.channel(empty_channel).no_register.set(True)
    assert config.channel(empty_channel).no_register() is True
#endregion


# Dynamic attribute testing
@pytest.mark.asyncio
async def test_set_dynamic_attr(config):
    await config.set_attr("foobar", True)

    assert config.foobar() is True


def test_get_dynamic_attr(config):
    assert config.get_attr("foobaz", True) is True


# Member Group testing
@pytest.mark.asyncio
async def test_membergroup_allguilds(config, empty_member):
    await config.member(empty_member).foo.set(False)

    all_servers = config.member(empty_member).all_guilds()
    assert str(empty_member.guild.id) in all_servers


@pytest.mark.asyncio
async def test_membergroup_allmembers(config, empty_member):
    await config.member(empty_member).foo.set(False)

    all_members = config.member(empty_member).all()
    assert str(empty_member.id) in all_members


# Clearing testing
@pytest.mark.asyncio
async def test_global_clear(config):
    config.register_global(foo=True, bar=False)

    await config.foo.set(False)
    await config.bar.set(True)

    assert config.foo() is False
    assert config.bar() is True

    await config.clear()

    assert config.foo() is True
    assert config.bar() is False


@pytest.mark.asyncio
async def test_member_clear(config, member_factory):
    config.register_member(foo=True)

    m1 = member_factory.get()
    await config.member(m1).foo.set(False)
    assert config.member(m1).foo() is False

    m2 = member_factory.get()
    await config.member(m2).foo.set(False)
    assert config.member(m2).foo() is False

    assert m1.guild.id != m2.guild.id

    await config.member(m1).clear()
    assert config.member(m1).foo() is True
    assert config.member(m2).foo() is False


@pytest.mark.asyncio
async def test_member_clear_all(config, member_factory):
    server_ids = []
    for _ in range(5):
        member = member_factory.get()
        await config.member(member).foo.set(True)
        server_ids.append(member.guild.id)

    member = member_factory.get()
    assert len(config.member(member).all_guilds()) == len(server_ids)

    await config.member(member).clear_all()

    assert len(config.member(member).all_guilds()) == 0


# Get All testing
@pytest.mark.asyncio
async def test_user_get_all_from_kind(config, user_factory):
    for _ in range(5):
        user = user_factory.get()
        await config.user(user).foo.set(True)

    user = user_factory.get()
    all_data = config.user(user).all_from_kind()

    assert len(all_data) == 5


@pytest.mark.asyncio
async def test_user_getalldata(config, user_factory):
    user = user_factory.get()
    await config.user(user).foo.set(False)

    assert "foo" in config.user(user).all()
