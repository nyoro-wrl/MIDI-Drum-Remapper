#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIDI Drum Remapper
Drum mapping remapping tool
"""

import argparse
import sys
from pathlib import Path
from typing import Tuple, Optional

try:
    import mido
    from mido import MidiFile, MidiTrack
except ImportError:
    print("Error: mido library is not installed.")
    print("Please install it with the following command:")
    print("  pip install mido python-rtmidi")
    sys.exit(1)

try:
    from mapping_loader import MappingLoader
except ImportError:
    print("Error: mapping_loader.py not found.")
    print("Please make sure mapping_loader.py is in the same directory.")
    sys.exit(1)


class DrumMapRemapper:
    """Drum map remapping class"""
    
    CHANNEL_ONLY_MODE_NAME = "as Source"

    def __init__(self, mapping_file: str):
        """
        Args:
            mapping_file: Mapping file name (e.g., "SSD5 to MuseScore.xml")
        """
        self.channel_only_mode = (mapping_file == self.CHANNEL_ONLY_MODE_NAME)
        self.conversion_table = {}
        self.velocity_overrides = {}

        if not self.channel_only_mode:
            loader = MappingLoader()
            try:
                self.conversion_table, self.velocity_overrides = \
                    loader.load_conversion_table(mapping_file)
            except Exception as e:
                print(f"Error: Failed to load mapping file: {e}", file=sys.stderr)
                sys.exit(1)
    
    def remap_note(self, note: int) -> int:
        """
        Remap note
        
        Args:
            note: Source note number
            
        Returns:
            int: Remapped note number (or original if not found)
        """
        # If channel only mode, no remapping
        if self.channel_only_mode:
            return note

        # Use conversion table
        if note in self.conversion_table:
            return self.conversion_table[note]
        
        # Keep original note if not found
        return note
    
    def remap_midi_file(self, input_path: str, output_path: str) -> bool:
        """
        Remap MIDI file
        
        Args:
            input_path: Input MIDI file path
            output_path: Output MIDI file path
            
        Returns:
            True if successful
        """
        try:
            # Load MIDI file
            midi = MidiFile(input_path)
            
            # Create new MIDI file
            new_midi = MidiFile(type=midi.type, ticks_per_beat=midi.ticks_per_beat)
            
            # Process each track
            for track in midi.tracks:
                new_track = MidiTrack()
                
                for msg in track:
                    # Copy message
                    new_msg = msg.copy()
                    
                    # Remap note number for note_on/note_off messages
                    if msg.type in ['note_on', 'note_off']:
                        original_note = msg.note
                        original_velocity = msg.velocity
                        
                        # Force channel to 9 (MIDI Channel 10) for drums
                        new_msg.channel = 9
                        
                        # Remap note (only if not channel only mode, efficiently handled by remap_note)
                        new_msg.note = self.remap_note(original_note)
                        
                        # Velocity override (skip in channel only mode)
                        if not self.channel_only_mode and msg.type == 'note_on' and original_velocity > 0 and original_note in self.velocity_overrides:
                            new_msg.velocity = self.velocity_overrides[original_note]
                    
                    new_track.append(new_msg)
                
                new_midi.tracks.append(new_track)
            
            # Save file
            new_midi.save(output_path)
            return True
            
        except FileNotFoundError:
            print(f"Error: File not found: {input_path}")
            return False
        except Exception as e:
            print(f"Error: Conversion failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='MIDI Drum Remapper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remap SSD5 to MuseScore
  python midi_drum_remapper.py -f input.mid -m "SSD5 to MuseScore.xml"
  
  # Remap MuseScore to SSD5
  python midi_drum_remapper.py -f input.mid -m "MuseScore to SSD5.xml"
  
  # Specify output file name
  python midi_drum_remapper.py -f input.mid -m "SSD5 to MuseScore.xml" -o output.mid
        """
    )
    
    parser.add_argument(
        '-f', '--file',
        required=True,
        help='Input MIDI file path'
    )
    
    parser.add_argument(
        '-m', '--mapping',
        required=True,
        help='Mapping file name (e.g., "SSD5 to MuseScore.xml")'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output MIDI file path (auto-generated if not specified)'
    )
    
    args = parser.parse_args()
    
    # Check input file existence
    input_path = Path(args.file)
    if not input_path.exists():
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    # Determine output file name
    if args.output:
        output_path = Path(args.output)
    else:
        # Auto-generate: original filename + "_remap"
        output_path = input_path.parent / f"{input_path.stem}_remap{input_path.suffix}"
    
    # Execute remapping
    print(f"Remapping: {input_path.name}")
    print(f"Mapping: {args.mapping}")
    print(f"Output: {output_path.name}")
    
    remapper = DrumMapRemapper(args.mapping)
    success = remapper.remap_midi_file(str(input_path), str(output_path))
    
    if success:
        print(f"✓ Remapping complete: {output_path}")
    else:
        print("✗ Remapping failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
