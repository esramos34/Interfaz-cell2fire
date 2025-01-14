from PyQt5.QtCore import QUrl, QObject, pyqtSlot, QThread, pyqtSignal, Qt  # Asegúrate de importar Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QLabel, QFrame
import os
import json
from test_polygon import process_polygon
from processingWindow import ProcessingWindow  # Asegúrate de usar el nombre correcto del archivo


# Variable global para saber si el polígono está presente
polygon_present = False

# Clase para manejar los eventos desde JavaScript
class JSBridge(QObject):
    @pyqtSlot(str)
    def save_coordinates(self, coordinates_json):
        global polygon_present
        try:
            coordinates = json.loads(coordinates_json)
            with open("polygon_coordinates.json", "w") as f:
                json.dump(coordinates, f, indent=4)
            polygon_present = True
            if self.parent():
                self.parent().validate_input()
        except Exception as e:
            print(f"Error al guardar coordenadas: {e}")

    @pyqtSlot()
    def delete_coordinates(self):
        global polygon_present
        polygon_present = False
        if self.parent():
            self.parent().validate_input()


class ProcessThread(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, cell_size):
        super().__init__()
        self.cell_size = cell_size

    def run(self):
        # Llamar a la función process_polygon y capturar el resultado
        result = process_polygon(self.cell_size)
        self.finished.emit(result)


class DataWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mapa Interactivo - Interfaz Compacta")
        self.setGeometry(100, 100, 1200, 800)

        # Crear el widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Diseño principal
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  # Márgenes completamente eliminados
        self.main_layout.setSpacing(0)  # Sin espaciado entre elementos

        # Sección: Tamaño de la celda (etiqueta + campo)
        self.cell_size_layout = QHBoxLayout()
        self.cell_size_label = QLabel("Tamaño de la celda:", self)
        self.cell_size_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 0;")
        self.cell_size_input = QLineEdit(self)
        self.cell_size_input.setPlaceholderText("Ingresa el tamaño en metros")
        self.cell_size_layout.addWidget(self.cell_size_label)
        self.cell_size_layout.addWidget(self.cell_size_input)
        self.cell_size_layout.setContentsMargins(5, 5, 5, 0)  # Solo un pequeño margen superior
        self.cell_size_layout.setSpacing(5)
        self.main_layout.addLayout(self.cell_size_layout)

        # Sección: Botones en vertical
        self.button_layout = QVBoxLayout()
        self.validate_button = QPushButton("Validar", self)
        self.next_button = QPushButton("Siguiente", self)
        self.next_button.setEnabled(False)
        self.button_layout.addWidget(self.validate_button)
        self.button_layout.addWidget(self.next_button)
        self.button_layout.setContentsMargins(5, 0, 5, 0)  # Márgenes mínimos laterales, sin espacio inferior
        self.button_layout.setSpacing(0)  # Sin espacio entre botones
        self.main_layout.addLayout(self.button_layout)

        # Etiqueta para mostrar mensajes
        self.message_label = QLabel("Ingresa un tamaño de celda y dibuja un polígono.", self)
        self.message_label.setStyleSheet("color: #555; font-size: 14px; margin: 0; padding: 0;")
        self.main_layout.addWidget(self.message_label)

        # Separador visual
        self.separator = QFrame(self)
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setFrameShadow(QFrame.Sunken)
        self.separator.setStyleSheet("margin: 0; padding: 0;")  # Sin espacio
        self.main_layout.addWidget(self.separator)

        # Visor del mapa
        self.map_view = QWebEngineView()
        self.generate_html()
        self.map_view.setUrl(QUrl.fromLocalFile(os.path.abspath("map_with_draw.html")))
        self.map_view.setStyleSheet("margin: 0; padding: 0;")  # Sin márgenes ni espacios
        self.main_layout.addWidget(self.map_view)

        # Indicador de carga
        self.loading_label = QLabel("Cargando...", self)
        self.loading_label.setStyleSheet("font-size: 18px; color: #ff5722;")
        self.loading_label.setAlignment(Qt.AlignCenter)  # Centrar el texto
        self.loading_label.setVisible(False)  # Inicialmente oculto
        self.main_layout.addWidget(self.loading_label)

        # Configurar la comunicación entre Python y JavaScript
        self.bridge = JSBridge()
        self.web_channel = QWebChannel()
        self.web_channel.registerObject("bridge", self.bridge)
        self.map_view.page().setWebChannel(self.web_channel)

        # Conectar señales
        self.cell_size_input.textChanged.connect(self.validate_input)
        self.validate_button.clicked.connect(self.validate_input)
        self.next_button.clicked.connect(self.on_next_button_clicked)

    def generate_html(self):
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/leaflet.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.3/leaflet.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
            <style>
                html, body {width: 100%; height: 100%; margin: 0; padding: 0;}
                #map {position: absolute; top: 0; bottom: 0; right: 0; left: 0;}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    var map = L.map('map').setView([-0.1807, -78.4678], 12);

                    L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                        attribution: 'ESRI'
                    }).addTo(map);

                    var drawnItems = new L.FeatureGroup();
                    map.addLayer(drawnItems);

                    var drawControl = new L.Control.Draw({
                        edit: { featureGroup: drawnItems },
                        draw: {
                            polygon: true,
                            rectangle: true,
                            circle: false,
                            marker: false,
                            polyline: false
                        }
                    });
                    map.addControl(drawControl);

                    var bridge;
                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        bridge = channel.objects.bridge;
                    });

                    map.on(L.Draw.Event.CREATED, function(event) {
                        var layer = event.layer;
                        drawnItems.addLayer(layer);

                        var coordinates = layer.getLatLngs()[0].map(function(latlng) {
                            return [latlng.lat, latlng.lng];
                        });

                        if (bridge) {
                            bridge.save_coordinates(JSON.stringify(coordinates));
                        }
                    });

                    map.on(L.Draw.Event.DELETED, function(event) {
                        var layers = event.layers;
                        layers.eachLayer(function(layer) {
                            drawnItems.removeLayer(layer);
                        });

                        if (bridge) {
                            bridge.delete_coordinates();
                        }
                    });
                });
            </script>
        </body>
        </html>
        """
        with open("map_with_draw.html", "w") as f:
            f.write(html_content)

    def validate_input(self):
        global polygon_present
        cell_size_text = self.cell_size_input.text()

        try:
            cell_size = float(cell_size_text)
            if cell_size > 0 and polygon_present:
                self.next_button.setEnabled(True)
                self.message_label.setText("¡Validación exitosa! Puedes continuar.")
            else:
                self.next_button.setEnabled(False)
                self.message_label.setText("Debes ingresar un tamaño de celda positivo y dibujar un polígono.")
        except ValueError:
            self.next_button.setEnabled(False)
            self.message_label.setText("El tamaño de la celda debe ser un número válido.")

    def on_next_button_clicked(self):
        # Mostrar el indicador de carga
        self.loading_label.setVisible(True)
        self.setEnabled(False)  # Desactivar la ventana principal

        # Obtener el tamaño de celda desde el campo de texto
        cell_size = float(self.cell_size_input.text())
        print(f"Tamaño de celda seleccionado: {cell_size} metros")

        # Crear y ejecutar el hilo de procesamiento
        self.process_thread = ProcessThread(cell_size)
        self.process_thread.finished.connect(self.on_process_finished)
        self.process_thread.start()

    def on_process_finished(self, result):
        # Ocultar el indicador de carga
        self.loading_label.setVisible(False)
        self.setEnabled(True)  # Restaurar la interactividad de la ventana principal

        # Imprimir las celdas generadas
        print("\nPrimeras 5 celdas generadas:")
        for cell in result['cells'][:5]:
            print(f"Celda ID: {cell['id']}, Coordenadas: {cell['center_coordinates']}, Elevación: {cell['elevation']}")

        # Imprimir la coordenada inferior izquierda en UTM
        print(f"\nCoordenada inferior izquierda en UTM: {result['bottom_left_utm']}")

        # Imprimir el número de filas y columnas
        print(f"\nNúmero de filas: {result['num_rows']}")
        print(f"Número de columnas: {result['num_columns']}")

        # Buscar e imprimir las celdas con elevación -1
        print("\nCeldas con elevación -1:")
        for cell in result['cells']:
            if cell['elevation'] == -1:
                print(f"Celda ID: {cell['id']}, Coordenadas: {cell['center_coordinates']}, Elevación: {cell['elevation']}")

        # Obtener el tamaño de las celdas desde la entrada del usuario
        cell_size = float(self.cell_size_input.text())

        # Crear y mostrar la ventana de procesamiento
        self.processing_window = ProcessingWindow(
            result['cells'], result['num_rows'], result['num_columns'], result['bottom_left_utm'], cell_size
        )
        self.processing_window.show()  # Muestra la nueva ventana

        # Cierra la ventana actual (DataWindow) después de abrir la nueva
        self.close()




if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = DataWindow()
    window.show()
    sys.exit(app.exec_())
