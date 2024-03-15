import datetime
from collections import namedtuple
from typing import Tuple, Generator, Union, List

import discord
from copy import deepcopy

from core import Config

__all__ = ["Account", "get_balance", "set_balance", "withdraw_credits", "deposit_credits",
           "can_spend", "transfer_credits", "wipe_bank", "get_guild_accounts",
           "get_global_accounts", "get_account", "is_global", "set_global",
           "get_bank_name", "set_bank_name", "get_currency_name", "set_currency_name",
           "get_default_balance", "set_default_balance"]

_DEFAULT_GLOBAL = {
    "is_global": False,
    "bank_name": "Twentysix bank",
    "currency": "credits",
    "default_balance": 100
}

_DEFAULT_GUILD = {
    "bank_name": "Twentysix bank",
    "currency": "credits",
    "default_balance": 100
}

_DEFAULT_MEMBER = {
    "name": "",
    "balance": 0,
    "created_at": 0
}

_DEFAULT_USER = _DEFAULT_MEMBER

_bank_type = type("Bank", (object,), {})

_conf = Config.get_conf(_bank_type(), 384734293238749, force_registration=True)


class Account:
    """A single account. This class should ONLY be instantiated by the bank itself."""

    def __init__(self, name: str, balance: int, created_at: datetime.datetime):
        self.name = name
        self.balance = balance
        self.created_at = created_at


def _register_defaults():
    _conf.register_global(**_DEFAULT_GLOBAL)
    _conf.register_guild(**_DEFAULT_GUILD)
    _conf.register_member(**_DEFAULT_MEMBER)
    _conf.register_user(**_DEFAULT_USER)


_register_defaults()


def _encoded_current_time() -> int:
    """
    Encoded current timestamp in UTC.
    :return:
    """
    now = datetime.datetime.utcnow()
    return _encode_time(now)


def _encode_time(time: datetime.datetime) -> int:
    """
    Goes from datetime object to serializable int.
    :param time:
    :return:
    """
    ret = int(time.timestamp())
    return ret


def _decode_time(time: int) -> datetime.datetime:
    """
    Returns decoded timestamp in UTC.
    :param time:
    :return:
    """
    return datetime.datetime.utcfromtimestamp(time)


async def get_balance(member: discord.Member) -> int:
    """
    Gets the current balance of a member.

    :param discord.Member member: 
        The member whose balance to check.
    :return: 
        The member's balance
    :rtype: 
        int
    """
    acc = await get_account(member)
    return acc.balance


async def can_spend(member: discord.Member, amount: int) -> bool:
    """
    Determines if a member can spend the given amount.

    :param discord.Member member: 
        The member wanting to spend.
    :param int amount: 
        The amount the member wants to spend.
    :return: 
        :code:`True` if the member has a sufficient balance to spend the amount, else :code:`False`.
    :rtype: 
        bool
    """
    if _invalid_amount(amount):
        return False
    return await get_balance(member) > amount


async def set_balance(member: discord.Member, amount: int) -> int:
    """
    Sets an account balance.

    May raise ValueError if amount is invalid.

    :param discord.Member member: 
        The member whose balance to set.
    :param int amount: 
        The amount to set the balance to.
    :return: 
        New account balance.
    :rtype: 
        int
    :raises ValueError: 
        If attempting to set the balance to a negative number
    """
    if amount < 0:
        raise ValueError("Not allowed to have negative balance.")
    if await is_global():
        group = _conf.user(member)
    else:
        group = _conf.member(member)
    await group.balance.set(amount)

    if await group.created_at() == 0:
        time = _encoded_current_time()
        await group.created_at.set(time)

    if await group.name() == "":
        await group.name.set(member.display_name)

    return amount


def _invalid_amount(amount: int) -> bool:
    return amount <= 0


async def withdraw_credits(member: discord.Member, amount: int) -> int:
    """
    Removes a certain amount of credits from an account.

    May raise ValueError if the amount is invalid or if the account has
    insufficient funds.

    :param discord.Member member: 
        The member to withdraw credits from.
    :param int amount: 
        The amount to withdraw.
    :return: 
        New account balance.
    :rtype: 
        int
    :raises ValueError: 
        if the withdrawal amount is invalid or if the account has insufficient funds
    """
    if _invalid_amount(amount):
        raise ValueError("Invalid withdrawal amount {} <= 0".format(amount))

    bal = await get_balance(member)
    if amount > bal:
        raise ValueError("Insufficient funds {} > {}".format(amount, bal))

    return await set_balance(member, bal - amount)


async def deposit_credits(member: discord.Member, amount: int) -> int:
    """
    Adds a given amount of credits to an account.

    May raise ValueError if the amount is invalid.

    :param discord.Member member: 
        The member to deposit credits to.
    :param int amount: 
        The amount to deposit.
    :return: 
        The new balance
    :rtype: 
        int
    :raises ValueError: 
        If the deposit amount is invalid.
    """
    if _invalid_amount(amount):
        raise ValueError("Invalid withdrawal amount {} <= 0".format(amount))

    bal = await get_balance(member)
    return await set_balance(member, amount + bal)


async def transfer_credits(from_: discord.Member, to: discord.Member, amount: int):
    """
    Transfers a given amount of credits from one account to another.

    May raise ValueError if the amount is invalid or if the :code:`from_`
    account has insufficient funds.

    :param discord.Member from_: 
        The member to transfer from.
    :param discord.Member to: 
        The member to transfer to.
    :param int amount: 
        The amount to transfer.
    :return: 
        The new balance.
    :rtype: 
        int
    :raises ValueError: 
        If the amount is invalid or if :code:`from_` has insufficient funds.
    """
    if _invalid_amount(amount):
        raise ValueError("Invalid transfer amount {} <= 0".format(amount))

    await withdraw_credits(from_, amount)
    return await deposit_credits(to, amount)


async def wipe_bank(user: Union[discord.User, discord.Member]):
    """
    Deletes all accounts from the bank.

    .. important::

        A member is required if the bank is currently guild specific.

    :param user:
        A user to be used in clearing the bank, this is required for technical
        reasons and it does not matter which user/member is used.
    :type user:
        discord.User or discord.Member
    """
    if await is_global():
        await _conf.user(user).clear()
    else:
        await _conf.member(user).clear()


async def get_guild_accounts(guild: discord.Guild) -> List[Account]:
    """
    Gets all account data for the given guild.

    May raise RuntimeError if the bank is currently global.

    :param discord.Guild guild: 
        The guild to get accounts for.
    :return: 
        A generator for all guild accounts.
    :rtype: 
        generator
    :raises RuntimeError: 
        If the bank is global.
    """
    if is_global():
        raise RuntimeError("The bank is currently global.")

    ret = []
    accs = await _conf.member(guild.owner).all_from_kind()
    for user_id, acc in accs.items():
        acc_data = acc.copy()  # There ya go kowlin
        acc_data['created_at'] = _decode_time(acc_data['created_at'])
        ret.append(Account(**acc_data))
    return ret


async def get_global_accounts(user: discord.User) -> List[Account]:
    """
    Gets all global account data.

    May raise RuntimeError if the bank is currently guild specific.

    :param discord.User user: 
        A user to be used for getting accounts.
    :return: 
        A generator of all global accounts.
    :rtype: 
        generator
    :raises RuntimeError: 
        If the bank is guild specific.
    """
    if not is_global():
        raise RuntimeError("The bank is not currently global.")

    ret = []
    accs = await _conf.user(user).all_from_kind()  # this is a dict of user -> acc
    for user_id, acc in accs.items():
        acc_data = acc.copy()
        acc_data['created_at'] = _decode_time(acc_data['created_at'])
        ret.append(Account(**acc_data))

    return ret


async def get_account(member: Union[discord.Member, discord.User]) -> Account:
    """
    Gets the appropriate account for the given user or member. A member is
    required if the bank is currently guild specific.

    :param member:
        The user whose account to get.
    :type member:
        discord.User or discord.Member
    :return: 
        The user's account.
    :rtype: 
        :py:class:`Account`
    """
    if await is_global():
        acc_data = (await _conf.user(member)()).copy()
        default = _DEFAULT_USER.copy()
    else:
        acc_data = (await _conf.member(member)()).copy()
        default = _DEFAULT_MEMBER.copy()

    if acc_data == {}:
        acc_data = default
        acc_data['name'] = member.display_name
        try:
            acc_data['balance'] = await get_default_balance(member.guild)
        except AttributeError:
            acc_data['balance'] = await get_default_balance()

    acc_data['created_at'] = _decode_time(acc_data['created_at'])
    return Account(**acc_data)


async def is_global() -> bool:
    """
    Determines if the bank is currently global.

    :return: 
        :code:`True` if the bank is global, otherwise :code:`False`.
    :rtype: 
        bool
    """
    return await _conf.is_global()


async def set_global(global_: bool, user: Union[discord.User, discord.Member]) -> bool:
    """
    Sets global status of the bank, requires the user parameter for technical reasons.
    
    .. important::
        All accounts are reset when you switch!

    :param global_:
        :code:`True` will set bank to global mode.
    :param user:
        Must be a Member object if changing TO global mode.
    :type user:
        discord.User or discord.Member
    :return:
        New bank mode, :code:`True` is global.
    :rtype: 
        bool
    :raises RuntimeError:
        If bank is becoming global and :py:class:`discord.Member` was not provided.
    """
    if (await is_global()) is global_:
        return global_

    if is_global():
        await _conf.user(user).clear_all()
    elif isinstance(user, discord.Member):
        await _conf.member(user).clear_all()
    else:
        raise RuntimeError("You must provide a member if you're changing to global"
                           " bank mode.")

    await _conf.is_global.set(global_)
    return global_


async def get_bank_name(guild: discord.Guild=None) -> str:
    """
    Gets the current bank name. If the bank is guild-specific the
    guild parameter is required.

    May raise RuntimeError if guild is missing and required.

    :param discord.Guild guild: 
        The guild to get the bank name for (required if bank is guild-specific).
    :return: 
        The bank's name.
    :rtype: 
        str
    :raises RuntimeError: 
        If the bank is guild-specific and guild was not provided.
    """
    if await is_global():
        return await _conf.bank_name()
    elif guild is not None:
        return await _conf.guild(guild).bank_name()
    else:
        raise RuntimeError("Guild parameter is required and missing.")


async def set_bank_name(name: str, guild: discord.Guild=None) -> str:
    """
    Sets the bank name, if bank is guild specific the guild parameter is
    required.

    May throw RuntimeError if guild is required and missing.

    :param str name: 
        The new name for the bank.
    :param discord.Guild guild: 
        The guild to set the bank name for (required if bank is guild-specific).
    :return: 
        The new name for the bank.
    :rtype: 
        str
    :raises RuntimeError: 
        If the bank is guild-specific and guild was not provided.
    """
    if await is_global():
        await _conf.bank_name.set(name)
    elif guild is not None:
        await _conf.guild(guild).bank_name.set(name)
    else:
        raise RuntimeError("Guild must be provided if setting the name of a guild"
                           "-specific bank.")
    return name


async def get_currency_name(guild: discord.Guild=None) -> str:
    """
    Gets the currency name of the bank. The guild parameter is required if
    the bank is guild-specific.

    May raise RuntimeError if the guild is missing and required.

    :param discord.Guild guild: 
        The guild to get the currency name for (required if bank is guild-specific).
    :return: 
        The currency name.
    :rtype: 
        str
    :raises RuntimeError: 
        If the bank is guild-specific and guild was not provided.
    """
    if await is_global():
        return await _conf.currency()
    elif guild is not None:
        return await _conf.guild(guild).currency()
    else:
        raise RuntimeError("Guild must be provided.")


async def set_currency_name(name: str, guild: discord.Guild=None) -> str:
    """
    Sets the currency name for the bank, if bank is guild specific the
    guild parameter is required.

    May raise RuntimeError if guild is missing and required.

    :param str name: 
        The new name for the currency.
    :param discord.Guild guild: 
        The guild to set the currency name for (required if bank is guild-specific).
    :return: 
        The new name for the currency.
    :rtype: 
        str
    :raises RuntimeError: 
        If the bank is guild-specific and guild was not provided.
    """
    if await is_global():
        await _conf.currency.set(name)
    elif guild is not None:
        await _conf.guild(guild).currency.set(name)
    else:
        raise RuntimeError("Guild must be provided if setting the currency"
                           " name of a guild-specific bank.")
    return name


async def get_default_balance(guild: discord.Guild=None) -> int:
    """
    Gets the current default balance amount. If the bank is guild-specific
    you must pass guild.

    May raise RuntimeError if guild is missing and required.

    :param discord.Guild guild: 
        The guild to get the default balance for (required if bank is guild-specific).
    :return: 
        The bank's default balance.
    :rtype: 
        str
    :raises RuntimeError: 
        If the bank is guild-specific and guild was not provided.
    """
    if await is_global():
        return await _conf.default_balance()
    elif guild is not None:
        return await _conf.guild(guild).default_balance()
    else:
        raise RuntimeError("Guild is missing and required!")


async def set_default_balance(amount: int, guild: discord.Guild=None) -> int:
    """
    Sets the default balance amount. Guild is required if the bank is
    guild-specific.

    May raise RuntimeError if guild is missing and required.

    May raise ValueError if amount is invalid.

    :param int amount: 
        The new default balance.
    :param discord.Guild guild: 
        The guild to set the default balance for (required if bank is guild-specific).
    :return: 
        The new default balance.
    :rtype: 
        str
    :raises RuntimeError: 
        If the bank is guild-specific and guild was not provided.
    :raises ValueError: 
        If the amount is invalid.
    """
    amount = int(amount)
    if amount < 0:
        raise ValueError("Amount must be greater than zero.")

    if await is_global():
        await _conf.default_balance.set(amount)
    elif guild is not None:
        await _conf.guild(guild).default_balance.set(amount)
    else:
        raise RuntimeError("Guild is missing and required.")

    return amount
