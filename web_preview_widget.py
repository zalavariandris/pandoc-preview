from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView

class WebPreview(QWidget):
    def __init__(self):
        super().__init__()

        # Create the text editor
        self.web_view = QWebEngineView()
        self.web_view.setAttribute( Qt.WA_OpaquePaintEvent, True );
        self.web_view.setAttribute( Qt.WA_PaintOnScreen, True );
        self.web_view.setAttribute( Qt.WA_DontCreateNativeAncestors, True );
        self.web_view.setAttribute( Qt.WA_NativeWindow, True );
        self.web_view.setAttribute( Qt.WA_NoSystemBackground, True );
        self.web_view.setAttribute( Qt.WA_NativeWindow, True );
        self.web_view.setAutoFillBackground( False );

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