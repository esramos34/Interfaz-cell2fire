import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QLineEdit, QLabel, QDateTimeEdit
)
from PyQt5.QtCore import QDateTime

class WeatherWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crear Weather.csv")
        self.resize(800, 400)

        # Crear la tabla
        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Instance", "datetime", "WS", "WD", "FireScenario"])
        self.table.setColumnWidth(1, 200)  # Ajustar ancho de la columna "datetime"

        # Entrada para carpeta de destino
        self.folder_label = QLabel("Carpeta de destino:", self)
        self.folder_input = QLineEdit(self)
        self.browse_button = QPushButton("Seleccionar Carpeta", self)
        self.browse_button.clicked.connect(self.select_folder)

        # Botones
        self.add_row_button = QPushButton("Agregar Fila", self)
        self.remove_row_button = QPushButton("Eliminar Fila", self)
        self.create_button = QPushButton("Crear Weather.csv", self)
        self.cancel_button = QPushButton("Cancelar", self)

        # Conexiones
        self.add_row_button.clicked.connect(self.add_row)
        self.remove_row_button.clicked.connect(self.remove_row)
        self.create_button.clicked.connect(self.create_weather)
        self.cancel_button.clicked.connect(self.cancel)

        # Diseño
        layout = QVBoxLayout()
        layout.addWidget(self.table)

        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(self.browse_button)

        layout.addLayout(folder_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_row_button)
        button_layout.addWidget(self.remove_row_button)
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_folder(self):
        """Abrir un cuadro de diálogo para seleccionar la carpeta de destino."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if folder:
            self.folder_input.setText(folder)

    def add_row(self):
        """Agregar una nueva fila a la tabla."""
        row_count = self.table.rowCount()
        self.table.insertRow(row_count)

        # Crear un QDateTimeEdit para la columna "datetime"
        datetime_editor = QDateTimeEdit(self)
        datetime_editor.setDisplayFormat("yyyy-MM-dd HH:00")
        datetime_editor.setDateTime(QDateTime.currentDateTime().addSecs(-QDateTime.currentDateTime().time().minute() * 60))
        self.table.setCellWidget(row_count, 1, datetime_editor)

    def remove_row(self):
        """Eliminar la fila seleccionada."""
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
        else:
            QMessageBox.warning(self, "Error", "Seleccione una fila para eliminar.")

    def create_weather(self):
        """Guardar los datos en un archivo Weather.csv en la carpeta seleccionada."""
        folder = self.folder_input.text()
        if not folder:
            QMessageBox.warning(self, "Error", "Seleccione una carpeta para guardar el archivo.")
            return

        file_name = f"{folder}/Weather.csv"

        try:
            with open(file_name, 'w') as file:
                # Escribir encabezados
                file.write("Instance,datetime,WS,WD,FireScenario\n")

                # Escribir filas
                for row in range(self.table.rowCount()):
                    row_data = []
                    for column in range(self.table.columnCount()):
                        if column == 1:  # Columna datetime con QDateTimeEdit
                            widget = self.table.cellWidget(row, column)
                            if widget and isinstance(widget, QDateTimeEdit):
                                row_data.append(widget.dateTime().toString("yyyy-MM-dd HH:00"))
                            else:
                                row_data.append("")
                        else:
                            item = self.table.item(row, column)
                            row_data.append(item.text() if item else "")
                    file.write(",".join(row_data) + "\n")

            QMessageBox.information(self, "Éxito", "Archivo guardado exitosamente.")
            self.accept()  # Cierra la ventana

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {e}")

    def cancel(self):
        """Cerrar la ventana sin guardar."""
        self.reject()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherWindow()
    if window.exec_() == QDialog.Accepted:
        print("Archivo Weather.csv creado exitosamente.")
    else:
        print("Operación cancelada por el usuario.")
    sys.exit(app.exec_())
