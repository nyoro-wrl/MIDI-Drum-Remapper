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
        else:
            # If script, look in the script's directory
            base_path = Path(__file__).parent
            
        if not self.mappings_dir.is_absolute():
            self.mappings_dir = base_path / self.mappings_dir
        
        if not self.mappings_dir.exists():
            try:
                self.mappings_dir.mkdir(parents=True, exist_ok=True)
                print(f"Created mappings directory: {self.mappings_dir}")
            except Exception as e:
                print(f"Failed to create mappings directory: {e}")
    
    
    def load_conversion_table(self, filename: str) -> Tuple[Dict[int, int], Dict[int, int], Dict[int, Dict[int, Tuple[int, Optional[int]]]]]:
        """
        Load conversion table, velocity override table, and conditional mappings from XML file
        
        Args:
            filename: Conversion table file name (e.g., "ssd5_to_musescore.xml")
            
        Returns:
            Tuple[Dict[int, int], Dict[int, int], Dict[int, Dict[int, Tuple[int, Optional[int]]]]]: 
                - Conversion table {source note: target note}
                - Velocity override table {source note: velocity value}
                - Conditional mappings {input velocity: {source note: (target note, output velocity)}}
                
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
            conditional_mappings = {}  # {velocity: {from_note: (to_note, output_velocity)}}
            
            # Load If elements (conditional mappings)
            for if_elem in root.findall('If'):
                condition_velocity_str = if_elem.get('velocity')
                if condition_velocity_str is None:
                    print(f"Warning: If element has no velocity attribute. Skipping.", file=sys.stderr)
                    continue
                
                try:
                    condition_velocity = int(condition_velocity_str)
                    if not (0 <= condition_velocity <= 127):
                        print(f"Warning: If condition velocity value out of range (0-127): {condition_velocity}", 
                              file=sys.stderr)
                        continue
                    
                    # Load Note elements under this condition
                    if condition_velocity not in conditional_mappings:
                        conditional_mappings[condition_velocity] = {}
                    
                    for note_elem in if_elem.findall('Note'):
                        from_str = note_elem.get('from')
                        to_str = note_elem.get('to')
                        output_velocity_str = note_elem.get('velocity')
                        
                        if from_str is None or to_str is None:
                            continue
                        
                        try:
                            source = int(from_str)
                            target = int(to_str)
                            output_velocity = None
                            
                            if output_velocity_str is not None:
                                output_velocity = int(output_velocity_str)
                                if not (0 <= output_velocity <= 127):
                                    print(f"Warning: Output velocity value out of range (0-127): {output_velocity}", 
                                          file=sys.stderr)
                                    output_velocity = None
                            
                            conditional_mappings[condition_velocity][source] = (target, output_velocity)
                            
                        except ValueError:
                            print(f"Warning: Skipped invalid conditional conversion entry: {from_str} → {to_str}", 
                                  file=sys.stderr)
                            continue
                    
                except ValueError:
                    print(f"Warning: Skipped invalid If condition: velocity={condition_velocity_str}", 
                          file=sys.stderr)
                    continue
            
            # Load normal Note elements (outside If elements)
            for note_elem in root.findall('Note'):
                # Skip Notes inside If elements (already processed)
                parent = None
                for if_elem in root.findall('If'):
                    if note_elem in if_elem.findall('Note'):
                        parent = if_elem
                        break
                
                if parent is not None:
                    continue  # Skip Notes inside If elements
                
                from_str = note_elem.get('from')
                to_str = note_elem.get('to')
                velocity_str = note_elem.get('velocity')  # Optional
                
                if from_str is None or to_str is None:
                    continue
                
                try:
                    source = int(from_str)
                    target = int(to_str)
                    conversion_table[source] = target
                    
                    # Add to override table if velocity attribute exists
                    if velocity_str is not None:
                        velocity = int(velocity_str)
                        if 0 <= velocity <= 127:
                            velocity_overrides[source] = velocity
                        else:
                            print(f"Warning: Velocity value out of range (0-127): {velocity}", 
                                  file=sys.stderr)
                    
                except ValueError:
                    print(f"Warning: Skipped invalid conversion entry: {from_str} → {to_str}", 
                          file=sys.stderr)
                    continue
            
            if not conversion_table and not conditional_mappings:
                raise ValueError(
                    f"No conversion entries found in conversion table file: {filepath}\n"
                    f"<Note from=\"XX\" to=\"YY\"/> format entries are required."
                )
            
            return conversion_table, velocity_overrides, conditional_mappings
            
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
        
        return sorted(conversion_tables)


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
        conv_table1, velocity_overrides1, conditional1 = loader.load_conversion_table("musescore_to_ssd5.xml")
        print(f"Conversion entries: {len(conv_table1)}")
        print(f"Velocity overrides: {len(velocity_overrides1)}")
        print(f"Conditional mappings: {len(conditional1)}")
        if conditional1:
            print(f"Conditional mappings:")
            for vel, mappings in sorted(conditional1.items()):
                print(f"  velocity={vel}: {len(mappings)} entries")
                for from_note, (to_note, out_vel) in sorted(mappings.items()):
                    vel_info = f", output_velocity={out_vel}" if out_vel is not None else ""
                    print(f"    Note {from_note} → {to_note}{vel_info}")
        print()
        
        print("=== SSD5→MuseScore conversion table ===")
        conv_table2, velocity_overrides2, conditional2 = loader.load_conversion_table("ssd5_to_musescore.xml")
        print(f"Conversion entries: {len(conv_table2)}")
        print(f"Velocity overrides: {len(velocity_overrides2)}")
        print(f"Conditional mappings: {len(conditional2)}")
        if velocity_overrides2:
            print(f"Velocity overrides:")
            for note, vel in sorted(velocity_overrides2.items()):
                print(f"  Note {note}: velocity={vel}")
        if conditional2:
            print(f"Conditional mappings:")
            for vel, mappings in sorted(conditional2.items()):
                print(f"  velocity={vel}: {len(mappings)} entries")
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
