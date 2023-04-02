from __future__ import annotations

from typing import TYPE_CHECKING, Dict

from mirex.serializers import role_as_dict, emoji_as_dict, sticker_as_dict

if TYPE_CHECKING:
    # Gate behind type checking
    # so it's not required to use the program
    from disnake import Guild


def guild_as_dict(guild: Guild) -> Dict:
    if guild.unavailable:
        return {"unavailable": True, "id": str(guild.id)}

    return {
        "id": str(guild.id),
        "name": guild.name,
        "icon": guild._icon,
        "description": guild.description,
        "home_header": None,  # TODO this field doesnt exist yet in disnake
        "splash": guild._splash,
        "discovery_splash": guild._discovery_splash,
        "features": guild.features,
        "approximate_member_count": guild.approximate_member_count,
        "approximate_presence_count": guild.approximate_presence_count,
        "emojis": [emoji_as_dict(e) for e in guild.emojis],
        "stickers": [sticker_as_dict(s) for s in guild.stickers],
        "banner": guild._banner,
        "owner_id": str(guild.owner_id),
        "application_id": None,  # TODO this field doesnt exist yet in disnake
        "region": guild._region,
        "afk_channel_id": str(guild.afk_channel.id) if guild.afk_channel else None,
        "afk_timeout": guild.afk_timeout,
        "system_channel_id": guild._system_channel_id,
        "widget_enabled": guild.widget_enabled,
        "widget_channel_id": guild.widget_channel_id,
        "verification_level": guild.verification_level.value,
        "roles": [role_as_dict(r) for r in guild.roles],
        "default_message_notifications": guild.default_notifications.value,
        "mfa_level": guild.mfa_level,
        "explicit_content_filter": guild.explicit_content_filter.value,
        "max_presences": guild.max_presences,
        "max_members": guild.max_members,
        "max_stage_video_channel_users": 50,  # TODO this field doesnt exist yet in disnake
        "max_video_channel_users": guild.max_video_channel_users,
        "vanity_url_code": guild.vanity_url_code,
        "premium_tier": guild.premium_tier,
        "premium_subscription_count": guild.premium_subscription_count,
        "system_channel_flags": guild.system_channel_flags.value,
        "preferred_locale": guild.preferred_locale.value,
        "rules_channel_id": guild._rules_channel_id,
        "safety_alerts_channel_id": None,  # TODO this field doesnt exist yet in disnake
        "public_updates_channel_id": guild._public_updates_channel_id,
        "hub_type": None,  # TODO this field doesnt exist yet in disnake
        "premium_progress_bar_enabled": guild.premium_progress_bar_enabled,
        "latest_onboarding_question_id": None,  # TODO this field doesnt exist yet in disnake
        "nsfw": False,  # TODO This field isn't in Disnake
        "nsfw_level": guild.nsfw_level.value,
    }
