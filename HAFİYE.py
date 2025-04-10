from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QListWidget, QStackedLayout,
    QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from takip_edilenleri_cek import InstagramScraper
from takipcileri_cek import InstagramFollowerScraper
from kontrol import GeriTakipKontrol
import sys
import os


class WorkerThread(QThread):
    finished = pyqtSignal(str)

    def __init__(self, username, password, target):
        super().__init__()
        self.username = username
        self.password = password
        self.target = target

    def run(self):
        try:
            takipciler = InstagramScraper(self.username, self.password, self.target)
            takipciler.run()
            takip_edilenler = InstagramFollowerScraper(self.username, self.password, self.target)
            takip_edilenler.run()
            kontrol = GeriTakipKontrol()
            kontrol.calistir()
            self.finished.emit("success")
        except Exception as e:
            self.finished.emit(str(e))


class ModernApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hafiye UNF Programı")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.theme = "dark"
        self.setWindowIcon(QIcon("skull.ico"))  # Add the custom icon

        self.worker_thread = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        self.create_inputs()
        self.create_buttons()
        self.create_listbox()
        self.create_theme_switch()

        self.apply_theme()

    def create_inputs(self):
        self.input_layout = QHBoxLayout()
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Hedef Kullanıcı Adı")

        self.input_layout.addWidget(self.username_input)
        self.input_layout.addWidget(self.password_input)
        self.input_layout.addWidget(self.target_input)

        self.main_layout.addLayout(self.input_layout)

    def create_buttons(self):
        self.button_layout = QHBoxLayout()

        self.start_button = QPushButton("BAŞLAT")
        self.start_button.clicked.connect(self.start_process)

        self.show_followers_button = QPushButton("Takipçileri Göster")
        self.show_followers_button.clicked.connect(self.show_followers)

        self.show_following_button = QPushButton("Takip Edilenleri Göster")
        self.show_following_button.clicked.connect(self.show_following)

        self.show_non_followers_button = QPushButton("Geri Takip Etmeyenleri Göster")
        self.show_non_followers_button.clicked.connect(self.show_non_followers)

        self.button_layout.addWidget(self.start_button)
        self.button_layout.addWidget(self.show_followers_button)
        self.button_layout.addWidget(self.show_following_button)
        self.button_layout.addWidget(self.show_non_followers_button)

        self.main_layout.addLayout(self.button_layout)

    def create_listbox(self):
        self.list_widget = QListWidget()
        self.main_layout.addWidget(self.list_widget)

    def create_theme_switch(self):
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.main_layout.addWidget(self.theme_combo)

    def apply_theme(self):
        if self.theme == "dark":
            self.setStyleSheet("""
                QWidget {
                    background-color: #121212;
                    color: #ffffff;
                }
                QLineEdit, QPushButton, QListWidget, QComboBox {
                    background-color: #1e1e1e;
                    color: white;
                    border: 1px solid #333;
                    padding: 8px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #2e2e2e;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QLineEdit, QPushButton, QListWidget, QComboBox {
                    background-color: white;
                    color: black;
                    border: 1px solid #ccc;
                    padding: 8px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #ddd;
                }
            """)

    def change_theme(self, value):
        self.theme = value.lower()
        self.apply_theme()

    def start_process(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        target = self.target_input.text().strip()

        if not username or not password or not target:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurun.")
            return

        self.list_widget.clear()
        self.list_widget.addItem("İşlem başlatılıyor, lütfen bekleyin...")

        self.worker_thread = WorkerThread(username, password, target)
        self.worker_thread.finished.connect(self.on_process_finished)
        self.worker_thread.start()

    def on_process_finished(self, result):
        if result == "success":
            self.list_widget.clear()
            self.list_widget.addItem("İşlem tamamlandı.")
            self.show_non_followers()
        else:
            QMessageBox.critical(self, "Hata", f"Hata oluştu: {result}")

    def show_file_content(self, file_name):
        self.list_widget.clear()
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                for line in f:
                    self.list_widget.addItem(line.strip())
        except FileNotFoundError:
            self.list_widget.addItem(f"{file_name} bulunamadı.")

    def show_followers(self):
        self.show_file_content("takipciler.txt")

    def show_following(self):
        self.show_file_content("takip_edilenler.txt")

    def show_non_followers(self):
        self.show_file_content("geri_takip_edenler_degil.txt")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec())
