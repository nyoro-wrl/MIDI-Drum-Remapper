import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    print("Starting build process...")
    
    # Define build arguments
    args = [
        'midi_drum_remapper_gui.py',  # Main script
        '--name=MIDI Drum Remapper',  # Executable name
        '--noconsole',                # Windowed mode (no console)
        '--onefile',                  # Single EXE file
        '--clean',                    # Clean cache
        # Exclude mappings folder from bundling (we want it external)
        # Note: We don't need explicit excludes usually, just don't include it.
    ]
    
    # Add icon if available (placeholder logic)
    # if Path("icon.ico").exists():
    #     args.append('--icon=icon.ico')
    
    print(f"Running PyInstaller with args: {args}")
    
    try:
        PyInstaller.__main__.run(args)
        print("\nBuild completed successfully!")
        print("Executable is located in the 'dist' folder.")
        print("IMPORTANT: Make sure to copy the 'mappings' folder next to the .exe file!")
    except Exception as e:
        print(f"\nBuild failed: {e}")

if __name__ == "__main__":
    build()
