# Morse Code Component for Home Assistant

A custom Home Assistant component that converts text to Morse code and plays it
by toggling a switch entity ON and OFF with precise timing.

## Installation

1. Copy the `morse_code/` folder into your `custom_components/` directory:

   ```
   custom_components/
   └── morse_code/
       ├── __init__.py
       ├── const.py
       ├── manifest.json
       ├── morse_player.py
       └── services.yaml
   ```

2. Add the following to your `configuration.yaml`:

   ```yaml
   morse_code:
   ```

3. Restart Home Assistant.

## Service: `morse_code.play`

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `entity_id` | string | Yes | — | The switch entity to toggle |
| `text` | string | Yes | — | The text to convert and play as Morse code |
| `dot_duration_ms` | int | No | 100 | Duration of a dot signal (ON time) in ms |
| `dash_duration_ms` | int | No | 300 | Duration of a dash signal (ON time) in ms |
| `symbol_gap_ms` | int | No | 100 | Gap between dots/dashes within a letter in ms |
| `letter_gap_ms` | int | No | 300 | Gap between letters in ms |
| `word_gap_ms` | int | No | 700 | Gap between words in ms |

## Usage Examples

### Simple automation

```yaml
automation:
  - alias: "Morse SOS on doorbell"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell
        to: "on"
    action:
      - service: morse_code.play
        data:
          entity_id: switch.indicator_light
          text: "SOS"
```

### Service call with custom timing

```yaml
service: morse_code.play
data:
  entity_id: switch.desk_lamp
  text: "HELLO WORLD"
  dot_duration_ms: 200
  dash_duration_ms: 600
  symbol_gap_ms: 200
  letter_gap_ms: 600
  word_gap_ms: 1400
```

## Morse Timing Diagram

```
          dot    dash         symbol_gap   letter_gap     word_gap
          ┌─┐   ┌───┐
  ON      │ │   │   │
 ─────────┘ └───┘   └──────────────────────────────────────────────────
  OFF       ^^^                  ^^^             ^^^           ^^^
         symbol_gap          symbol_gap      letter_gap     word_gap

  Example: "AB" = .- -...

  ┌─┐ ┌───┐     ┌───┐ ┌─┐ ┌─┐ ┌─┐
  │.│ │ - │     │ - │ │.│ │.│ │.│
  ┘ └─┘   └─────┘   └─┘ └─┘ └─┘ └
  ^   ^   ^     ^       ^ ^ ^ ^
  dot sym dash  letter  symbols between
      gap       gap     dots/dashes

  Timing (defaults):
    dot  = 100ms ON
    dash = 300ms ON
    symbol_gap = 100ms OFF  (between signals in a letter)
    letter_gap = 300ms OFF  (between letters)
    word_gap   = 700ms OFF  (between words)
```

## Supported Characters

**Latin Letters:** A B C D E F G H I J K L M N O P Q R S T U V W X Y Z

**Russian Cyrillic:** А Б В Г Д Е Ж З И Й К Л М Н О П Р С Т У Ф Х Ц Ч Ш Щ Ъ Ы Ь Э Ю Я Ё

**Digits:** 0 1 2 3 4 5 6 7 8 9

**Punctuation:** `.` `,` `?` `'` `!` `/` `(` `)` `&` `:` `;` `=` `+` `-` `_` `"` `$` `@`

Unsupported characters are silently skipped (logged at DEBUG level).
Text is case-insensitive. Latin and Cyrillic can be mixed in the same message.

## Troubleshooting

### Component not loading

- Check the Home Assistant logs for errors (`Settings > System > Logs`).
- Verify the `morse_code/` folder is inside `custom_components/` and contains
  all required files (`__init__.py`, `manifest.json`, etc.).
- Ensure `morse_code:` is present in `configuration.yaml` (no extra indentation).
- Restart Home Assistant after adding the component.

### Switch not toggling

- Confirm the `entity_id` points to a valid, available switch entity.
- Check that the switch supports `homeassistant.turn_on` / `homeassistant.turn_off`.
- Look at the HA logs at DEBUG level for the `custom_components.morse_code`
  logger to see the playback sequence.

### Overlapping playback

- If `morse_code.play` is called for the same entity while playback is already
  in progress, the current playback is automatically cancelled and the new one
  starts immediately.
- The switch is turned OFF when playback is cancelled before the new sequence
  begins.
- Different entities can play Morse code simultaneously without interference.
