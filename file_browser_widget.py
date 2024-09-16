from pathlib import Path
from PySide6.QtCore import QDir, Signal, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QTreeView, QFileSystemModel


class FileBrowser(QWidget):
    fileClicked = Signal(Path)  # Define a custom signal that sends a Path object

    def __init__(self):
        super().__init__()
        
        # Create the file browser
        self.file_browser = QTreeView()
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.file_browser.setModel(self.file_system_model)
        self.file_browser.clicked.connect(self.on_file_clicked)
        
        # Hide all columns except the specified one
        self.file_browser.setHeaderHidden(True)
        for column in range(self.file_system_model.columnCount()):
            if column != 0:
                self.file_browser.hideColumn(column)
            else:
                self.file_browser.showColumn(column)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.file_browser)
        self.setLayout(layout)

        # Placeholder for selected file path
        self.file_path = None

    @Slot(int)
    def on_file_clicked(self, index):
        """Handle file selection from the file browser."""
        file_path = Path(self.file_system_model.filePath(index))
        if file_path.suffix == '.md':
            self.file_path = file_path
            self.fileClicked.emit(self.file_path)  # Emit the signal when a file is clicked

    def set_root_directory(self, directory):
        """Set the root directory of the file browser."""
        self.file_browser.setRootIndex(self.file_system_model.index(str(directory)))

    def select_file(self, file_path):
        """Select the file in the file browser."""
        index = self.file_system_model.index(str(file_path))
        self.file_browser.setCurrentIndex(index)
        self.file_browser.scrollTo(index)  # Optional: Scroll to the file
