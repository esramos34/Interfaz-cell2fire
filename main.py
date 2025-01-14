# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Importar las otras ventanas
from main_window_ui import MainWindow
from data_window_ui import DataWindow
from weather_window import WeatherWindow
from ignition_generate import IgnitionsWindow

class HomeWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuración básica
        self.setWindowTitle("Cell2Fire - Selección de Ventanas")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f5f5f5;")

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)  # Centrar todo vertical y horizontalmente

        # Logo
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("descarga.jpeg").scaled(120, 120, Qt.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Título
        self.title_label = QLabel("Cell2Fire - Interfaz de Usuario")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 10px;")
        self.layout.addWidget(self.title_label)

        # Botón para abrir el simulador de incendios
        self.simulator_button = QPushButton("Simulador de Incendios")
        self.simulator_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.simulator_button.clicked.connect(self.open_simulator)
        self.layout.addWidget(self.simulator_button)

        # Botón para abrir el generador de datos
        self.generator_button = QPushButton("Generador de Datos")
        self.generator_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.generator_button.clicked.connect(self.open_generator)
        self.layout.addWidget(self.generator_button)

        # Botón para abrir la configuración del clima
        self.weather_button = QPushButton("Configuración Clima")
        self.weather_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.weather_button.clicked.connect(self.open_weather)
        self.layout.addWidget(self.weather_button)

        # Botón para abrir la ventana de definir puntos de ignición
        self.ignition_button = QPushButton("Definir Punto de Ignición")
        self.ignition_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.ignition_button.clicked.connect(self.open_ignition)
        self.layout.addWidget(self.ignition_button)

        # Aplicar el layout al widget central
        self.central_widget.setLayout(self.layout)

    def open_simulator(self):
        # Abrir la ventana del simulador de incendios
        self.simulator_window = MainWindow()
        self.simulator_window.show()

    def open_generator(self):
        # Abrir la ventana del generador de datos
        self.generator_window = DataWindow()
        self.generator_window.show()

    def open_weather(self):
        # Abrir la ventana de configuración del clima
        self.weather_window = WeatherWindow()
        self.weather_window.exec_()

    def open_ignition(self):
        # Abrir la ventana para definir puntos de ignición
        self.ignition_window = IgnitionsWindow()
        self.ignition_window.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    home_window = HomeWindow()
    home_window.show()
    sys.exit(app.exec_())
