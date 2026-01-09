#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mapping Loader
Module for loading drum mappings and conversion tables from XML files
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Set, Tuple, Optional
import sys


class MappingLoader:
    """Class for loading mapping files"""
    
    def __init__(self, mappings_dir: str = "mappings"):
        """
        Args:
            mappings_dir: Directory containing mapping files
        """
        self.mappings_dir = Path(mappings_dir)
        
        # Resolve path based on execution context (Frozen vs Script)
        if getattr(sys, 'frozen', False):
            # If frozen (PyInstaller), look in the same directory as the executable
            base_path = Path(sys.executable).parent
            self.mappings_dir = base_path / self.mappings_dir
        else:
            # If script, look in the assets directory (../assets relative to src)
            # base_path is the project root
            base_path = Path(__file__).parent.parent
            self.mappings_dir = base_path / "assets" / self.mappings_dir
        
        if not self.mappings_dir.exists():
            try:
                self.mappings_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created mappings directory: {self.mappings_dir}")
            except Exception as e:
                print(f"Failed to create mappings directory: {e}")
    
    
    def load_conversion_table(self, filename: str) -> Tuple[Dict[int, int], Dict[int, int]]:
        """
        Load conversion table and velocity override table from XML file
        
        Args:
            filename: Conversion table file name (e.g., "ssd5_to_musescore.xml")
            
        Returns:
            Tuple[Dict[int, int], Dict[int, int]]: 
                - Conversion table {source note: target note}
                - Velocity override table {source note: velocity value}
                
        Raises:
            FileNotFoundError: If file not found
            ValueError: If XML format is invalid
        """
        filepath = self.mappings_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(
                f"Conversion table file not found: {filepath}\n"
                f"Please make sure the file exists."
            )
        
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            conversion_table = {}
            velocity_overrides = {}
            
            # Helper to process a Note element
            def process_note(note_elem, default_to=None, default_velocity=None):
                from_str = note_elem.get('from')
                to_str = note_elem.get('to')
                velocity_str = note_elem.get('velocity')
                
                # If 'to' is not in Note, use default_to (from Group)
                if to_str is None and default_to is not None:
                    to_str = str(default_to)
                
                if from_str is None or to_str is None:
                    return
                
                try:
                    source = int(from_str)
                    target = int(to_str)
                    conversion_table[source] = target
                    
                    # Logic for velocity: Note > Group
                    velocity = None
                    if velocity_str is not None:
                         velocity = int(velocity_str)
                    elif default_velocity is not None:
                         velocity = default_velocity

                    if velocity is not None:
                        if 0 <= velocity <= 127:
                            velocity_overrides[source] = velocity
                        else:
                             print(f"Warning: Velocity value out of range (0-127): {velocity}", 
                                  file=sys.stderr)

                except ValueError:
                    print(f"Warning: Skipped invalid conversion entry: from={from_str} to={to_str}", 
                          file=sys.stderr)

            # 1. Load Group elements
            for group_elem in root.findall('Group'):
                group_to_str = group_elem.get('to')
                group_velocity_str = group_elem.get('velocity') # Optional velocity for group
                
                if group_to_str is None:
                    print("Warning: Group element missing 'to' attribute. Skipping.", file=sys.stderr)
                    continue
                
                try:
                    group_to = int(group_to_str)
                    group_velocity = None
                    if group_velocity_str is not None:
                         group_velocity = int(group_velocity_str)

                    for note_elem in group_elem.findall('Note'):
                        process_note(note_elem, default_to=group_to, default_velocity=group_velocity)
                except ValueError:
                     # Check which value caused error for better reporting
                    if group_velocity_str and not group_velocity_str.isdigit():
                         print(f"Warning: Invalid 'velocity' value in Group: {group_velocity_str}", file=sys.stderr)
                    else:
                         print(f"Warning: Invalid 'to' value in Group: {group_to_str}", file=sys.stderr)
            
            # 2. Load top-level Note elements (backward compatibility / mixed usage)
            for note_elem in root.findall('Note'):
                # ONLY process if it's a direct child of root (though findall on root finds direct children)
                # Ensure we are not reprocessing nodes if they were somehow reachable (findall only does direct children)
                process_note(note_elem)
            
            if not conversion_table:
                raise ValueError(
                    f"No conversion entries found in conversion table file: {filepath}\n"
                    f"<Group to=\"YY\"><Note from=\"XX\"/></Group> or <Note from=\"XX\" to=\"YY\"/> format entries are required."
                )
            
            return conversion_table, velocity_overrides
            
        except ET.ParseError as e:
            raise ValueError(
                f"XML parse error: {filepath}\n"
                f"Error details: {e}"
            )
    
    def list_available_mappings(self) -> list:
        """
        List available conversion table files
        
        Returns:
            list: List of conversion table files
        """
        if not self.mappings_dir.exists():
            return []
        
        conversion_tables = []
        
        for file in self.mappings_dir.glob('*.xml'):
            if 'to' in file.stem:  # Conversion table (e.g., ssd5_to_musescore.xml)
                conversion_tables.append(file.name)
        
        # Add built-in mode
        conversion_tables.sort()
        conversion_tables.insert(0, "as Source")
        
        return conversion_tables


def test_loader():
    """Loader test function"""
    try:
        loader = MappingLoader()
        
        print("=== Available conversion table files ===")
        available = loader.list_available_mappings()
        print(f"Conversion tables: {available}")
        print()
        
        # Load conversion tables
        print("=== MuseScore→SSD5 conversion table ===")
        try:
            conv_table1, velocity_overrides1 = loader.load_conversion_table("musescore_to_ssd5.xml")
            print(f"Conversion entries: {len(conv_table1)}")
            print(f"Velocity overrides: {len(velocity_overrides1)}")
        except Exception as e:
            print(f"Warning: Failed directly loading 'musescore_to_ssd5.xml' (may not exist or different format): {e}")

        
        print("=== SSD5→MuseScore conversion table ===")
        try:
            conv_table2, velocity_overrides2 = loader.load_conversion_table("SSD5 to MuseScore.xml") # Adjusted filename to likely existing one
            print(f"Conversion entries: {len(conv_table2)}")
            print(f"Velocity overrides: {len(velocity_overrides2)}")
            if velocity_overrides2:
                print(f"Velocity overrides:")
                for note, vel in sorted(velocity_overrides2.items()):
                    print(f"  Note {note}: velocity={vel}")
        except Exception as e:
             print(f"Warning: Failed loading 'SSD5 to MuseScore.xml': {e}")
        print()
        print()
        
        print("[OK] All mapping files loaded successfully")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}", file=sys.stderr)
        return False
    
    return True


if __name__ == '__main__':
    # Run test
    success = test_loader()
    sys.exit(0 if success else 1)
