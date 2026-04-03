"""Morse Code component for Home Assistant.

Plays text as Morse code by toggling a switch entity ON/OFF.
"""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    DEFAULT_DASH_DURATION_MS,
    DEFAULT_DOT_DURATION_MS,
    DEFAULT_LETTER_GAP_MS,
    DEFAULT_SYMBOL_GAP_MS,
    DEFAULT_WORD_GAP_MS,
    DOMAIN,
)
from .morse_player import MorsePlayer

_LOGGER = logging.getLogger(__name__)

SERVICE_PLAY = "play"

SERVICE_PLAY_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required("text"): cv.string,
        vol.Optional("dot_duration_ms", default=DEFAULT_DOT_DURATION_MS): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=5000)
        ),
        vol.Optional("dash_duration_ms", default=DEFAULT_DASH_DURATION_MS): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=5000)
        ),
        vol.Optional("symbol_gap_ms", default=DEFAULT_SYMBOL_GAP_MS): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=5000)
        ),
        vol.Optional("letter_gap_ms", default=DEFAULT_LETTER_GAP_MS): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=10000)
        ),
        vol.Optional("word_gap_ms", default=DEFAULT_WORD_GAP_MS): vol.All(
            vol.Coerce(int), vol.Range(min=10, max=20000)
        ),
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Morse Code component from YAML (legacy)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Morse Code from a config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if setup was successful.
    """
    _LOGGER.info("Setting up Morse Code component")

    player = MorsePlayer(hass)
    hass.data[DOMAIN] = player

    async def handle_play(call: ServiceCall) -> None:
        """Handle the morse_code.play service call.

        Args:
            call: The service call data.
        """
        entity_id: str = call.data["entity_id"]
        text: str = call.data["text"]
        dot_duration_ms: int = call.data["dot_duration_ms"]
        dash_duration_ms: int = call.data["dash_duration_ms"]
        symbol_gap_ms: int = call.data["symbol_gap_ms"]
        letter_gap_ms: int = call.data["letter_gap_ms"]
        word_gap_ms: int = call.data["word_gap_ms"]

        _LOGGER.info(
            "Playing Morse code on %s: %r (dot=%dms, dash=%dms)",
            entity_id,
            text,
            dot_duration_ms,
            dash_duration_ms,
        )

        await player.play(
            entity_id=entity_id,
            text=text,
            dot_duration_ms=dot_duration_ms,
            dash_duration_ms=dash_duration_ms,
            symbol_gap_ms=symbol_gap_ms,
            letter_gap_ms=letter_gap_ms,
            word_gap_ms=word_gap_ms,
        )

    hass.services.async_register(
        DOMAIN, SERVICE_PLAY, handle_play, schema=SERVICE_PLAY_SCHEMA
    )

    _LOGGER.info("Morse Code component loaded successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Morse Code config entry.

    Args:
        hass: The Home Assistant instance.
        entry: The config entry.

    Returns:
        True if unload was successful.
    """
    hass.services.async_remove(DOMAIN, SERVICE_PLAY)
    hass.data.pop(DOMAIN, None)
    _LOGGER.info("Morse Code component unloaded")
    return True
