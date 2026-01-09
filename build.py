import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    print("Starting build process...")
    
    # Define build arguments
    args = [
        'src/midi_drum_remapper_gui.py',  # Main script in src
        '--name=MIDI Drum Remapper',      # Executable name
        '--noconsole',                    # Windowed mode (no console)
        '--onefile',                      # Single EXE file
        '--clean',                        # Clean cache
        # Exclude mappings folder from bundling
    ]
    
    # Add icon if available (placeholder logic)
    # if Path("icon.ico").exists():
    #     args.append('--icon=icon.ico')
    
    print(f"Running PyInstaller with args: {args}")
    
    try:
        PyInstaller.__main__.run(args)
        print("\nBuild completed successfully!")
        
        # Auto-copy assets
        import shutil
        
        dist_dir = Path("dist")
        assets_src = Path("assets")
        
        if assets_src.exists():
            print(f"Copying assets from {assets_src} to {dist_dir}...")
            for item in assets_src.iterdir():
                dest = dist_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                
                if item.is_dir():
                    shutil.copytree(item, dest)
                else:
                    shutil.copy2(item, dest)
            print("Assets copied successfully.")
        else:
            print(f"Warning: Assets directory not found at {assets_src}")

        print("\nExecutable is located in the 'dist' folder.")
        print("Required 'mappings' folder has been bundled next to the .exe file.")
    except Exception as e:
        print(f"\nBuild failed: {e}")

if __name__ == "__main__":
    build()
