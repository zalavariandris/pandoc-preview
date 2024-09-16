import sys
import os
import subprocess
from pathlib import Path, PureWindowsPath
from PySide6 import QtCore
from PySide6.QtCore import QFileSystemWatcher, Qt, Signal, Slot
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QFileDialog, QSplitter

from file_browser_widget import FileBrowser
from html_preview_widget import HTMLPreview

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

class WebPreview(QWidget):
    def __init__(self):
        super().__init__()

        # Create the text editor
        self.web_view = QWebEngineView()

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

    def set_html(self, html_body: str, base_url: QUrl):
        # Convert Markdown to HTML
        

        # Set the HTML content for preview with centered text and limited width
        html_head = """
            <style>
                body {
                    font-family: 'Courier New', monospace;
                    max-width: 600px;
                    margin: 50px auto;
                    text-align: left;
                }
                h1 {
                    text-align: center;
                }
            </style>"""

        html_site_content = f"""
            <html>
                <head>
                    {html_head}
                </head>
                <body>
                    {html_body}
                </body>
            </html>
        """

        # Set the HTML content for preview
        self.web_view.setHtml(html_site_content, base_url)

from typing import Optional

CONFIG_FILE_PATH = 'pandoc_preview.ini'

def read_file(file_path: Path) -> str:
    """Read the content of a file."""
    if file_path.exists():
        return file_path.read_text(encoding='utf-8')
    else:
        return f"<p>Failed to load file: {file_path}</p>"

def resolve_wikilinks(resource_path, filename):
    resource_path = Path(resource_path)
    filename = Path(filename)
    result = resource_path / filename
    # print(str(result))
    return result

def check_file_access(file_path):
    path = Path(file_path)
    if path.exists():
        print(f"File exists: {file_path}")
        if path.is_file():
            print(f"File is accessible: {file_path}")
        else:
            print(f"Path is not a file: {file_path}")
    else:
        print(f"File does not exist: {file_path}")

def replace_wikilink_images(text):
    import re
    # Regular expression pattern to match Wikilink-style images
    pattern = r'!\[\[([^\]]+)\]\]'

    def normalize_path(path):
        from os.path import normpath
        return PureWindowsPath(normpath(PureWindowsPath(path).as_posix())).as_posix()
    
    # Replacement function to convert Wikilink-style image to standard Markdown image
    def replace_match(match):
        # Extract the image path
        image_path = match.group(1)
        image_path = resolve_wikilinks("../Attachments", image_path)
        check_file_access(image_path.resolve())
        # Replace with standard Markdown image syntax
        return f'![]({normalize_path(image_path)})'
    
    # Use re.sub to replace all occurrences of the pattern
    result = re.sub(pattern, replace_match, text)
    return result


def markdown_to_html_pandoc(markdown_text: str) -> str:
    """Convert Markdown text to HTML using pandoc with citation processing."""
    try:

        markdown_text_with_images = replace_wikilink_images(markdown_text)
        # print(markdown_text_with_images)
        resource_path = "../Attachments"
        result = subprocess.run(
            ['pandoc', f"--resource-path={resource_path}", '--from=markdown', '--to=html', '--citeproc'],
            input=markdown_text_with_images.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"<p>Error converting Markdown to HTML: {e.stderr.decode('utf-8')}</p>"
    except Exception as e:
        return f"{e}, {e.args}. Pleasa install pandoc!"


class PandocPreviewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.file_path: Optional[Path] = None

        # self.setStyleSheet("QMainWindow {background: 'white';}");
        self.setup_ui()
        
        # Open the last opened file if available
        self.load_last_opened_file()

    def setup_ui(self):
        # Create the markdown preview widget
        self.html_preview_widget = WebPreview()
        self.html_preview_widget.layout().setContentsMargins(0,0,0,0)

        # Create the file browser widget
        self.file_browser_widget = FileBrowser()
        self.file_browser_widget.fileClicked.connect(self.update_file_path)  # Connect signal to slot
        self.file_browser_widget.layout().setContentsMargins(0,0,0,0)

        # Create a central widget and layout
        splitter = QSplitter()
        splitter.addWidget(self.file_browser_widget)
        splitter.addWidget(self.html_preview_widget)
        splitter.setStretchFactor(0,0)
        splitter.setStretchFactor(1,1)
        # splitter.setStretchFactor(1, 5)
        self.setCentralWidget(splitter)
        self.centralWidget().setContentsMargins(0,0,0,0)
        splitter.setHandleWidth(0)

        # Set up file watcher
        self.file_watcher = QFileSystemWatcher()

        self.file_watcher.fileChanged.connect(self.on_file_modified)

        # self.setup_menubar()

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Set window properties
        self.resize(800, 600)

    def on_file_modified(self):
        print("on file modified")
        if self.file_path:
            html_content = markdown_to_html_pandoc(self.file_path.read_text(encoding="utf-8"))
            baseUrl = QtCore.QUrl.fromLocalFile(str(self.file_path.parent) + '/')
            print(f"Base URL: {baseUrl}")
            self.html_preview_widget.set_html(html_content, baseUrl)
            html_file_path = Path("./html") / self.file_path.with_suffix(".html").name

            html_file_path.write_text(html_content, encoding="utf-8")
        
#         html_site = f"""<!DOCTYPE html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <meta http-equiv="X-UA-Compatible" content="ie=edge">
#     <title>HTML 5 Boilerplate</title>
#     <link rel="stylesheet" href="style.css">
#     <script type="text/javascript" src="https://livejs.com/live.js"></script>
#   </head>
#   <body>
#     {html_content}
#     <script src="index.js"></script>
#   </body>
# </html>
#         """
#         html_file_path.write_text(html_site, encoding="utf-8")

    def setup_menubar(self):
        # Set up the menu
        self.menu_bar = self.menuBar()

        file_menu = self.menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    @Slot()
    def open_file(self):
        """Open a Markdown file and update the preview."""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Markdown File", "", "Markdown Files (*.md);;All Files (*)", options=options)
        self.update_file_path(Path(file_name))

    def update_file_path(self, file_path:Path):
        file_path = Path(file_path)
        if file_path.exists() and file_path.suffix == '.md':
            self.file_path = file_path
            os.chdir(self.file_path.parent) # set working directory

            """Update the file browser root to the directory of the current file and select the file."""
            directory = self.file_path.parent
            self.file_browser_widget.set_root_directory(directory)
            self.file_browser_widget.select_file(self.file_path)

            """refresh views"""
            self.setWindowTitle(f"Pandoc Preview - {self.file_path.name}")
            self.file_watcher.addPath(str(self.file_path))

            self.on_file_modified()

            self.save_last_opened_file()
        else:
            self.setWindowTitle(f"Pandoc Preview")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events to check if the data can be accepted."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events to process dropped files."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                self.update_file_path(Path(file_path))

    @Slot()
    def save_last_opened_file(self):
        """Save the path of the last opened file."""
        if self.file_path:
            Path(CONFIG_FILE_PATH).write_text(str(self.file_path), encoding="utf-8")

    @Slot()
    def load_last_opened_file(self):
        """Load the path of the last opened file."""
        if Path(CONFIG_FILE_PATH).exists():
            last_opened_file =  Path(CONFIG_FILE_PATH).read_text(encoding="utf-8")
            self.update_file_path(Path(last_opened_file))


def main():
    import os
    os.environ['QT_QPA_PLATFORM'] = 'windows:darkmode=0' # Set the environment variable to disable dark mode
    
    # create QT app
    app = QApplication(sys.argv)

    # Create the main window
    window = PandocPreviewer()
    # window.setWindowFlags(window.windowFlags() | ~Qt.FramelessWindowHint)
    # window.setWindowFlags(window.windowFlags() | ~Qt.CustomizeWindowHint)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()