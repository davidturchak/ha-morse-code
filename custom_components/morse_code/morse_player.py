"""Async Morse code playback logic with cancellation support."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .const import MORSE_ALPHABET

_LOGGER = logging.getLogger(__name__)


class MorsePlayer:
    """Plays Morse code by toggling a switch entity on and off."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the Morse player.

        Args:
            hass: The Home Assistant instance.
        """
        self._hass = hass
        self._active_tasks: dict[str, asyncio.Task[None]] = {}

    async def play(
        self,
        entity_id: str,
        text: str,
        dot_duration_ms: int,
        dash_duration_ms: int,
        symbol_gap_ms: int,
        letter_gap_ms: int,
        word_gap_ms: int,
    ) -> None:
        """Start Morse code playback for an entity, cancelling any existing playback.

        Args:
            entity_id: The switch entity to toggle.
            text: The text to play as Morse code.
            dot_duration_ms: Duration of a dot in milliseconds.
            dash_duration_ms: Duration of a dash in milliseconds.
            symbol_gap_ms: Gap between symbols within a letter in milliseconds.
            letter_gap_ms: Gap between letters in milliseconds.
            word_gap_ms: Gap between words in milliseconds.
        """
        # Cancel any existing playback for this entity
        if entity_id in self._active_tasks:
            existing_task = self._active_tasks[entity_id]
            if not existing_task.done():
                _LOGGER.info(
                    "Cancelling existing Morse playback for %s", entity_id
                )
                existing_task.cancel()
                try:
                    await existing_task
                except asyncio.CancelledError:
                    pass

        # Start new playback task
        task = self._hass.async_create_task(
            self._play_morse(
                entity_id,
                text,
                dot_duration_ms,
                dash_duration_ms,
                symbol_gap_ms,
                letter_gap_ms,
                word_gap_ms,
            )
        )
        self._active_tasks[entity_id] = task

    async def _play_morse(
        self,
        entity_id: str,
        text: str,
        dot_duration_ms: int,
        dash_duration_ms: int,
        symbol_gap_ms: int,
        letter_gap_ms: int,
        word_gap_ms: int,
    ) -> None:
        """Execute Morse code playback sequence.

        Args:
            entity_id: The switch entity to toggle.
            text: The text to play as Morse code.
            dot_duration_ms: Duration of a dot in milliseconds.
            dash_duration_ms: Duration of a dash in milliseconds.
            symbol_gap_ms: Gap between symbols within a letter in milliseconds.
            letter_gap_ms: Gap between letters in milliseconds.
            word_gap_ms: Gap between words in milliseconds.
        """
        try:
            # If switch is currently ON, turn it OFF and wait
            state = self._hass.states.get(entity_id)
            if state and state.state == "on":
                _LOGGER.debug("Switch %s is ON, turning OFF before playback", entity_id)
                await self._turn_off(entity_id)
                await asyncio.sleep(dot_duration_ms / 1000)

            words = text.upper().split()
            for word_idx, word in enumerate(words):
                if word_idx > 0:
                    await asyncio.sleep(word_gap_ms / 1000)

                first_letter_in_word = True
                for char in word:
                    morse = MORSE_ALPHABET.get(char)
                    if morse is None:
                        _LOGGER.debug(
                            "Skipping unsupported character: %r", char
                        )
                        continue

                    if not first_letter_in_word:
                        await asyncio.sleep(letter_gap_ms / 1000)
                    first_letter_in_word = False

                    for symbol_idx, symbol in enumerate(morse):
                        if symbol_idx > 0:
                            await asyncio.sleep(symbol_gap_ms / 1000)

                        if symbol == ".":
                            await self._turn_on(entity_id)
                            await asyncio.sleep(dot_duration_ms / 1000)
                            await self._turn_off(entity_id)
                        elif symbol == "-":
                            await self._turn_on(entity_id)
                            await asyncio.sleep(dash_duration_ms / 1000)
                            await self._turn_off(entity_id)

        except asyncio.CancelledError:
            # Ensure switch is OFF on cancellation
            _LOGGER.debug("Playback cancelled for %s, turning OFF", entity_id)
            await self._turn_off(entity_id)
            raise
        finally:
            self._active_tasks.pop(entity_id, None)

    async def _turn_on(self, entity_id: str) -> None:
        """Turn on the switch entity.

        Args:
            entity_id: The switch entity to turn on.
        """
        await self._hass.services.async_call(
            "homeassistant",
            "turn_on",
            {"entity_id": entity_id},
        )

    async def _turn_off(self, entity_id: str) -> None:
        """Turn off the switch entity.

        Args:
            entity_id: The switch entity to turn off.
        """
        await self._hass.services.async_call(
            "homeassistant",
            "turn_off",
            {"entity_id": entity_id},
        )
