from elevation_query import calculate_cell_elevation
import pyproj
import numpy as np
import json
from sim import generate_and_save_data

# Definir la proyección de lat/lon (WGS84)
wgs84 = pyproj.CRS('EPSG:4326')  # WGS84 es el sistema de coordenadas geográficas (lat/lon)

# Definir la proyección UTM (Zona 18N para América del Sur)
utm_proj = pyproj.CRS('EPSG:32718')  # UTM zona 18 para América del Sur

# Crear transformadores (de UTM a lat/lon y viceversa)
transformer_to_latlon = pyproj.Transformer.from_crs(utm_proj, wgs84, always_xy=True)
transformer_to_utm = pyproj.Transformer.from_crs(wgs84, utm_proj, always_xy=True)

# Función para convertir lat/lon a UTM (en metros)
def latlon_to_utm(lat, lon):
    x, y = transformer_to_utm.transform(lon, lat)
    return x, y

# Función para convertir UTM a lat/lon
def utm_to_latlon(x, y):
    lon, lat = transformer_to_latlon.transform(x, y)
    return lat, lon

# Función para ajustar el polígono a celdas cuadradas de tamaño cell_size
def adjust_polygon_to_cells(polygon_meters, cell_size):
    # Obtener el rango de las coordenadas en X y Y
    min_x = min(coord[0] for coord in polygon_meters)
    max_x = max(coord[0] for coord in polygon_meters)
    min_y = min(coord[1] for coord in polygon_meters)
    max_y = max(coord[1] for coord in polygon_meters)

    # Calcular las distancias horizontales y verticales
    horizontal_distance = max_x - min_x
    vertical_distance = max_y - min_y

    # Calcular el ajuste necesario para que las distancias sean múltiplos de cell_size
    horizontal_adjustment = (np.ceil(horizontal_distance / cell_size) * cell_size) - horizontal_distance
    vertical_adjustment = (np.ceil(vertical_distance / cell_size) * cell_size) - vertical_distance

    # Distribuir el ajuste entre los puntos izquierdo/derecho (horizontal) y superior/inferior (vertical)
    adjustment_left = horizontal_adjustment / 2
    adjustment_right = horizontal_adjustment / 2
    adjustment_bottom = vertical_adjustment / 2
    adjustment_top = vertical_adjustment / 2

    # Ajustar las coordenadas del polígono para que encajen con las celdas
    adjusted_polygon_meters = [
        [min_x - adjustment_left, min_y - adjustment_bottom],
        [min_x - adjustment_left, max_y + adjustment_top],
        [max_x + adjustment_right, max_y + adjustment_top],
        [max_x + adjustment_right, min_y - adjustment_bottom]
    ]

    # Calcular el número de filas y columnas usando las dimensiones del polígono ajustado
    adjusted_horizontal_distance = adjusted_polygon_meters[2][0] - adjusted_polygon_meters[0][0]
    adjusted_vertical_distance = adjusted_polygon_meters[1][1] - adjusted_polygon_meters[0][1]

    num_columns = int(np.ceil(adjusted_horizontal_distance / cell_size))
    num_rows = int(np.ceil(adjusted_vertical_distance / cell_size))

    return adjusted_polygon_meters, num_rows, num_columns

# Función para generar la estructura de celdas usando solo el centro
def create_grid_structure(top_left_x, top_left_y, num_rows, num_columns, cell_size):
    cells = []
    cell_id = 1

    # Iteración para filas y columnas
    for i in range(num_columns):
        for j in range(num_rows):
            # Calcular las coordenadas del centro de la celda (en UTM)
            x_center = top_left_x + (i * cell_size) + (cell_size / 2)
            y_center = top_left_y - (j * cell_size) - (cell_size / 2)

            # Convertir el centro de la celda de UTM a lat/lon
            center_lat, center_lon = utm_to_latlon(x_center, y_center)

            # Obtener la elevación promedio de la celda usando calculate_cell_elevation
            elevation = calculate_cell_elevation(center_lat, center_lon, cell_size)

            # Guardar la celda con su id, coordenadas del centro, y la elevación promedio
            cell = {
                'id': cell_id,
                'center_coordinates': [center_lat, center_lon],
                'elevation': elevation  # Agregar la elevación promedio
            }
            cells.append(cell)
            cell_id += 1

    return cells


def process_polygon(cell_size):
    """
    Procesa el polígono definido en 'polygon_coordinates.json', ajustándolo a una cuadrícula
    con celdas del tamaño especificado, y genera la estructura de celdas.

    Args:
        cell_size (float): Tamaño de cada celda en metros.

    Returns:
        dict: Contiene:
            - 'cells': Lista de celdas con IDs y coordenadas del centro en lat/lon.
            - 'bottom_left_utm': Coordenadas del punto inferior izquierdo del polígono ajustado en UTM.
            - 'num_rows': Número de filas de celdas.
            - 'num_columns': Número de columnas de celdas.
    """
    # Leer el archivo polygon_coordinates.json
    with open('polygon_coordinates.json', 'r') as f:
        polygon_coords = json.load(f)

    # Convertir el polígono original a UTM (en metros)
    polygon_meters = [latlon_to_utm(lat, lon) for lat, lon in polygon_coords]

    # Ajustar el polígono para que encaje con las celdas
    adjusted_polygon_meters, num_rows, num_columns = adjust_polygon_to_cells(polygon_meters, cell_size)

    generate_and_save_data(adjusted_polygon_meters, 10,'fuel_data.json')

    # Imprimir los resultados ajustados
    print("Polígono ajustado en UTM:")
    for coord in adjusted_polygon_meters:
        print(coord)

    # Obtener la coordenada inferior izquierda (el punto con el valor mínimo de X y Y)
    bottom_left_utm = min(adjusted_polygon_meters, key=lambda x: (x[0], x[1]))  # Mínimo en X, luego en Y

    # Generar la estructura de celdas
    cells = create_grid_structure(
        adjusted_polygon_meters[0][0],  # Top-left X
        adjusted_polygon_meters[0][1],  # Top-left Y
        num_rows,
        num_columns,
        cell_size
    )

    # Retornar las celdas, la coordenada inferior izquierda en UTM, y el número de filas y columnas
    return {
        'cells': cells,
        'bottom_left_utm': bottom_left_utm,  # Coordenada inferior izquierda en UTM
        'num_rows': num_rows,  # Número de filas de celdas
        'num_columns': num_columns  # Número de columnas de celdas
    }


# Bloque principal para ejecutar el script
if __name__ == "__main__":
    # Tamaño de las celdas (en metros)
    cell_size = 100

    # Ejecutar la lógica completa
    result = process_polygon(cell_size)

    # Mostrar los resultados
    print("Polígono ajustado en UTM:")
    for coord in result['adjusted_polygon_meters']:
        print(coord)

    print("\nPolígono ajustado en lat/lon:")
    for coord in result['adjusted_polygon_latlon']:
        print(coord)

    print(f"\nNúmero de filas: {result['num_rows']}")
    print(f"Número de columnas: {result['num_columns']}")

    print("\nPrimeras 5 celdas generadas:")
    for cell in result['cells'][:5]:
        print(cell)
