import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QTextEdit, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import logging
from main import process_files

class WorkerThread(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, input_folder, output_folder):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder

    def run(self):
        try:
            # Create a custom logging handler that emits to our progress signal
            class SignalHandler(logging.Handler):
                def emit(self, record):
                    msg = self.format(record)
                    self.thread.progress.emit(msg)

            handler = SignalHandler()
            handler.thread = self
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            
            # Process the files
            process_files(self.input_folder, handler, self.output_folder)
            self.finished.emit(True, "Processing completed successfully!")
        except Exception as e:
            self.finished.emit(False, str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Text Replacer")
        self.setMinimumSize(800, 600)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Input folder selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Input Folder:")
        self.input_path = QLabel("No folder selected")
        self.input_path.setStyleSheet("color: #666;")
        self.browse_input = QPushButton("Browse")
        self.browse_input.clicked.connect(self.select_input_folder)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path, 1)
        input_layout.addWidget(self.browse_input)
        layout.addLayout(input_layout)

        # Output folder selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output Folder:")
        self.output_path = QLabel("No folder selected")
        self.output_path.setStyleSheet("color: #666;")
        self.browse_output = QPushButton("Browse")
        self.browse_output.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path, 1)
        output_layout.addWidget(self.browse_output)
        layout.addLayout(output_layout)

        # Process button
        self.process_btn = QPushButton("Process Files")
        self.process_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
        """)
        self.process_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.process_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.log_output)

        # Status bar
        self.statusBar().showMessage("Ready")

        # Initialize variables
        self.input_folder = None
        self.output_folder = None
        self.worker = None

    def select_input_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_folder = folder
            self.input_path.setText(folder)
            self.check_ready()

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        print(folder)
        if folder:
            self.output_folder = folder
            self.output_path.setText(folder)
            self.check_ready()

    def check_ready(self):
        self.process_btn.setEnabled(bool(self.input_folder and self.output_folder))

    def start_processing(self):
        if not self.input_folder or not self.output_folder:
            QMessageBox.warning(self, "Error", "Please select both input and output folders!")
            return

        # Disable UI elements
        self.process_btn.setEnabled(False)
        self.browse_input.setEnabled(False)
        self.browse_output.setEnabled(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.log_output.clear()
        self.statusBar().showMessage("Processing...")

        # Start processing in a separate thread
        self.worker = WorkerThread(self.input_folder, self.output_folder)
        self.worker.progress.connect(self.update_log)
        self.worker.finished.connect(self.processing_finished)
        self.worker.start()

    def update_log(self, message):
        self.log_output.append(message)

    def processing_finished(self, success, message):
        # Re-enable UI elements
        self.process_btn.setEnabled(True)
        self.browse_input.setEnabled(True)
        self.browse_output.setEnabled(True)
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)

        if success:
            self.statusBar().showMessage("Processing completed successfully!")
            QMessageBox.information(self, "Success", message)
        else:
            self.statusBar().showMessage("Processing failed!")
            QMessageBox.critical(self, "Error", f"An error occurred: {message}")

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 