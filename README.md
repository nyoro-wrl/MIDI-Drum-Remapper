# MIDI Drum Remapper

Remap MIDI drum mappings between any formats.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### GUI Mode (Recommended)

```bash
python midi_drum_remapper_gui.py
```

**GUI Features:**
- Professional design (PySide6/Qt)
- Material Design style dark UI
- Drag & drop file support
- Automatic remapping on drop
- Completion sound notification

### Command Line Mode

```bash
python midi_drum_remapper.py -f <input_file> -m <mapping_file> [-o <output_file>]
```

#### Options

- `-f`, `--file`: Input MIDI file path (required)
- `-m`, `--mapping`: Mapping file name (required)
- `-o`, `--output`: Output MIDI file path (auto-generated if not specified)

#### Examples

```bash
# SSD5 → MuseScore
python midi_drum_remapper.py -f input.mid -m "SSD5 to MuseScore.xml"

# MuseScore → SSD5
python midi_drum_remapper.py -f input.mid -m "MuseScore to SSD5.xml"

# Specify output file name
python midi_drum_remapper.py -f input.mid -m "SSD5 to MuseScore.xml" -o output.mid
```

## Mapping Files

Place mapping files in the `mappings/` folder.

Currently provided mappings:
- `SSD5 to MuseScore.xml` - SSD5 to MuseScore remapping
- `MuseScore to SSD5.xml` - MuseScore to SSD5 remapping

You can create custom mapping files to remap between other drum sources.

## License

MIT License
