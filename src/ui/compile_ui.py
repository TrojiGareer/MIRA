import subprocess, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import (
    SRC_DIR,
    UI_DIR,
    WIDGETS_DIR,
)

def compile_ui():
    # Directories to search for .ui files
    search_dirs = [Path(UI_DIR), Path(WIDGETS_DIR)]

    print(f"🚀 Starting UI compilation in {SRC_DIR}...")

    ui_files_found = 0

    for folder in search_dirs:
        if not folder.exists():
            print(f"⚠️  Skipping missing folder: {folder}")
            continue

        # Find all .ui files in the directory
        for ui_file in folder.glob("*.ui"):
            # Construct output filename: auto_<original_name>.py
            output_file = folder / f"auto_{ui_file.stem}.py"
            
            print(f"🔨 Compiling: {ui_file.name} -> {output_file.name}")
            
            # Execute pyuic6
            try:
                subprocess.run(
                    ["pyuic6", str(ui_file), "-o", str(output_file)],
                    check=True
                )
                ui_files_found += 1
            except subprocess.CalledProcessError as e:
                print(f"❌ Error compiling {ui_file.name}: {e}")
            except FileNotFoundError:
                print("❌ Error: 'pyuic6' not found.")
                return

    print(f"\n Compiling done! Processed {ui_files_found} files.")

if __name__ == "__main__":
    compile_ui()