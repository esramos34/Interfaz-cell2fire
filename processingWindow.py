import json
import math
import shutil
import os
from collections import Counter
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt

def assign_fuel_models_to_cells(cells, fuel_data, cell_size):
    """
    Asigna modelos de combustible a las celdas basado en la distancia entre el centro de la celda
    y las coordenadas proporcionadas en el archivo JSON de combustible.

    Args:
        cells (list): Lista de celdas con sus centros.
        fuel_data (list): Lista de coordenadas y modelos de combustible del JSON.
        cell_size (float): Tamaño de cada celda en metros.

    Returns:
        list: Lista de celdas actualizada con los modelos de combustible asignados.
    """
    max_dist = math.sqrt(2) * (cell_size / 2)  # Distancia máxima del centro a la esquina de la celda

    for cell in cells:
        center_x, center_y = cell['center_coordinates']
        nearby_models = []

        # Iterar sobre los datos del JSON de combustible
        for fuel_entry in fuel_data:
            if 'coordinates' in fuel_entry and 'fuel_model' in fuel_entry:
                fuel_x, fuel_y = fuel_entry['coordinates']
                fuel_model = fuel_entry['fuel_model']

                # Calcular la distancia entre el centro de la celda y el punto de combustible
                distance = math.sqrt((center_x - fuel_x)**2 + (center_y - fuel_y)**2)

                # Si está dentro del rango de la celda, agregar el modelo a la lista
                if distance <= max_dist:
                    nearby_models.append(fuel_model)

        # Determinar el modelo de combustible más frecuente
        if nearby_models:
            most_common_model = Counter(nearby_models).most_common(1)[0][0]  # Más frecuente
        else:
            most_common_model = fuel_data[0]['fuel_model']  # Primer modelo como predeterminado

        # Asignar el modelo a la celda
        cell['fuel_model'] = most_common_model

    return cells

class ProcessingWindow(QDialog):
    """
    Ventana de procesamiento que muestra los detalles de las celdas, filas, columnas, y la coordenada inferior izquierda.
    Además, genera un archivo .asc con la información de elevación y un archivo fuel.asc con los modelos de combustible.
    """
    def __init__(self, cells, num_rows, num_columns, bottom_left_utm, cell_size):
        super().__init__()

        self.setWindowTitle("Procesamiento")
        self.setGeometry(400, 200, 500, 350)  # Tamaño de la ventana

        # Datos pasados a la ventana
        self.cells = cells
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.bottom_left_utm = bottom_left_utm
        self.cell_size = cell_size  # Tamaño de celda

        # Diseño de la ventana
        layout = QVBoxLayout()

        # Etiqueta que indica los datos cargados
        layout.addWidget(QLabel(f"Coordenada inferior izquierda en UTM: {self.bottom_left_utm}"))
        layout.addWidget(QLabel(f"Número de filas: {self.num_rows}"))
        layout.addWidget(QLabel(f"Número de columnas: {self.num_columns}"))
        layout.addWidget(QLabel(f"Tamaño de celda: {self.cell_size} metros"))

        # Botón para seleccionar el archivo JSON de combustible
        self.select_json_button = QPushButton("Seleccionar archivo JSON de combustible", self)
        self.select_json_button.clicked.connect(self.select_fuel_json_path)
        layout.addWidget(self.select_json_button)

        # Campo para mostrar la ruta seleccionada del archivo JSON de combustible
        self.fuel_json_path_input = QLineEdit(self)
        self.fuel_json_path_input.setPlaceholderText("Ruta del archivo JSON de combustible")
        self.fuel_json_path_input.setReadOnly(True)
        layout.addWidget(self.fuel_json_path_input)

        # Botón para seleccionar la ruta para guardar el archivo .asc
        self.select_save_button = QPushButton("Seleccionar ruta para guardar el archivo .asc", self)
        self.select_save_button.clicked.connect(self.select_save_path)
        layout.addWidget(self.select_save_button)

        # Campo para mostrar la ruta de guardar el archivo .asc
        self.asc_file_path_input = QLineEdit(self)
        self.asc_file_path_input.setPlaceholderText("Ruta para guardar archivo .asc")
        self.asc_file_path_input.setReadOnly(True)
        layout.addWidget(self.asc_file_path_input)

        # Botón para generar los archivos
        self.generate_button = QPushButton("Generar archivos .asc y fuel.asc", self)
        self.generate_button.clicked.connect(self.generate_files)
        layout.addWidget(self.generate_button)

        # Configurar el diseño
        self.setLayout(layout)
        self.setModal(True)  # Para que no se pueda interactuar con otras ventanas hasta que se cierre

    def select_fuel_json_path(self):
        """
        Abre un cuadro de diálogo para seleccionar la ruta del archivo JSON de combustible.
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo JSON de combustible", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            self.fuel_json_path_input.setText(file_path)

    def select_save_path(self):
        """
        Abre un cuadro de diálogo para seleccionar la carpeta donde guardar el archivo .asc.
        """
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para guardar archivo .asc", options=options)
        if folder_path:
            self.asc_file_path_input.setText(folder_path + "/elevation.asc")  # Guardar con un nombre por defecto

    def generate_files(self):
        """
        Genera los archivos 'elevation.asc', 'fuel.asc', y copia 'spain_lookup_table.csv' con los parámetros proporcionados.
        """
        # Obtener las rutas de los archivos
        fuel_json_path = self.fuel_json_path_input.text()
        asc_file_path = self.asc_file_path_input.text()

        if not fuel_json_path or not asc_file_path:
            QMessageBox.warning(self, "Error", "Debe proporcionar ambas rutas de archivo: JSON de combustible y ruta para guardar el archivo .asc")
            return

        try:
            # Cargar los datos del archivo JSON de combustible
            with open(fuel_json_path, 'r') as f:
                fuel_data = json.load(f)  # Lista de puntos con coordenadas y modelos de combustible

            # Asignar modelos de combustible a las celdas
            self.cells = assign_fuel_models_to_cells(self.cells, fuel_data, self.cell_size)

            # Generar archivo .asc (elevación)
            with open(asc_file_path, 'w') as file:
                file.write(f"ncols         {self.num_columns}\n")
                file.write(f"nrows         {self.num_rows}\n")
                file.write(f"xllcorner     {self.bottom_left_utm[0]}\n")
                file.write(f"yllcorner     {self.bottom_left_utm[1]}\n")
                file.write(f"cellsize      {self.cell_size}\n")
                file.write(f"NODATA_value  -9999\n")

                for i in range(self.num_rows):
                    row = ""
                    for j in range(self.num_columns):
                        cell_index = i * self.num_columns + j
                        elevation = self.cells[cell_index]['elevation'] if cell_index < len(self.cells) else -9999
                        row += f"{elevation} "
                    file.write(row.strip() + "\n")

            print(f"Archivo .asc generado en: {asc_file_path}")

            # Generar archivo fuel.asc
            fuel_file_path = asc_file_path.replace('elevation.asc', 'fuel.asc')
            with open(fuel_file_path, 'w') as f:
                f.write(f"ncols         {self.num_columns}\n")
                f.write(f"nrows         {self.num_rows}\n")
                f.write(f"xllcorner     {self.bottom_left_utm[0]}\n")
                f.write(f"yllcorner     {self.bottom_left_utm[1]}\n")
                f.write(f"cellsize      {self.cell_size}\n")
                f.write(f"NODATA_value  -9999\n")

                for i in range(self.num_rows):
                    row = ""
                    for j in range(self.num_columns):
                        cell_index = i * self.num_columns + j
                        fuel_model = self.cells[cell_index]['fuel_model'] if cell_index < len(self.cells) else -1
                        row += f"{fuel_model} "
                    f.write(row.strip() + "\n")

            print(f"Archivo fuel.asc generado en: {fuel_file_path}")

            # Copiar archivo spain_lookup_table.csv
            lookup_table_src = os.path.join(os.path.dirname(__file__), "spain_lookup_table.csv")
            lookup_table_dest = os.path.join(os.path.dirname(asc_file_path), "spain_lookup_table.csv")

            shutil.copy(lookup_table_src, lookup_table_dest)
            print(f"Archivo spain_lookup_table.csv copiado a: {lookup_table_dest}")

            # Mostrar ventana de éxito
            QMessageBox.information(self, "Éxito", "¡Archivos generados correctamente!")
            self.accept()  # Cierra la ventana de procesamiento

        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"No se encontró el archivo {lookup_table_src}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al generar los archivos: {e}")

    def closeEvent(self, event):
        """
        Permite el cierre manual de la ventana de procesamiento.
        """
        reply = QMessageBox.question(
            self,
            "Cerrar ventana",
            "¿Está seguro de que desea cerrar esta ventana?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()  # Permite cerrar la ventana
        else:
            event.ignore()  # Cancela el cierre
