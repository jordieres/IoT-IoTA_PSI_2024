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


def pack_environmental_data(temp_stats, hum_stats, pres_stats, num_samples):
    """
    Packs all environmental statistics (temperature, humidity, pressure) into a single payload

    Args:
        temp_stats (tuple): Max, min, mean, and std deviation for temperature
        hum_stats (tuple): Max, min, mean, and std deviation for humidity
        pres_stats (tuple): Max, min, mean, and std deviation for pressure
        num_samples (int): Number of samples used in the statistics

    Returns:
        bytes: Packed payload containing all environmental data
    """
    payload_type = b'\x02'
    sample_count = num_samples.to_bytes(1, 'big')

    environmental_payload = (
            pack_humid(hum_stats[0]) +
            pack_humid(hum_stats[1]) +
            pack_humid(hum_stats[2]) +
            pack_humid(hum_stats[3]) +
            pack_pressure(pres_stats[0]) +
            pack_pressure(pres_stats[1]) +
            pack_pressure(pres_stats[2]) +
            pack_std(pres_stats[3]) +
            pack_temp(temp_stats[0]) +
            pack_temp(temp_stats[1]) +
            pack_temp(temp_stats[2]) +
            pack_temp(temp_stats[3])
    )

    return payload_type + sample_count + environmental_payload


def pack_timestamp(epoch_time):
    return pack("!I", epoch_time)


def pack_coordinate(value):
    return pack("!i", int(value * 10 ** 6))


def pack_gps_data(gps_positions):
    """
    Packs GPS data into a single payload

    Args:
        gps_positions (list): List of dictionaries, each containing:
            - 't': Timestamp (only the first one will be included)
            - 'X': Latitude
            - 'Y': Longitude

    Returns:
        tuple: Packed payload containing all GPS data
    """

    payload_type = b'\x01'

    if not gps_positions:
        return payload_type + b'\x00'  # No GPS positions available

    timestamp = pack_timestamp(gps_positions[0]['t'])

    gps_payload = b"".join([
        pack_coordinate(gps['X']) +
        pack_coordinate(gps['Y'])
        for gps in gps_positions
    ])
    gps_count = len(gps_positions).to_bytes(1, 'big')

    return payload_type + timestamp + gps_count + gps_payload


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
    """Converts latitude string (e.g., '40.446° N') to decimal degrees (e.g., 40.446)"""
    coord, hemi = latitude_str.replace("\xb0", "°").split("°")
    decimal_lat = float(coord.strip())
    if hemi.strip().upper() == 'S':
        decimal_lat = -decimal_lat
    return decimal_lat


def parse_longitude(longitude_str):
    """Converts longitude string (e.g., '3.462° W') to decimal degrees (e.g., -3.462)"""
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
        print("Not enough GPS points to filter outliers")
        return gps_data

    distances = [
        haversine(
            gps_data[i - 1]["X"], gps_data[i - 1]["Y"],
            gps_data[i]["X"], gps_data[i]["Y"]
        )
        for i in range(1, len(gps_data))
    ]

    threshold = calculate_percentile(distances, threshold_percentile)

    filtered_data = [gps_data[0]]
    for i in range(1, len(gps_data)):
        if distances[i - 1] <= threshold:
            filtered_data.append(gps_data[i])
    return filtered_data


def convert_to_epoch(timestamp, date, local_offset=0):
    """
    Convert GPS timestamp and date to epoch time.
    :param timestamp: List [hour, minute, second]
    :param date: String with format "January 4th, 2025"
    :param local_offset: Time zone difference to UTC in hours
    :return: Epoch time as an integer
    """

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

    tm = (year, month, day, hour, minute, second, 0, 0)

    try:
        epoch_time = mktime(tm)
        return epoch_time + 946681200 + local_offset * 3600
    except Exception as e:
        print(f"Error converting to epoch time: {e}")
        return None


def adjust_threshold_percentile(gps_data):
    """
    Dynamically adjusts the threshold percentile based on average speed

    Args:
        gps_data: List of dicts [{"t": timestamp, "X": lat, "Y": lon}, ...]

    Returns:
        New `threshold percentage` value to eliminate outliers
    """
    if len(gps_data) < 2:
        print("There is not enough GPS data to calculate speed")
        return 95

    speeds = []
    for i in range(1, len(gps_data)):
        dist = haversine(
            gps_data[i - 1]['X'], gps_data[i - 1]['Y'],
            gps_data[i]['X'], gps_data[i]['Y']
        )
        time_diff = gps_data[i]['t'] - gps_data[i - 1]['t']
        if time_diff > 0:
            speeds.append(dist / time_diff)

    avg_speed = mean(speeds)
    print(f"Average speed: {avg_speed}")

    if avg_speed < 1.4:
        return 85
    elif avg_speed < 27:
        return 95
    else:
        return 99
