import requests
import time

class ElevationAPI:
    """
    Clase para consultar elevaciones utilizando Open Elevation API.
    """

    @staticmethod
    def get_elevation_batch(locations, retries=1, delay=0.5, timeout=1):
        """
        Consulta las elevaciones de varios puntos usando Open Elevation API en una sola solicitud.

        Args:
            locations (list): Lista de tuplas de coordenadas (lat, lon).
            retries (int): Número de reintentos en caso de error.
            delay (int): Tiempo de espera entre los intentos.
            timeout (int): Tiempo de espera antes de que la solicitud se considere fallida.

        Returns:
            list: Lista de elevaciones correspondientes a cada coordenada.
        """
        locations_str = '|'.join([f"{lat},{lon}" for lat, lon in locations])
        url = f"https://api.open-elevation.com/api/v1/lookup?locations={locations_str}"

        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=timeout)  # Timeout de 10 segundos
                response.raise_for_status()  # Si la respuesta no es 200, lanza un error
                elevation_data = response.json()
                # Extraer elevaciones
                elevations = [result['elevation'] for result in elevation_data['results']]
                return elevations
            except requests.exceptions.Timeout:
                print(f"Intento {attempt+1} fallido: La solicitud de elevación ha excedido el tiempo de espera. Reintentando...")
                time.sleep(delay)
            except Exception as e:
                print(f"Intento {attempt+1} fallido: Error al consultar la elevación: {e}")
                time.sleep(delay)

        # Si fallaron todos los intentos, retornamos None para todos los puntos
        return [None] * len(locations)


def calculate_cell_elevation(lat, lon, cell_size_meters):
    """
    Calcula el promedio de elevación de una celda, considerando 5 puntos (4 esquinas y el centro).
    Si un punto no tiene elevación, se intentan hasta 3 veces. Si sigue fallando, se consulta solo la coordenada central.
    Si la elevación del centro es exitosa, se asigna a todos los puntos.

    Args:
        lat (float): Latitud del centro de la celda.
        lon (float): Longitud del centro de la celda.
        cell_size_meters (float): Tamaño de la celda en metros.

    Returns:
        float: Promedio de elevación en metros.
    """
    meters_to_degrees = 1 / 111320  # Aproximado: 1 grado ≈ 111.32 km en el ecuador
    half_cell_degrees = (cell_size_meters / 2) * meters_to_degrees

    # Generar los 5 puntos: las 4 esquinas y el centro
    locations = [
        (lat - half_cell_degrees, lon - half_cell_degrees),  # Esquina inferior izquierda
        (lat - half_cell_degrees, lon + half_cell_degrees),  # Esquina inferior derecha
        (lat + half_cell_degrees, lon - half_cell_degrees),  # Esquina superior izquierda
        (lat + half_cell_degrees, lon + half_cell_degrees),  # Esquina superior derecha
        (lat, lon)  # Punto central
    ]

    print("Puntos dentro de la celda (4 esquinas y el centro):")
    for i, (point_lat, point_lon) in enumerate(locations):
        print(f"  Punto {i+1}: ({point_lat:.6f}, {point_lon:.6f})")

    # Consultar las elevaciones para los puntos
    elevations = ElevationAPI.get_elevation_batch(locations)

    # Si alguna elevación no se obtiene, intentamos solo con el punto central
    if any(elev is None for elev in elevations):
        print("Elevación no encontrada para uno o más puntos. Consultando solo el punto central.")
        # Intentar obtener solo la elevación del centro
        elevations = ElevationAPI.get_elevation_batch([(lat, lon)])

        # Si la elevación del centro sigue siendo None después de reintentar, asignar -1
        if elevations[0] is None:
            print("No se pudo obtener la elevación del centro. Asignando -1 a todos los puntos.")
            elevations = [-1] * len(locations)
        else:
            # Si el centro es exitoso, asignamos esa elevación a todos los puntos
            center_elevation = elevations[0]
            elevations = [center_elevation] * len(locations)

    # Filtrar las elevaciones válidas (excepto -1) y calcular el promedio
    valid_elevations = [elev for elev in elevations if elev != -1]
    if valid_elevations:
        average_elevation = sum(valid_elevations) / len(valid_elevations)
        return average_elevation
    else:
        print("No se pudo obtener ninguna elevación válida.")
        return None


if __name__ == "__main__":
    # Coordenadas del centro de la celda
    center_lat = -0.19361274175710194
    center_lon = -78.56971672862728
    cell_size = 100  # Tamaño de la celda en metros

    # Calcular el promedio de elevación
    avg_elevation = calculate_cell_elevation(center_lat, center_lon, cell_size)

    if avg_elevation is not None:
        print(f"\nEl promedio de elevación de la celda es {avg_elevation:.2f} metros.")
    else:
        print("\nNo se pudo calcular el promedio de elevación.")
