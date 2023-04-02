from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from disnake import Role


def role_as_dict(role: Role) -> Dict:
    return {
        "id": str(role.id),
        "name": role.name,
        "description": None,  # TODO this field doesnt exist yet in disnake
        "permissions": role.permissions.value,
        "position": role.position,
        "color": role.color.value,
        "hoist": role.hoist,
        "managed": role.managed,
        "mentionable": role.mentionable,
        "icon": role._icon,
        "unicode_emoji": role._emoji,
        "flags": 0,  # TODO this field doesnt exist yet in disnake
    }
