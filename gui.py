import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QProgressBar,
    QFileDialog, QWidget, QMessageBox, QSpinBox
)
from PyQt6.QtCore import QThread, pyqtSignal
from extensive_search import run_research, save_in_markdown, save_in_csv, save_in_excel, save_in_pdf, save_in_html


class ResearchWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    preview = pyqtSignal(str)

    def __init__(self, query, output_format, save_path, num_searches):
        super().__init__()
        self.query = query
        self.output_format = output_format
        self.save_path = save_path
        self.num_searches = num_searches

    def run(self):
        try:
            self.log.emit("Starting research...")
            self.progress.emit(10)

            # Perform the research
            results = run_research(self.query, max_searches=self.num_searches)
            self.progress.emit(50)
            self.log.emit("Research completed, preparing to save results...")

            # Emit results for preview
            self.preview.emit(results)

            # Create full file path
            file_path = os.path.join(self.save_path, f"results.{self.output_format}")

            # Save results in selected format
            if self.output_format == "markdown":
                save_in_markdown(results, file_path)
            elif self.output_format == "csv":
                save_in_csv([{"result": results}], file_path)
            elif self.output_format == "excel":
                save_in_excel([{"result": results}], file_path)
            elif self.output_format == "pdf":
                save_in_pdf(results, file_path)
            elif self.output_format == "html":
                save_in_html(results, file_path)

            self.progress.emit(100)
            self.finished.emit(file_path)

        except Exception as e:
            self.error.emit(str(e))


class DeepResearchGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DeepResearch Agent")
        self.setGeometry(200, 200, 700, 500)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layouts
        main_layout = QVBoxLayout()
        input_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        output_layout = QVBoxLayout()

        # Input: Search Query
        input_layout.addWidget(QLabel("Search Query:"))
        self.query_input = QLineEdit()
        input_layout.addWidget(self.query_input)

        # Input: Number of Individual Searches
        input_layout.addWidget(QLabel("Number of Individual Searches:"))
        self.num_searches_input = QSpinBox()
        self.num_searches_input.setRange(1, 10)  # Set the range as needed
        self.num_searches_input.setValue(5)  # Default value
        input_layout.addWidget(self.num_searches_input)

        # Output: Format Selector
        input_layout.addWidget(QLabel("Select Output Format:"))
        self.format_selector = QComboBox()
        self.format_selector.addItems(["markdown", "csv", "excel", "pdf", "html"])
        input_layout.addWidget(self.format_selector)

        # Output: Save Location
        input_layout.addWidget(QLabel("Save Location:"))
        self.save_location = QLineEdit()
        save_browse_button = QPushButton("Browse")
        save_browse_button.clicked.connect(self.browse_save_location)
        save_location_layout = QHBoxLayout()
        save_location_layout.addWidget(self.save_location)
        save_location_layout.addWidget(save_browse_button)
        input_layout.addLayout(save_location_layout)

        # Theme Selector
        input_layout.addWidget(QLabel("Select Theme:"))
        self.theme_selector = QComboBox()
        self.theme_selector.addItems(["Light", "Dark"])
        self.theme_selector.currentTextChanged.connect(self.change_theme)
        input_layout.addWidget(self.theme_selector)

        # Buttons: Start Search & Exit
        self.start_button = QPushButton("Start Search")
        self.start_button.clicked.connect(self.start_search)
        exit_button = QPushButton("Exit")
        exit_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(exit_button)

        # Output: Log/Console
        output_layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        output_layout.addWidget(self.log_output)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        output_layout.addWidget(self.progress_bar)

        # Add layouts to main layout
        main_layout.addLayout(input_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(output_layout)
        central_widget.setLayout(main_layout)

        # Initialize worker as None
        self.worker = None

    def browse_save_location(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Location")
        if directory:
            self.save_location.setText(directory)

    def start_search(self):
        query = self.query_input.text()
        output_format = self.format_selector.currentText()
        save_path = self.save_location.text()
        num_searches = self.num_searches_input.value()  # Get the number of individual searches

        if not query or not save_path:
            QMessageBox.critical(self, "Error", "Please provide a query and save location.")
            return

        # Disable the start button while processing
        self.start_button.setEnabled(False)
        self.progress_bar.setValue(0)

        # Create and setup the worker thread
        self.worker = ResearchWorker(query, output_format, save_path, num_searches)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_complete)
        self.worker.error.connect(self.on_error)
        self.worker.log.connect(self.log_message)
        self.worker.preview.connect(self.preview_results)

        # Start the worker thread
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def log_message(self, message):
        self.log_output.append(message)

    def preview_results(self, results):
        QMessageBox.information(self, "Result Preview", results)

    def on_complete(self, file_path):
        self.log_output.append(f"Search completed. Results saved at: {file_path}")
        self.start_button.setEnabled(True)

    def on_error(self, error_message):
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")
        self.log_output.append(f"Error: {error_message}")
        self.progress_bar.setValue(0)
        self.start_button.setEnabled(True)

    def change_theme(self, theme):
        if theme == "Dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #e0e0e0;
                }
                QLineEdit, QComboBox, QTextEdit {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #555;
                }
                QPushButton {
                    background-color: #333;
                    color: #ffffff;
                    border: 1px solid #555;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #444;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QProgressBar {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #555;
                    text-align: center;
                }
            """)
        else:  # Light Theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QLineEdit, QComboBox, QTextEdit {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #ccc;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #ccc;
                    padding: 5px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d6d6d6;
                }
                QLabel {
                    color: #000000;
                }
                QProgressBar {
                    background-color: #f5f5f5;
                    color: #000000;
                    border: 1px solid #ccc;
                    text-align: center;
                }
            """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DeepResearchGUI()
    gui.show()
    sys.exit(app.exec())
