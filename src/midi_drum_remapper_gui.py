#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIDI Drum Remapper - PySide6 GUI
Drum mapping remapping tool (Professional GUI application)
"""

import sys
import json
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QComboBox, QProgressBar,
    QTextEdit, QFileDialog, QCheckBox, QLineEdit, QFrame,
    QMessageBox, QListWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QPropertyAnimation, QEasingCurve, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtMultimedia import QSoundEffect

try:
    from midi_drum_remapper import DrumMapRemapper
    from mapping_loader import MappingLoader
    from styles_qt import DARK_THEME
except ImportError as e:
    print(f"Error: Required module not found: {e}")
    sys.exit(1)


class RemappingThread(QThread):
    """Remapping processing thread"""
    progress = Signal(int, int, int)  # current, total, percentage
    finished = Signal(list)
    error = Signal(str)
    
    def __init__(self, files: List[Path], mapping_file: str, output_template: str, default_suffix: str = "_remap"):
        super().__init__()
        self.files = files
        self.mapping_file = mapping_file
        self.output_template = output_template
        self.default_suffix = default_suffix

    def build_output_path(self, input_file: Path) -> Path:
        template = self.output_template.strip()
        if not template:
            return input_file.parent / f"{input_file.stem}{self.default_suffix}{input_file.suffix}"

        placeholders = {
            "{filename}": input_file.stem,
            "{ext}": input_file.suffix,
            "{input_dir}": str(input_file.parent)
        }

        if any(key in template for key in placeholders):
            for key, value in placeholders.items():
                template = template.replace(key, value)
            return Path(template)

        candidate = Path(template)
        if candidate.suffix.lower() in [".mid", ".midi"]:
            return candidate

        return candidate / f"{input_file.stem}{self.default_suffix}{input_file.suffix}"

    def run(self):
        try:
            remapper = DrumMapRemapper(self.mapping_file)
            results = []
            total = len(self.files)
            
            for i, input_file in enumerate(self.files):
                # Determine output path
                output_file = self.build_output_path(input_file)

                # Execute remapping
                success = remapper.remap_midi_file(str(input_file), str(output_file))
                
                results.append({
                    'input': input_file,
                    'output': output_file,
                    'success': success
                })
                
                # Notify progress
                percentage = int(((i + 1) / total) * 100)
                self.progress.emit(i + 1, total, percentage)
            
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class FileSelectArea(QFrame):
    """Integrated file selection area (button + drag&drop + file display)"""
    files_selected = Signal(list)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setProperty("dropzone", True)
        self.setMinimumHeight(110)
        self.setCursor(Qt.PointingHandCursor)
        self.is_dragging = False
        
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(8)
        
        # Icon label (file icon style)
        self.icon_label = QLabel("📁")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("font-size: 24pt;")
        layout.addWidget(self.icon_label)
        
        # Main text
        self.main_label = QLabel("Click to select file")
        self.main_label.setAlignment(Qt.AlignCenter)
        self.main_label.setStyleSheet("color: #E0E0E0; font-size: 10pt; font-weight: 500;")
        self.main_label.setWordWrap(True)
        layout.addWidget(self.main_label)
        
        # Sub text
        self.sub_label = QLabel("or drop file here")
        self.sub_label.setAlignment(Qt.AlignCenter)
        self.sub_label.setStyleSheet("color: #757575; font-size: 9pt;")
        self.sub_label.setWordWrap(True)
        layout.addWidget(self.sub_label)
        
        # File list (for multiple files)
        self.file_list_label = QLabel("")
        self.file_list_label.setAlignment(Qt.AlignCenter)
        self.file_list_label.setStyleSheet("color: #9E9E9E; font-size: 8pt; margin-top: 5px; line-height: 1.4;")
        self.file_list_label.setWordWrap(True)
        self.file_list_label.hide()
        layout.addWidget(self.file_list_label)
    
    def mousePressEvent(self, event):
        """Open file selection dialog on click"""
        if event.button() == Qt.LeftButton:
            # Reset display
            self.reset_display()
            self.open_file_dialog()
    
    def reset_display(self):
        """Reset display to waiting state"""
        self.icon_label.show()
        self.icon_label.setText("📁")
        self.icon_label.setStyleSheet("font-size: 24pt;")
        self.main_label.setText("Drop file to remap")
        self.main_label.setStyleSheet("color: #E0E0E0; font-size: 10pt; font-weight: 500;")
        self.sub_label.setText("Click to select file")
        self.sub_label.setStyleSheet("color: #757575; font-size: 9pt;")
        self.sub_label.show()
        self.file_list_label.hide()
    
    def open_file_dialog(self):
        """File selection dialog"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select MIDI file",
            "",
            "MIDI files (*.mid *.midi);;All files (*.*)"
        )
        
        if files:
            file_paths = [Path(f) for f in files]
            self.files_selected.emit(file_paths)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Reset display
            self.reset_display()
            self.highlight(True)
    
    def dragLeaveEvent(self, event):
        self.highlight(False)
    
    def dropEvent(self, event: QDropEvent):
        self.highlight(False)
        
        files = []
        for url in event.mimeData().urls():
            file_path = Path(url.toLocalFile())
            if file_path.suffix.lower() in ['.mid', '.midi']:
                files.append(file_path)
        
        if files:
            self.files_selected.emit(files)
    
    def highlight(self, active: bool):
        """Toggle highlight display"""
        if active:
            self.setStyleSheet("""
                QFrame[dropzone="true"] {
                    background-color: #1A237E;
                    border-color: #1E88E5;
                }
            """)
        else:
            self.setStyleSheet("")
            self.setProperty("dropzone", True)
            self.style().unpolish(self)
            self.style().polish(self)
    
    def update_display(self, file_count: int, file_names: List[str]):
        """Update display"""
        if file_count == 0:
            self.icon_label.show()
            self.icon_label.setText("📁")
            self.main_label.setText("Drop file to remap")
            self.main_label.setStyleSheet("color: #E0E0E0; font-size: 10pt; font-weight: 500;")
            self.sub_label.setText("Click to select file")
            self.sub_label.setStyleSheet("color: #757575; font-size: 9pt;")
            self.sub_label.show()
            self.file_list_label.hide()
        elif file_count == 1:
            self.icon_label.show()
            self.icon_label.setText("⏳")
            self.main_label.setText(file_names[0])
            self.main_label.setStyleSheet("color: #1E88E5; font-size: 10pt; font-weight: 500;")
            self.sub_label.setText("Remapping...")
            self.sub_label.setStyleSheet("color: #2196F3; font-size: 9pt;")
            self.sub_label.show()
            self.file_list_label.hide()
        else:
            self.icon_label.show()
            self.icon_label.setText("⏳")
            self.main_label.setText(f"{file_count} files")
            self.main_label.setStyleSheet("color: #1E88E5; font-size: 10pt; font-weight: 500;")
            self.sub_label.setText("Remapping...")
            self.sub_label.setStyleSheet("color: #2196F3; font-size: 9pt;")
            self.sub_label.show()
            # Display file list (subtle)
            file_list_text = "\n".join(file_names)
            self.file_list_label.setText(file_list_text)
            self.file_list_label.show()
    
    def show_complete(self, success: bool, success_count: int, total_count: int):
        """Display remapping complete"""
        if success:
            self.icon_label.show()
            self.icon_label.setText("✓")
            self.icon_label.setStyleSheet("font-size: 32pt; color: #10B981;")
            self.main_label.setText("Complete")
            self.main_label.setStyleSheet("color: #10B981; font-size: 12pt; font-weight: 600;")
            self.sub_label.setText("Drop next file")
            self.sub_label.setStyleSheet("color: #757575; font-size: 9pt;")
            self.sub_label.show()
            self.file_list_label.hide()
        else:
            self.icon_label.show()
            self.icon_label.setText("⚠")
            self.icon_label.setStyleSheet("font-size: 32pt; color: #F59E0B;")
            self.main_label.setText(f"Partial failure ({success_count}/{total_count})")
            self.main_label.setStyleSheet("color: #F59E0B; font-size: 11pt; font-weight: 600;")
            self.sub_label.setText("Drop next file")
            self.sub_label.setStyleSheet("color: #757575; font-size: 9pt;")
            self.sub_label.show()
            self.file_list_label.hide()
    
    def show_error(self, error_msg: str):
        """Display error"""
        self.icon_label.show()
        self.icon_label.setText("✗")
        self.icon_label.setStyleSheet("font-size: 32pt; color: #EF4444;")
        self.main_label.setText("Error")
        self.main_label.setStyleSheet("color: #EF4444; font-size: 11pt; font-weight: 600;")
        self.sub_label.setText(error_msg[:50])
        self.sub_label.setStyleSheet("color: #EF4444; font-size: 8pt;")
        self.sub_label.show()
        self.file_list_label.hide()


class MidiDrumRemapperGUI(QMainWindow):
    """MIDI Drum Remapper GUI class (PySide6 version)"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("MIDI Drum Remapper")
        self.setGeometry(100, 100, 400, 260)
        
        # Determine config file path
        if getattr(sys, 'frozen', False):
            base_path = Path(sys.executable).parent
        else:
            # If running from src, keep config in project root for easier access
            base_path = Path(__file__).parent.parent
            
        self.config_file = base_path / "config.json"
        
        # Font settings
        self.default_font = ("Segoe UI", 9)
        self.title_font = ("Segoe UI", 16, "bold")
        self.heading_font = ("Segoe UI", 10, "bold")
        
        # Initialize variables
        self.input_files: List[Path] = []
        self.mapping_files: List[str] = []
        self.mapping_display_names: List[str] = []
        self.is_converting = False
        self.remapping_thread: Optional[RemappingThread] = None
        self.output_template = ""
        self.output_dir = ""
        self.use_same_folder = True  # Default: True
        self.default_suffix = "_remap"
        self.open_explorer = False # Default: False
        self.settings_expanded = False
        
        # Apply dark theme
        self.setStyleSheet(DARK_THEME)
        
        # Enable drag&drop for entire window
        self.setAcceptDrops(True)
        
        # Setup completion sound
        self.setup_sound()
        
        # Build UI
        self.setup_ui()
        
        # Load mapping files
        self.load_mappings()
        
        # Load config
        self.load_config()
        
        # Set initial size and center
        self.resize(500, 260)
        self.center()
    
    def center(self):
        """Center window on screen"""
        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def setup_sound(self):
        """Setup completion sound"""
        try:
            self.success_sound = QSoundEffect()
            # Use Windows standard notification sound
            self.success_sound.setSource(QUrl.fromLocalFile("C:/Windows/Media/Windows Notify System Generic.wav"))
            self.success_sound.setVolume(0.5)
        except:
            self.success_sound = None
    
    def setup_ui(self):
        """Build UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Mapping selection
        self.mapping_combo = QComboBox()
        self.mapping_combo.setMinimumHeight(32)
        main_layout.addWidget(self.mapping_combo)        
        # Output settings (collapsible)
        self.settings_toggle_btn = QPushButton("Output Settings ▽")
        self.settings_toggle_btn.setProperty("secondary", True)
        self.settings_toggle_btn.setMinimumHeight(28)
        self.settings_toggle_btn.setStyleSheet("padding: 4px 10px;")
        self.settings_toggle_btn.clicked.connect(self.toggle_settings)
        main_layout.addWidget(self.settings_toggle_btn)
        
        # Settings panel (hidden by default)
        self.settings_panel = QWidget()
        settings_layout = QVBoxLayout(self.settings_panel)
        settings_layout.setContentsMargins(0, 5, 0, 0)
        settings_layout.setSpacing(8)
        
        # 'Same as input' Checkbox
        self.same_folder_check = QCheckBox("Output to same folder as input")
        self.same_folder_check.setStyleSheet("font-size: 9pt; color: #E0E0E0;")
        self.same_folder_check.setChecked(True) # Default True
        self.same_folder_check.stateChanged.connect(self.toggle_output_controls)
        settings_layout.addWidget(self.same_folder_check)
        
        # Output Directory Row
        out_dir_layout = QHBoxLayout()
        out_dir_layout.setSpacing(5)
        
        self.dir_label_title = QLabel("Output Dir:")
        self.dir_label_title.setStyleSheet("color: #9E9E9E; font-size: 8pt;")
        out_dir_layout.addWidget(self.dir_label_title)
        
        self.out_dir_val_label = QLabel("Select folder...")
        self.out_dir_val_label.setStyleSheet("color: #BDBDBD; font-size: 8pt;") # Default style
        out_dir_layout.addWidget(self.out_dir_val_label, 1)
        
        self.dir_btn = QPushButton("Select")
        self.dir_btn.setMinimumWidth(80) # Changed to minimum width
        self.dir_btn.setProperty("secondary", True)
        self.dir_btn.setStyleSheet("padding: 4px 8px;") # Reduce padding for this specific button
        self.dir_btn.clicked.connect(self.select_output_dir)
        out_dir_layout.addWidget(self.dir_btn)
        
        settings_layout.addLayout(out_dir_layout)

        # File Name Row
        template_layout = QHBoxLayout()
        template_layout.setSpacing(5)
        template_label = QLabel("File Name:") # Changed label
        template_label.setStyleSheet("color: #9E9E9E; font-size: 8pt;")
        template_layout.addWidget(template_label)

        self.output_template_entry = QLineEdit()
        self.output_template_entry.setText("{filename}_remap{ext}") # Default value
        self.output_template_entry.setPlaceholderText("{filename}_remap{ext}")
        self.output_template_entry.setMinimumHeight(24)
        self.output_template_entry.setStyleSheet("font-size: 8pt; padding: 4px 8px;")
        template_layout.addWidget(self.output_template_entry, 1)
        
        # Select button removed from here
        
        settings_layout.addLayout(template_layout)

        # Open explorer checkbox
        self.open_explorer_check = QCheckBox("Open folder after remapping")
        self.open_explorer_check.setStyleSheet("font-size: 9pt; color: #E0E0E0;")
        self.open_explorer_check.setChecked(False) # Default False
        settings_layout.addWidget(self.open_explorer_check)
        
        main_layout.addWidget(self.settings_panel)
        self.settings_panel.hide()

        
        # Integrated file selection area
        self.file_select_area = FileSelectArea()
        self.file_select_area.files_selected.connect(self.on_files_selected)
        main_layout.addWidget(self.file_select_area)

        
        # Add stretch to adjust layout
        main_layout.addStretch()
    
    def load_mappings(self):
        """Load mapping files"""
        try:
            loader = MappingLoader()
            self.mapping_files = loader.list_available_mappings()
            
            if self.mapping_files:
                self.mapping_display_names = [Path(f).stem for f in self.mapping_files]
                self.mapping_combo.addItems(self.mapping_display_names)
            else:
                QMessageBox.warning(self, "Warning", 
                    "No mapping files found.\nPlease place XML files in mappings/ folder.")
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Failed to load mapping files:\n{e}")
    
    def get_actual_mapping_file(self, display_name: str) -> Optional[str]:
        """Get actual file name from display name"""
        try:
            index = self.mapping_display_names.index(display_name)
            return self.mapping_files[index]
        except (ValueError, IndexError):
            return None
    
    def on_files_selected(self, files: List[Path]):
        """File selection/drop handler (overwrite)"""
        # Clear existing files and set new files
        self.input_files = list(files)
        self.update_file_display()
        
        # Start remapping automatically
        self.start_remapping()
    
    def toggle_settings(self):
        """Toggle output settings panel"""
        self.settings_expanded = not self.settings_expanded
        if self.settings_expanded:
            self.settings_panel.show()
            self.settings_toggle_btn.setText("Output Settings △")
            self.setFixedHeight(400) # Increased height to fit new controls
        else:
            self.settings_panel.hide()
            self.settings_toggle_btn.setText("Output Settings ▽")
            self.setFixedHeight(260)
            
    def toggle_output_controls(self):
        """Toggle output directory controls based on checkbox"""
        use_same = self.same_folder_check.isChecked()
        self.use_same_folder = use_same
        
        self.dir_label_title.setEnabled(not use_same)
        self.out_dir_val_label.setEnabled(not use_same)
        self.dir_btn.setEnabled(not use_same)
        
        # Determine label text (Always show selected dir or placeholder)
        if self.output_dir:
            self.out_dir_val_label.setText(self.output_dir)
        else:
            self.out_dir_val_label.setText("Select folder...")

        # Apply styles based on state
        if use_same:
            self.out_dir_val_label.setStyleSheet("color: #505050; font-size: 8pt;") # Disabled look (no italic)
            self.dir_label_title.setStyleSheet("color: #505050; font-size: 8pt;")
        else:
            self.dir_label_title.setStyleSheet("color: #9E9E9E; font-size: 8pt;") # Enabled label
            if self.output_dir:
                self.out_dir_val_label.setStyleSheet("color: #E0E0E0; font-size: 8pt;")
            else:
                self.out_dir_val_label.setStyleSheet("color: #EF5350; font-size: 8pt;") # Error/Warning color but consistent font
    
    def select_output_dir(self):
        """Output directory selection dialog"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select output folder"
        )
        if directory:
            self.output_dir = str(Path(directory))
            self.out_dir_val_label.setText(self.output_dir)
            self.out_dir_val_label.setStyleSheet("color: #E0E0E0; font-size: 8pt;")
            # No longer updates text entry
    
    def update_file_display(self):
        """Update file display"""
        file_count = len(self.input_files)
        file_names = [f.name for f in self.input_files]
        
        self.file_select_area.update_display(file_count, file_names)
    
    def start_remapping(self):
        """Start remapping process"""
        # Input check
        if not self.input_files:
            return
        
        if self.mapping_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Warning", "Please select a mapping file.")
            return
        
        display_name = self.mapping_combo.currentText()
        actual_mapping = self.get_actual_mapping_file(display_name)
        if not actual_mapping:
            QMessageBox.critical(self, "Error", "Selected mapping file not found.")
            return
        
        if self.is_converting:
            return
        
        # Get output settings (moved up before state change)
        filename_template = self.output_template_entry.text().strip()
        if not filename_template:
            filename_template = "{filename}_remap{ext}"
            
        # Check for existing files (Overwrite Protection)
        # Check for existing files (Overwrite Protection)
        files_to_process = self.check_and_filter_files(self.input_files, filename_template)
        # If cancelled or all skipped (empty list but inputs existed), reset UI
        if not files_to_process:
            self.file_select_area.reset_display()
            return

        final_template = ""
        if self.use_same_folder:
            # Use {input_dir} placeholder to ensure absolute path relative to input file
            final_template = str(Path("{input_dir}") / filename_template)
        else:
            if not self.output_dir:
                # Force selection if not set
                self.select_output_dir()
                # If still not set (user cancelled), abort
                if not self.output_dir:
                    return
            final_template = str(Path(self.output_dir) / filename_template)
        
        # Change UI state (only after all checks pass)
        self.is_converting = True
        
        # Start thread
        self.remapping_thread = RemappingThread(
            files_to_process,
            actual_mapping,
            final_template
        )
        self.remapping_thread.progress.connect(self.on_progress)
        self.remapping_thread.finished.connect(self.on_remapping_complete)
        self.remapping_thread.error.connect(self.on_remapping_error)
        self.remapping_thread.start()
    
    def on_progress(self, current: int, total: int, percentage: int):
        """Progress update"""
        # Progress bar removed, do nothing
        pass
    
    def on_remapping_complete(self, results: list):
        """Remapping complete handler"""
        self.is_converting = False
        
        success_count = sum(1 for r in results if r['success'])
        total_count = len(results)
        
        # Display complete in drop zone
        if success_count == total_count:
            self.file_select_area.show_complete(True, success_count, total_count)
            # Play complete sound
            if self.success_sound:
                self.success_sound.play()
            
            # Open explorer if enabled
            if self.open_explorer_check.isChecked() and results:
                output_path = results[0]['output']
                import subprocess
                subprocess.run(['explorer', '/select,', str(output_path)])
        else:
            self.file_select_area.show_complete(False, success_count, total_count)
    
    def on_remapping_error(self, error_msg: str):
        """Remapping error handler"""
        self.is_converting = False
        self.file_select_area.show_error(error_msg)
    
    def load_config(self):
        """Load config from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Restore last selected mapping
                last_mapping = config.get('last_mapping')
                if last_mapping and last_mapping in self.mapping_display_names:
                    index = self.mapping_display_names.index(last_mapping)
                    self.mapping_combo.setCurrentIndex(index)
                # Restore output settings
                # Restore output settings
                if 'use_same_folder' in config:
                    self.use_same_folder = config['use_same_folder']
                    self.same_folder_check.setChecked(self.use_same_folder)
                
                if 'output_dir' in config:
                    self.output_dir = config['output_dir']
                    if self.output_dir and not self.use_same_folder:
                        self.out_dir_val_label.setText(self.output_dir)
                        self.out_dir_val_label.setStyleSheet("color: #E0E0E0; font-size: 8pt;")
                
                # Update controls state
                self.toggle_output_controls() # Apply state to UI
                
                if 'filename_template' in config:
                    self.output_template_entry.setText(config['filename_template'])
                elif 'output_template' in config:
                    # Migration from old config if possible, or just ignore complex ones
                    pass 

                self.open_explorer = config.get('open_explorer', False) # Default False if missing
                self.open_explorer_check.setChecked(self.open_explorer)
                
        except Exception as e:
            print(f"Failed to load config file: {e}")
    
    def save_config(self):
        """Save config to file"""
        try:
            config = {
                'last_mapping': self.mapping_combo.currentText() if self.mapping_combo.currentIndex() >= 0 else "",
                'filename_template': self.output_template_entry.text().strip(),
                'output_dir': self.output_dir,
                'use_same_folder': self.same_folder_check.isChecked(), # New config
                'open_explorer': self.open_explorer_check.isChecked()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to save config file: {e}")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Drag enter handler for entire window"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Highlight file selection area
            self.file_select_area.highlight(True)
    
    def dragLeaveEvent(self, event):
        """Drag leave handler"""
        self.file_select_area.highlight(False)
    
    def dropEvent(self, event: QDropEvent):
        """Drop handler for entire window"""
        self.file_select_area.highlight(False)
        
        files = []
        for url in event.mimeData().urls():
            file_path = Path(url.toLocalFile())
            if file_path.suffix.lower() in ['.mid', '.midi']:
                files.append(file_path)
        
        if files:
            self.on_files_selected(files)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def check_and_filter_files(self, files: List[Path], filename_template: str) -> List[Path]:
        """Check for existing files and ask user"""
        
        # Helper to predict output path (logic from Thread)
        def predict_output(input_file: Path) -> Path:
            template = filename_template
            
            # Determine base directory
            base_dir = input_file.parent if self.use_same_folder else Path(self.output_dir)
            
            placeholders = {
                "{filename}": input_file.stem,
                "{ext}": input_file.suffix,
                "{input_dir}": str(input_file.parent)
            }
            
            for key, value in placeholders.items():
                template = template.replace(key, value)
                
            return base_dir / template

        existing_files = []
        for f in files:
            try:
                out_path = predict_output(f)
                if out_path.exists():
                    existing_files.append((f, out_path))
            except:
                pass
        
        if not existing_files:
            return files

        # Conflict resolution logic
        final_files = []
        overwrite_all = False
        skip_all = False
        
        # Add non-conflicting files first
        conflicting_inputs = [i for i, _ in existing_files]
        final_files.extend([f for f in files if f not in conflicting_inputs])

        # Process conflicts
        total_conflicts = len(existing_files)
        
        for input_file, out_path in existing_files:
            if skip_all:
                continue
            
            if overwrite_all:
                final_files.append(input_file)
                continue
                
            # Show Dialog for individual conflict
            msg = QMessageBox(self)
            msg.setWindowTitle("Confirm Overwrite")
            msg.setText(f"File already exists:\n{out_path.name}")
            msg.setInformativeText("Would you like to overwrite it?")
            msg.setIcon(QMessageBox.Question)
            
            # Checkbox for "Apply to all" (only if multiple conflicts)
            cb = None
            if total_conflicts > 1:
                cb = QCheckBox("Apply to all conflicts")
                msg.setCheckBox(cb)
            
            overwrite_btn = msg.addButton("Overwrite", QMessageBox.YesRole)
            
            # Skip button (only if multiple conflicts)
            skip_btn = None
            if total_conflicts > 1:
                skip_btn = msg.addButton("Skip", QMessageBox.NoRole)
                
            cancel_btn = msg.addButton(QMessageBox.Cancel)
            
            msg.exec()
            
            apply_to_all = cb.isChecked() if cb else False
            
            clicked = msg.clickedButton()
            
            if clicked == cancel_btn:
                return [] # Abort everything
            
            if clicked == overwrite_btn:
                final_files.append(input_file)
                if apply_to_all:
                    overwrite_all = True
            
            elif skip_btn and clicked == skip_btn:
                if apply_to_all:
                    skip_all = True
                    
        return final_files

    def closeEvent(self, event):
        """Window close handler"""
        self.save_config()
        event.accept()


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    window = MidiDrumRemapperGUI()
    window.show()
    
    # Check for command line arguments (files dropped onto exe)
    if len(sys.argv) > 1:
        initial_files = []
        for arg in sys.argv[1:]:
            path = Path(arg)
            if path.exists() and path.suffix.lower() in ['.mid', '.midi']:
                initial_files.append(path)
        
        if initial_files:
            # Delay slightly to ensure window is ready
            # Use QTimer.singleShot is safest for UI updates after show
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: window.on_files_selected(initial_files))

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
