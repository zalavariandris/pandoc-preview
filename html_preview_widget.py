from PySide6.QtGui import QFont, QResizeEvent
from PySide6.QtWidgets import QTextEdit,  QWidget, QHBoxLayout, QSizePolicy, QScrollArea
from PySide6.QtCore import Qt, Signal, Slot, QSize

class HTMLPreview(QWidget):
	def __init__(self):
		super().__init__()

		# Create the text editor
		self.text_edit = TextEdit()
		self.text_edit.setAttribute(Qt.WA_MacShowFocusRect, 0)
		self.text_edit.setFocusPolicy(Qt.NoFocus)
		self.text_edit.setReadOnly(True)  # Make it a read-only preview
		# self.text_edit.setFixedWidth(600)

		# Set the font to monospace
		self.text_edit.setStyleSheet('''QTextEdit {
			border: none; 
			padding: 0;
			}''')

		self.text_edit.setFont(self.get_font())

		# Set layout
		# Create a layout for the TextEdit to center it horizontally
		text_edit_layout = QHBoxLayout()
		text_edit_layout.addStretch()  # Add stretchable space before the widget
		text_edit_layout.addWidget(self.text_edit)  # Add the TextEdit widget
		text_edit_layout.addStretch()  # Add stretchable space after the widget

		# Create a QWidget for the layout
		text_edit_container = QWidget()
		text_edit_container.setLayout(text_edit_layout)

		# Create a QScrollArea and set the TextEdit widget as its content
		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setWidget(text_edit_container)

		# Create a layout and add the QScrollArea to it
		self.setLayout(QHBoxLayout())
		self.layout().addWidget(self.scroll_area)

	def get_font(self):
		return QFont("iA Writer Mono S", 14)
		return QFont("Courier New", 14)  # You can adjust the size as needed

	def set_html(self, html_content: str):
		# Convert Markdown to HTML

		# Set the HTML content for preview
		styled_html = """
		<style>
		img{
			width: 100px
		}
		img + em { }
		</style>
		"""+html_content
		
		self.text_edit.setHtml(styled_html)

class TextEdit(QTextEdit):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

	def sizeHint(self) -> QSize:
		s = self.document().size().toSize()
		# Make sure width and height have 'usable' values
		s.setWidth(max(600, s.width()))
		s.setHeight(max(100, s.height()))
		return s

	def resizeEvent(self, event: QResizeEvent) -> None:
		# Call updateGeometry to make sure any layouts are notified of the change
		self.updateGeometry()
		super().resizeEvent(event)
