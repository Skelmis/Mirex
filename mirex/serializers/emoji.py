from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from disnake import Emoji


def emoji_as_dict(emoji: Emoji) -> Dict:
    return {
        "name": emoji.name,
        "roles": [],  # TODO This field
        "id": str(emoji.id),
        "require_colons": emoji.require_colons,
        "managed": emoji.managed,
        "animated": emoji.animated,
        "available": emoji.available,
    }
