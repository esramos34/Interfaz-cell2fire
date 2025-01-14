import random
import json

# Función para generar puntos aleatorios dentro de un polígono rectangular
def generate_random_points_in_polygon(polygon, num_points=10):
    """
    Genera puntos aleatorios dentro de un polígono rectangular.
    El polígono debe estar representado por las coordenadas de sus 4 vértices (esquinas).

    Args:
        polygon (list): Lista de 4 coordenadas que representan el polígono, por ejemplo:
                        [[xmin, ymin], [xmin, ymax], [xmax, ymax], [xmax, ymin]]
        num_points (int): Número de puntos aleatorios a generar.

    Returns:
        list: Lista de puntos aleatorios dentro del polígono.
    """
    xmin, ymin = polygon[0]
    xmax, ymax = polygon[2]

    points = []
    for _ in range(num_points):
        # Generar coordenadas aleatorias dentro del rango
        lat = random.uniform(ymin, ymax)
        lon = random.uniform(xmin, xmax)
        points.append([lat, lon])

    return points

# Función para asignar un modelo de combustible (número aleatorio entre 0 y 120)
def assign_fuel_model(points):
    """
    Asigna un modelo de combustible (número entre 0 y 120) a cada punto.

    Args:
        points (list): Lista de puntos generados aleatoriamente.

    Returns:
        list: Lista de puntos con su respectivo modelo de combustible asignado.
    """
    points_with_fuel = []
    for point in points:
        fuel_model = random.randint(0, 120)  # Generar un número aleatorio entre 0 y 120
        points_with_fuel.append({'coordinates': point, 'fuel_model': fuel_model})
    return points_with_fuel

# Generar datos y guardarlos en un archivo
def generate_and_save_data(polygon, num_points=10, output_file='fuel_data.json'):
    # Generar puntos aleatorios dentro del polígono
    random_points = generate_random_points_in_polygon(polygon, num_points)

    # Asignar modelos de combustible
    data = assign_fuel_model(random_points)

    # Guardar los datos en un archivo JSON
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Datos guardados en {output_file}")

# Ejemplo de uso
polygon = [
    [109656.87332936798, 9981878.893806815],  # Esquina inferior izquierda
    [109656.87332936798, 9982178.893806815],  # Esquina inferior derecha
    [109956.87332936798, 9982178.893806815],  # Esquina superior derecha
    [109956.87332936798, 9981878.893806815]   # Esquina superior izquierda
]

# Generar y guardar datos de ejemplo
generate_and_save_data(polygon, num_points=5)
