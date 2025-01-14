import csv
import math
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QSpinBox
)
from PyQt5.QtCore import Qt


class IgnitionsWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crear Ignitions.csv")
        self.resize(600, 400)

        # Variables iniciales
        self.num_columns = None
        self.num_rows = None
        self.cell_size = None
        self.bottom_left_utm = None

        # Diseño principal
        layout = QVBoxLayout()

        # Botón para seleccionar el archivo fuel.asc
        self.fuel_label = QLabel("Archivo fuel.asc:", self)
        self.fuel_input = QLineEdit(self)
        self.browse_fuel_button = QPushButton("Seleccionar fuel.asc", self)
        self.browse_fuel_button.clicked.connect(self.load_fuel_file)

        fuel_layout = QHBoxLayout()
        fuel_layout.addWidget(self.fuel_label)
        fuel_layout.addWidget(self.fuel_input)
        fuel_layout.addWidget(self.browse_fuel_button)

        layout.addLayout(fuel_layout)

        # Tabla para ingresar los datos
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Año", "UTM X", "UTM Y"])
        layout.addWidget(self.table)

        # Botones para agregar/eliminar filas
        button_layout = QHBoxLayout()

        self.add_row_button = QPushButton("Agregar Fila")
        self.add_row_button.clicked.connect(self.add_row)
        button_layout.addWidget(self.add_row_button)

        self.remove_row_button = QPushButton("Eliminar Fila")
        self.remove_row_button.clicked.connect(self.remove_row)
        button_layout.addWidget(self.remove_row_button)

        layout.addLayout(button_layout)

        # Botón para seleccionar la carpeta de destino
        self.folder_label = QLabel("Carpeta de destino:")
        self.folder_input = QLineEdit(self)
        self.browse_button = QPushButton("Seleccionar Carpeta")
        self.browse_button.clicked.connect(self.select_folder)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_button)

        layout.addLayout(folder_layout)

        # Botón para crear el archivo CSV
        self.create_button = QPushButton("Crear Ignitions.csv")
        self.create_button.clicked.connect(self.create_csv)
        layout.addWidget(self.create_button)

        self.setLayout(layout)

    def load_fuel_file(self):
        """Carga el archivo fuel.asc y extrae los parámetros necesarios."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar fuel.asc", "", "ASC Files (*.asc);;All Files (*)")
        if file_path:
            self.fuel_input.setText(file_path)
            try:
                with open(file_path, 'r') as file:
                    for line in file:
                        if line.startswith("ncols"):
                            self.num_columns = int(line.split()[1])
                        elif line.startswith("nrows"):
                            self.num_rows = int(line.split()[1])
                        elif line.startswith("cellsize"):
                            self.cell_size = float(line.split()[1])
                        elif line.startswith("xllcorner"):
                            xllcorner = float(line.split()[1])
                        elif line.startswith("yllcorner"):
                            yllcorner = float(line.split()[1])
                        if self.num_columns and self.num_rows and self.cell_size and 'xllcorner' in locals() and 'yllcorner' in locals():
                            break

                self.bottom_left_utm = (xllcorner, yllcorner)
                QMessageBox.information(self, "Éxito", "Archivo fuel.asc cargado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo fuel.asc: {e}")

    def add_row(self):
        """Agregar una fila a la tabla."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

        # Columna "Año" como campo numérico
        spin_box = QSpinBox()
        spin_box.setMinimum(1)
        spin_box.setMaximum(9999)
        self.table.setCellWidget(row_count, 0, spin_box)

    def remove_row(self):
        """Eliminar la fila seleccionada."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "Error", "Seleccione una fila para eliminar.")

    def select_folder(self):
        """Seleccionar la carpeta donde guardar el archivo CSV."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if folder:
            self.folder_input.setText(folder)

    def calculate_cell(self, utm_x, utm_y):
        """
        Calcula el número de celda basado en las coordenadas y los parámetros de la cuadrícula.
        """
        if not self.num_columns or not self.cell_size or not self.bottom_left_utm:
            raise ValueError("No se han cargado los parámetros del archivo fuel.asc.")

        x_offset = utm_x - self.bottom_left_utm[0]
        y_offset = utm_y - self.bottom_left_utm[1]

        # Calcular columna y fila
        col = math.floor(x_offset / self.cell_size)
        row = math.floor(y_offset / self.cell_size)

        # Validar que las coordenadas están dentro del rango
        if col < 0 or col >= self.num_columns or row < 0 or row >= self.num_rows:
            raise ValueError("Las coordenadas están fuera del rango de la cuadrícula.")

        # Calcular el número de celda
        ncell = row * self.num_columns + col + 1
        return ncell

    def create_csv(self):
        """Crear el archivo Ignitions.csv."""
        folder = self.folder_input.text()
        if not folder:
            QMessageBox.warning(self, "Error", "Seleccione una carpeta para guardar el archivo.")
            return

        if not self.num_columns or not self.cell_size or not self.bottom_left_utm:
            QMessageBox.warning(self, "Error", "Cargue un archivo fuel.asc válido antes de continuar.")
            return

        file_path = f"{folder}/Ignitions.csv"

        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                # Escribir encabezados manualmente
                file.write("Year,Ncell\n")  # Encabezados en el formato correcto

                for row in range(self.table.rowCount()):
                    year_widget = self.table.cellWidget(row, 0)
                    year = year_widget.value() if year_widget else None

                    x_item = self.table.item(row, 1)
                    y_item = self.table.item(row, 2)

                    utm_x = float(x_item.text()) if x_item else None
                    utm_y = float(y_item.text()) if y_item else None

                    if year is not None and utm_x is not None and utm_y is not None:
                        try:
                            ncell = self.calculate_cell(utm_x, utm_y)
                            # Escribir los datos manualmente en formato CSV
                            file.write(f"{year},{ncell}\n")
                        except ValueError as ve:
                            QMessageBox.warning(self, "Error", str(ve))
                            return

            QMessageBox.information(self, "Éxito", "¡Archivo Ignitions.csv creado exitosamente!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo crear el archivo: {e}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = IgnitionsWindow()
    window.exec_()
