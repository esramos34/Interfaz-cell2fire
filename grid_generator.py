import numpy as np
import folium

def generate_grid(mask_bounds, cell_size):
    """
    Genera un grid ajustado al tamaño de celda dado y devuelve una lista de celdas.

    Args:
        mask_bounds (dict): Límites de la máscara con las claves 'min_x', 'max_x', 'min_y', 'max_y'.
        cell_size (float): Tamaño de la celda en metros.

    Returns:
        list: Lista de celdas como rectángulos [((x1, y1), (x2, y2))].
    """
    # Conversión aproximada de metros a grados (varía ligeramente por latitud)
    METERS_TO_DEGREES = 1 / 111320  # Aproximadamente 1 grado = 111.32 km

    cell_size_degrees = cell_size * METERS_TO_DEGREES

    min_x, max_x = mask_bounds['min_x'], mask_bounds['max_x']
    min_y, max_y = mask_bounds['min_y'], mask_bounds['max_y']

    # Ajustar los límites para que encajen con el tamaño de las celdas
    adjusted_width = np.ceil((max_x - min_x) / cell_size_degrees) * cell_size_degrees
    adjusted_height = np.ceil((max_y - min_y) / cell_size_degrees) * cell_size_degrees

    # Calcular los nuevos límites ajustados
    adjusted_max_x = min_x + adjusted_width
    adjusted_max_y = min_y + adjusted_height

    # Calcular el número de celdas
    num_cols = int(adjusted_width / cell_size_degrees)
    num_rows = int(adjusted_height / cell_size_degrees)

    # Generar celdas como rectángulos
    cells = []
    for row in range(num_rows):
        for col in range(num_cols):
            x1 = min_x + col * cell_size_degrees
            y1 = min_y + row * cell_size_degrees
            x2 = x1 + cell_size_degrees
            y2 = y1 + cell_size_degrees
            cells.append(((x1, y1), (x2, y2)))

    return cells


def add_grid_to_map(cells, map_object):
    """
    Agrega un grid de celdas al objeto del mapa.

    Args:
        cells (list): Lista de celdas como rectángulos [((x1, y1), (x2, y2))].
        map_object (folium.Map): Objeto del mapa de folium.

    Returns:
        folium.Map: Mapa con el grid agregado.
    """
    for cell in cells:
        (x1, y1), (x2, y2) = cell
        folium.Rectangle(
            bounds=[[y1, x1], [y2, x2]],
            color="blue",
            weight=1,
            fill=True,
            fill_opacity=0.2
        ).add_to(map_object)

    return map_object
