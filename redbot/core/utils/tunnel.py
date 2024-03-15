import discord
from datetime import datetime
from redbot.core.utils.chat_formatting import pagify
import io
import sys
import weakref

_instances = weakref.WeakValueDictionary({})


class TunnelMeta(type):
    """
    lets prevent having multiple tunnels with the same
    places involved.
    """

    def __call__(cls, *args, **kwargs):
        lockout_tuple = (
            (kwargs.get('sender'), kwargs.get('origin')),
            kwargs.get('recipient')
        )

        if lockout_tuple in _instances:
            return _instances[lockout_tuple]

        # this is needed because weakvalue dicts can
        # change size without warning if an object is discarded
        # it can raise a runtime error, so ..
        while True:
            try:
                if not (
                    any(
                        lockout_tuple[0] == x[0]
                        for x in _instances.keys()
                    ) or any(
                        lockout_tuple[1] == x[1]
                        for x in _instances.keys()
                    )
                ):
                    # if this isn't temporarily stored, the weakref dict
                    # will discard this before the return statement,
                    # causing a key error
                    temp = super(TunnelMeta, cls).__call__(*args, **kwargs)
                    _instances[lockout_tuple] = temp
                    return temp
            except:  # NOQA: E722
                # Am I really supposed to except a runtime error flake >.>
                continue
            else:
                return None


class Tunnel(metaclass=TunnelMeta):
    """
    A tunnel interface for messages

    This will return None on init if the destination
    or source + origin pair is already in use, or the
    existing tunnel object if one exists for the designated
    parameters

    Attributes
    ----------
    sender: `discord.Member`
        The person who opened the tunnel
    origin: `discord.TextChannel`
        The channel in which it was opened
    recipient: `discord.User`
        The user on the other end of the tunnel
    """

    def __init__(self, *,
                 sender: discord.Member,
                 origin: discord.TextChannel,
                 recipient: discord.User):
        self.sender = sender
        self.origin = origin
        self.recipient = recipient
        self.last_interaction = datetime.utcnow()

    async def react_close(self, *, uid: int, message: str):
        send_to = self.origin if uid == self.sender.id else self.sender
        closer = next(filter(
            lambda x: x.id == uid, (self.sender, self.recipient)), None)
        await send_to.send(
            message.format(closer=closer)
        )

    @property
    def members(self):
        return self.sender, self.recipient

    @property
    def minutes_since(self):
        return int((self.last_interaction - datetime.utcnow()).seconds / 60)

    async def communicate(self, *,
                          message: discord.Message,
                          topic: str=None,
                          skip_message_content: bool=False):
        """
        Forwards a message.

        Parameters
        ----------
        message : `discord.Message`
            The message to forward
        topic : `str`
            A string to prepend
        skip_message_content : `bool`
            If this flag is set, only the topic will be sent

        Returns
        -------
        `int`, `int`
            a pair of ints matching the ids of the
            message which was forwarded
            and the last message the bot sent to do that.
            useful if waiting for reactions.

        Raises
        ------
        discord.Forbidden
            This should only happen if the user's DMs are disabled
            the bot can't upload at the origin channel
            or can't add reactions there.
        """
        if message.channel == self.origin \
                and message.author == self.sender:
            send_to = self.recipient
        elif message.author == self.recipient \
                and isinstance(message.channel, discord.DMChannel):
            send_to = self.origin
        else:
            return None

        if not skip_message_content:
            content = "\n".join((topic, message.content)) if topic \
                else message.content
        else:
            content = topic

        attach = None
        if message.attachments:
            files = []
            size = 0
            max_size = 8 * 1024 * 1024
            for a in message.attachments:
                _fp = io.BytesIO()
                await a.save(_fp)
                size += sys.getsizeof(_fp)
                if size > max_size:
                    await send_to.send(
                        "Could not forward attatchments. "
                        "Total size of attachments in a single "
                        "message must be less than 8MB."
                    )
                    break
                files.append(
                    discord.File(_fp, filename=a.filename)
                )
            else:
                attach = files

        rets = []
        for page in pagify(content):
            rets.append(
                await send_to.send(content, files=attach)
            )
            if attach:
                del attach

        await message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await message.add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")
        self.last_interaction = datetime.utcnow()
        await rets[-1].add_reaction("\N{NEGATIVE SQUARED CROSS MARK}")
        return [rets[-1].id, message.id]
