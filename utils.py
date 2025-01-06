"""
File Name: utils.py
Author: Irene Pereda Serrano
Created On: 29/12/2024
Description: Utility functions for packing sensor data and performing statistical analysis
"""

from ustruct import pack
import math
from utime import mktime


def pack_temp(temp):
    temp_conv = round(temp / 0.005)
    return pack("!h", temp_conv)


def pack_humid(hum):
    hum_conv = round(hum / 0.0025)
    return pack("!H", hum_conv)


def pack_pressure(pressure):
    pres_conv = round(pressure * 0.5)
    return pack("!H", pres_conv)


def pack_std(std):
    std_conv = round(std / 0.005)
    return pack("!H", std_conv)


def pack_timestamp(epoch_time):
    return pack("!I", epoch_time)


def pack_coordinate(value):
    return pack("!i", int(value * 10 ** 6))


def pack_gps_data(gps_data):
    return (
            pack_timestamp(gps_data["t"]) +
            pack_coordinate(gps_data["X"]) +
            pack_coordinate(gps_data["Y"])
    )


def mean(data):
    return sum(data) / len(data) if data else 0


def stdev(data):
    if len(data) <= 1:
        return 0
    avg = mean(data)
    variance = sum((x - avg) ** 2 for x in data) / len(data)
    return variance ** 0.5


def calculate_statistics(data):
    """Calculate max, min, mean, and standard deviation for a list of data."""
    if not data:
        return 0, 0, 0, 0
    return max(data), min(data), mean(data), stdev(data)


def parse_latitude(latitude_str):
    """Converts latitude string (e.g., '40.446° N') to decimal degrees (e.g., 40.446)."""
    coord, hemi = latitude_str.replace("\xb0", "°").split("°")
    decimal_lat = float(coord.strip())
    if hemi.strip().upper() == 'S':
        decimal_lat = -decimal_lat
    return decimal_lat


def parse_longitude(longitude_str):
    """Converts longitude string (e.g., '3.462° W') to decimal degrees (e.g., -3.462)."""
    coord, hemi = longitude_str.replace("\xb0", "°").split("°")
    decimal_lon = float(coord.strip())
    if hemi.strip().upper() == 'W':
        decimal_lon = -decimal_lon
    return decimal_lon


def haversine(lat1, lon1, lat2, lon2):
    """Calculates the distance between two GPS points (lat, lon) in meters"""
    R = 6371000  # Radius of Earth in meters
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def calculate_percentile(data, percentile):
    """Calculates the percentile value for a sorted list"""
    if not data:
        return None
    sorted_data = sorted(data)
    k = (len(sorted_data) - 1) * (percentile / 100)
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] + (sorted_data[c] - sorted_data[f]) * (k - f)


def filter_outliers_by_distance(gps_data, threshold_percentile=95):
    """
    Filters out GPS points that are outliers based on distance.

    Args:
        gps_data: List of dicts [{"t": timestamp, "X": lat, "Y": lon}, ...]
        threshold_percentile: Percentile above which a distance is considered an outlier

    Returns:
        Filtered list of GPS coordinates without outliers.
    """
    if len(gps_data) < 2:
        return gps_data

    # Calculate distances between consecutive points
    distances = [
        haversine(
            gps_data[i - 1]["X"], gps_data[i - 1]["Y"],
            gps_data[i]["X"], gps_data[i]["Y"]
        )
        for i in range(1, len(gps_data))
    ]

    # Determine the distance threshold for outliers
    threshold = calculate_percentile(distances, threshold_percentile)

    # Filter out points based on distance threshold
    filtered_data = [gps_data[0]]  # Always keep the first point
    for i in range(1, len(gps_data)):
        if distances[i - 1] <= threshold:
            filtered_data.append(gps_data[i])
    return filtered_data


def convert_to_epoch(timestamp, date):
    """
    Convert GPS timestamp and date to epoch time.
    :param timestamp: List [hour, minute, second]
    :param date: String with format "January 4th, 2025"
    :return: Epoch time as an integer
    """
    # Parse the date string
    months = {
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5,
        "June": 6, "July": 7, "August": 8, "September": 9, "October": 10,
        "November": 11, "December": 12
    }
    parts = date.split()
    month = months[parts[0]]
    day = int("".join(filter(str.isdigit, parts[1])))
    year = int(parts[2])

    timestamp = [int(float(x)) for x in timestamp]
    hour, minute, second = map(int, timestamp)

    # Create the tuple for mktime
    tm = (year, month, day, hour, minute, second, 0, 0)

    # Convert to epoch time
    try:
        epoch_time = mktime(tm)
        return epoch_time + 946681200
    except Exception as e:
        print(f"Error converting to epoch time: {e}")
        return None


def adjust_threshold_percentile(gps_data):
    """
    Ajusta dinámicamente el percentil del threshold en función de la velocidad promedio.

    Args:
        gps_data: Lista de dicts [{"t": timestamp, "X": lat, "Y": lon}, ...]

    Returns:
        Nuevo valor de `threshold_percentile` (porcentaje) para eliminar outliers.
    """
    if len(gps_data) < 2:
        return 95

    speeds = []
    for i in range(1, len(gps_data)):
        dist = haversine(
            gps_data[i - 1]['X'], gps_data[i - 1]['Y'],
            gps_data[i]['X'], gps_data[i]['Y']
        )
        time_diff = gps_data[i]['t'] - gps_data[i - 1]['t']
        if time_diff > 0:
            speeds.append(dist / time_diff)  # Velocidad en m/s

    avg_speed = mean(speeds)
    print(f"Average speed: {avg_speed}")

    # Ajustar el percentil según la velocidad promedio
    if avg_speed < 1.4:  # Velocidad de caminata (~5 km/h)
        return 85  # Umbral más estricto
    elif avg_speed < 27:  # Velocidad de coche (~100 km/h)
        return 95  # Umbral estándar
    else:  # Velocidad alta (vehículos rápidos)
        return 99  # Umbral más relajado
