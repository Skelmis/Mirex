from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Union

if TYPE_CHECKING:
    from disnake import Sticker, GuildSticker, StandardSticker


def sticker_as_dict(sticker: Union[Sticker, GuildSticker, StandardSticker]) -> Dict:
    return {
        "id": str(sticker.id),
        "name": sticker.name,
        "tags": getattr(sticker, "tags")
        if getattr(sticker, "tags", False)
        else sticker.emoji,
        "type": sticker.type.value,
        "format_type": sticker.format.value,
        "description": sticker.description,
        "asset": "",  # TODO this field doesnt exist yet in disnake
        "available": sticker.available,
        "guild_id": str(sticker.guild_id),
    }
