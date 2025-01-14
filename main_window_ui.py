import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QComboBox, QFormLayout, QCheckBox, QSpacerItem, QSizePolicy, QMessageBox, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana
        self.setWindowTitle("Cell2Fire UI")
        self.setGeometry(100, 100, 800, 700)  # (x, y, ancho, alto)
        self.setStyleSheet("background-color: #f5f5f5;")

        # Variables para almacenar rutas
        self.input_folder_path = None
        self.output_folder_path = None

        # Configuración del widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal
        self.layout = QVBoxLayout()

        # Encabezado con imagen y título
        self.header_layout = QHBoxLayout()

        # Imagen
        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("descarga.jpeg").scaled(100, 100, Qt.KeepAspectRatio))
        self.image_label.setAlignment(Qt.AlignCenter)
        self.header_layout.addWidget(self.image_label)

        # Título del programa
        self.title_label = QLabel("Cell2Fire - Interfaz de Usuario")
        self.title_label.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente
        self.title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        self.header_layout.addWidget(self.title_label)

        # Centrar la imagen y el título
        self.header_layout.setAlignment(Qt.AlignCenter)

        # Añadir encabezado al layout principal
        self.layout.addLayout(self.header_layout)

        # Espacio entre el encabezado y los botones de configuración
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Formulario para parámetros de simulación
        self.form_layout = QFormLayout()
        self.form_layout.setLabelAlignment(Qt.AlignRight)
        self.form_layout.setFormAlignment(Qt.AlignCenter)

        # Estilo del formulario
        form_style = "font-size: 14px; color: #555;"

        # Botón para seleccionar carpeta de entrada
        self.select_folder_button = QPushButton("Seleccionar carpeta de archivos de entrada")
        self.select_folder_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 8px;")
        self.select_folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_button, alignment=Qt.AlignCenter)

        # Etiqueta para mostrar la carpeta seleccionada
        self.folder_label = QLabel("Carpeta seleccionada: Ninguna")
        self.folder_label.setAlignment(Qt.AlignCenter)  # Centrar horizontalmente
        self.folder_label.setStyleSheet("color: #333; font-size: 12px;")
        self.layout.addWidget(self.folder_label, alignment=Qt.AlignCenter)

        # Botón para seleccionar carpeta de salida
        self.select_output_folder_button = QPushButton("Seleccionar carpeta de salida")
        self.select_output_folder_button.setStyleSheet("background-color: #4CAF50; color: white; border-radius: 5px; padding: 8px;")
        self.select_output_folder_button.clicked.connect(self.select_output_folder)
        self.layout.addWidget(self.select_output_folder_button, alignment=Qt.AlignCenter)

        # Etiqueta para mostrar la carpeta de salida seleccionada
        self.output_folder_label = QLabel("Carpeta de salida seleccionada: Ninguna")
        self.output_folder_label.setAlignment(Qt.AlignCenter)
        self.output_folder_label.setStyleSheet("color: #333; font-size: 12px;")
        self.layout.addWidget(self.output_folder_label, alignment=Qt.AlignCenter)

        # Parámetro: Duración de la simulación (años)
        self.sim_years_input = QLineEdit()
        self.sim_years_input.setPlaceholderText("Duración en años")
        self.sim_years_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Años de simulación:"), self.sim_years_input)

        # Parámetro: Período de propagación (horas)
        self.fire_period_input = QLineEdit()
        self.fire_period_input.setPlaceholderText("Período en horas")
        self.fire_period_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Período de propagación:"), self.fire_period_input)

        # Parámetro: Número de simulaciones
        self.num_simulations_input = QLineEdit()
        self.num_simulations_input.setPlaceholderText("Número de simulaciones")
        self.num_simulations_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Número de simulaciones:"), self.num_simulations_input)

        # Parámetro: Escenario climático
        self.weather_combo = QComboBox()
        self.weather_combo.addItems(["constant", "dynamic", "custom"])
        self.weather_combo.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Escenario climático:"), self.weather_combo)

        # Parámetro: Número de escenarios climáticos
        self.nweathers_input = QLineEdit()
        self.nweathers_input.setPlaceholderText("Número de escenarios climáticos")
        self.nweathers_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Número de escenarios climáticos:"), self.nweathers_input)

        # Parámetro: ROS-CV
        self.ros_cv_input = QLineEdit()
        self.ros_cv_input.setPlaceholderText("Valor de ROS-CV")
        self.ros_cv_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("ROS-CV:"), self.ros_cv_input)

        # Parámetro: Semilla aleatoria
        self.seed_input = QLineEdit()
        self.seed_input.setPlaceholderText("Semilla aleatoria")
        self.seed_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Semilla aleatoria:"), self.seed_input)

        # Parámetro: Radio de ignición
        self.ignition_rad_input = QLineEdit()
        self.ignition_rad_input.setPlaceholderText("Radio de ignición (km)")
        self.ignition_rad_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Radio de ignición:"), self.ignition_rad_input)

        # Parámetro: Opciones de grillas
        self.grids_all_radio = QRadioButton("All Grids")
        self.grids_final_radio = QRadioButton("Only Final Grid")
        self.grids_all_radio.setChecked(True)  # Valor por defecto
        grids_layout = QHBoxLayout()
        grids_layout.addWidget(self.grids_all_radio)
        grids_layout.addWidget(self.grids_final_radio)
        self.form_layout.addRow(QLabel("Opciones de Grillas:"), grids_layout)

        # Checkbox: Mensajes de salida
        self.output_messages_checkbox = QCheckBox("Incluir mensajes de salida (--output-messages)")
        self.output_messages_checkbox.setStyleSheet("color: #555;")
        self.form_layout.addRow(self.output_messages_checkbox)

        # Checkbox: Resultados del comportamiento del fuego
        self.fire_behavior_checkbox = QCheckBox("Incluir resultados del comportamiento del fuego")
        self.fire_behavior_checkbox.setStyleSheet("color: #555;")
        self.form_layout.addRow(self.fire_behavior_checkbox)

        # Checkbox: Fuego de copas
        self.crown_fire_checkbox = QCheckBox("Permitir fuego en copas")
        self.crown_fire_checkbox.setStyleSheet("color: #555;")
        self.form_layout.addRow(self.crown_fire_checkbox)

        # Parámetro: Opciones de ignición
        self.ignition_combo = QComboBox()
        self.ignition_combo.addItems(["random", "specific", "manual"])
        self.ignition_combo.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Opciones de Ignición:"), self.ignition_combo)

        # Parámetro: Hilos paralelos
        self.parallel_threads_input = QLineEdit()
        self.parallel_threads_input.setPlaceholderText("Número de hilos paralelos")
        self.parallel_threads_input.setStyleSheet("padding: 6px; border: 1px solid #ccc; border-radius: 5px;")
        self.form_layout.addRow(QLabel("Hilos paralelos:"), self.parallel_threads_input)

        # Parámetro: Procesamiento posterior
        self.postprocessing_none_radio = QRadioButton("Not PostProcessing")
        self.postprocessing_stats_radio = QRadioButton("Obtain Only Stats")
        self.postprocessing_plots_radio = QRadioButton("Obtain Plots and Stats")
        self.postprocessing_none_radio.setChecked(True)  # Valor por defecto
        postprocessing_layout = QHBoxLayout()
        postprocessing_layout.addWidget(self.postprocessing_none_radio)
        postprocessing_layout.addWidget(self.postprocessing_stats_radio)
        postprocessing_layout.addWidget(self.postprocessing_plots_radio)
        self.form_layout.addRow(QLabel("Procesamiento Posterior:"), postprocessing_layout)

        # Checkbox: Estadísticas
        self.stats_checkbox = QCheckBox("Generar estadísticas (--stats)")
        self.stats_checkbox.setStyleSheet("color: #555;")
        self.form_layout.addRow(self.stats_checkbox)

        # Checkbox: Todos los gráficos
        self.all_plots_checkbox = QCheckBox("Generar todos los gráficos (--allPlots)")
        self.all_plots_checkbox.setStyleSheet("color: #555;")
        self.form_layout.addRow(self.all_plots_checkbox)

        # Añadir formulario al layout principal
        self.layout.addLayout(self.form_layout)

        # Botón para iniciar simulación
        self.run_simulation_button = QPushButton("Iniciar Simulación")
        self.run_simulation_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px; font-weight: bold; border-radius: 5px; padding: 10px;")
        self.run_simulation_button.clicked.connect(self.run_simulation)
        self.layout.addWidget(self.run_simulation_button, alignment=Qt.AlignCenter)

        # Aplicar el layout
        self.central_widget.setLayout(self.layout)

    def select_folder(self):
        # Abrir un cuadro de diálogo para seleccionar carpeta de entrada
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Entrada")
        if folder:
            self.input_folder_path = folder  # Almacenar el path seleccionado
            self.folder_label.setText(f"Carpeta seleccionada: {folder}")

    def select_output_folder(self):
        # Abrir un cuadro de diálogo para seleccionar carpeta de salida
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Salida")
        if folder:
            self.output_folder_path = folder  # Almacenar el path seleccionado
            self.output_folder_label.setText(f"Carpeta de salida seleccionada: {folder}")

    def show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec_()

    def run_simulation(self):
        # Recuperar valores de los campos
        sim_years = self.sim_years_input.text()
        fire_period = self.fire_period_input.text()
        num_simulations = self.num_simulations_input.text()
        weather = self.weather_combo.currentText()
        nweathers = self.nweathers_input.text()
        ros_cv = self.ros_cv_input.text()
        seed = self.seed_input.text()
        ignition_rad = self.ignition_rad_input.text()
        parallel_threads = self.parallel_threads_input.text()

        # Validar los parámetros obligatorios
        if not self.input_folder_path:
            self.show_error_message("Debe seleccionar una carpeta de entrada.")
            return
        if not self.output_folder_path:
            self.show_error_message("Debe seleccionar una carpeta de salida.")
            return
        if not sim_years:
            self.show_error_message("Debe especificar la duración en años de la simulación.")
            return
        if not fire_period:
            self.show_error_message("Debe especificar el período de propagación en horas.")
            return
        if not num_simulations:
            self.show_error_message("Debe especificar el número de simulaciones.")
            return

        # Construir comando
        command = ["Cell2Fire","--sim","S"]
        command += ["--input-instance-folder", self.input_folder_path]
        command += ["--output-folder", self.output_folder_path]
        if sim_years:
            command += ["--sim-years", sim_years]
        if fire_period:
            command += ["--Fire-Period-Length", fire_period]
        if num_simulations:
            command += ["--nsims", num_simulations]
        if weather:
            command += ["--weather", weather]
        if nweathers:
            command += ["--nweathers", nweathers]
        if ros_cv:
            command += ["--ROS-CV", ros_cv]
        if seed:
            command += ["--seed", seed]
        if ignition_rad:
            command += ["--IgnitionRad", ignition_rad]
        if self.grids_final_radio.isChecked():
            command += ["--finalGrid"]
        if self.output_messages_checkbox.isChecked():
            command += ["--output-messages"]
        if self.fire_behavior_checkbox.isChecked():
            command += ["--FireBehavior"]
        if self.crown_fire_checkbox.isChecked():
            command += ["--AllowCrownFire"]
        if parallel_threads:
            command += ["--threads", parallel_threads]

        # Imprimir el comando
        print("Iniciando simulación con el siguiente comando:")
        print(" ".join(command))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
