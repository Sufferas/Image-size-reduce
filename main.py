import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QLabel, QSlider, QComboBox, QTextEdit
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from PIL import Image


class CompressImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Bildkomprimierer')

        # Create widgets
        self.button = QPushButton("Bilder auswählen")
        self.button.clicked.connect(self.select_files)

        # Create quality slider
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setMinimum(1)
        self.quality_slider.setMaximum(100)
        self.quality_slider.setValue(20)
        self.quality_slider.valueChanged.connect(self.update_quality_label)

        # Create labels for quality slider
        self.quality_label = QLabel()
        self.update_quality_label(self.quality_slider.value())
        self.min_quality_label = QLabel('1')
        self.max_quality_label = QLabel('100')

        # Create format combobox
        self.format_combobox = QComboBox()
        self.format_combobox.addItems(["JPEG", "PNG", "WEBP"])

        self.result_label = QLabel()

        self.drop_area = QTextEdit()
        self.drop_area.setReadOnly(True)
        self.drop_area.setText("Ziehen und ablegen Sie Dateien hier...")

        # Set layout
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(self.min_quality_label)
        quality_layout.addWidget(self.quality_slider)
        quality_layout.addWidget(self.max_quality_label)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addLayout(quality_layout)
        layout.addWidget(self.quality_label)
        layout.addWidget(self.format_combobox)
        layout.addWidget(self.drop_area)
        layout.addWidget(self.result_label)
        self.setLayout(layout)

        # Enable drag and drop
        self.setAcceptDrops(True)

    def update_quality_label(self, value):
        self.quality_label.setText(f'Qualität: {value}%')

    def compress_image(self, image_path, output_path, quality, format):
        # Bild öffnen
        img = Image.open(image_path)

        # Konvertieren in RGB falls es in RGBA oder CMYK Modus ist
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            img = img.convert('RGB')

        # Qualität reduzieren und in ein neues File speichern
        img.save(output_path, format=format, optimize=True, quality=quality)

    def select_files(self):
        file_paths, _ = QFileDialog.getOpenFileNames()
        if file_paths:
            self.process_files(file_paths)

    def process_files(self, file_paths):
        for file_path in file_paths:
            # Bestimme den absoluten Pfad für den Unterordner
            folder_path = os.path.join(os.path.dirname(os.path.abspath(file_path)), 'compressed')
            # Erstelle den Unterordner, wenn er nicht existiert
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            output_path = os.path.join(folder_path, os.path.split(file_path)[1].rsplit('.', 1)[0] + '_compressed.' + self.format_combobox.currentText().lower())
            self.compress_image(file_path, output_path, self.quality_slider.value(), self.format_combobox.currentText())
        self.result_label.setText(f"Die Bilder wurden komprimiert und im Ordner 'compressed' gespeichert.")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        file_paths = [url.toLocalFile() for url in event.mimeData().urls()]
        self.drop_area.setText("\n".join(file_paths))
        self.process_files(file_paths)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = CompressImageWidget()
    widget.show()

    sys.exit(app.exec_())
