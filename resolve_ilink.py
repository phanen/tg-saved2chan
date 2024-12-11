import base64
import binascii
import re
import struct

USERNAME_RE = re.compile(
    r"@|(?:https?://)?(?:www\.)?(?:telegram\.(?:me|dog)|t\.me)/(@|\+|joinchat/)?"
)
TG_JOIN_RE = re.compile(r"tg://(join)\?invite=")

VALID_USERNAME_RE = re.compile(r"^[a-z](?:(?!__)\w){1,30}[a-z\d]$", re.IGNORECASE)


def _decode_telegram_base64(string):
    """
    Decodes a url-safe base64-encoded string into its bytes
    by first adding the stripped necessary padding characters.

    This is the way Telegram shares binary data as strings,
    such as Bot API-style file IDs or invite links.

    Returns `None` if the input string was not valid.
    """
    try:
        return base64.urlsafe_b64decode(string + "=" * (len(string) % 4))
    except (binascii.Error, ValueError, TypeError):
        return None  # not valid base64, not valid ascii, not a string


def parse_username(username):
    """
    Parses the given username or channel access hash, given
    a string, username or URL. Returns a tuple consisting of
    both the stripped, lowercase username and whether it is
    a joinchat/ hash (in which case is not lowercase'd).

    Returns ``(None, False)`` if the ``username`` or link is not valid.
    """
    username = username.strip()
    m = USERNAME_RE.match(username) or TG_JOIN_RE.match(username)
    if m:
        username = username[m.end() :]
        is_invite = bool(m.group(1))
        if is_invite:
            return username, True
        else:
            username = username.rstrip("/")

    if VALID_USERNAME_RE.match(username):
        return username.lower(), False
    else:
        return None, False


def resolve_invite_link(link):
    """
    Resolves the given invite link. Returns a tuple of
    ``(link creator user id, global chat id, random int)``.

    Note that for broadcast channels or with the newest link format, the link
    creator user ID will be zero to protect their identity. Normal chats and
    megagroup channels will have such ID.

    Note that the chat ID may not be accurate for chats with a link that were
    upgraded to megagroup, since the link can remain the same, but the chat
    ID will be correct once a new link is generated.
    """
    link_hash, is_link = parse_username(link)
    print(link_hash, is_link)
    if not is_link:
        # Perhaps the user passed the link hash directly
        link_hash = link

    # Little known fact, but invite links with a
    # hex-string of bytes instead of base64 also works.
    if re.match(r"[a-fA-F\d]+", link_hash) and len(link_hash) in (24, 32):
        payload = bytes.fromhex(link_hash)
    else:
        payload = _decode_telegram_base64(link_hash)

    try:
        if len(payload) == 12:
            return (0, *struct.unpack(">LQ", payload))
        elif len(payload) == 16:
            return struct.unpack(">LLQ", payload)
        else:
            pass
    except (struct.error, TypeError):
        pass
    return None, None, None
