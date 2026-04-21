"""
cities_data.py
--------------
Module containing a curated dataset of 35+ Indian cities
with their accurate geographical coordinates (latitude, longitude).

Project: AI-Based Route Optimization Using Hill Climbing Algorithm
Author : Final Year AI Project
"""

# Indian cities dictionary: {city_name: (latitude, longitude)}
INDIAN_CITIES = {
    "Mumbai":         (19.0760, 72.8777),
    "Delhi":          (28.7041, 77.1025),
    "Bengaluru":      (12.9716, 77.5946),
    "Hyderabad":      (17.3850, 78.4867),
    "Ahmedabad":      (23.0225, 72.5714),
    "Chennai":        (13.0827, 80.2707),
    "Kolkata":        (22.5726, 88.3639),
    "Pune":           (18.5204, 73.8567),
    "Jaipur":         (26.9124, 75.7873),
    "Surat":          (21.1702, 72.8311),
    "Lucknow":        (26.8467, 80.9462),
    "Kanpur":         (26.4499, 80.3319),
    "Nagpur":         (21.1458, 79.0882),
    "Indore":         (22.7196, 75.8577),
    "Thane":          (19.2183, 72.9781),
    "Bhopal":         (23.2599, 77.4126),
    "Visakhapatnam":  (17.6868, 83.2185),
    "Pimpri-Chinchwad":(18.6298, 73.7997),
    "Patna":          (25.5941, 85.1376),
    "Vadodara":       (22.3072, 73.1812),
    "Ghaziabad":      (28.6692, 77.4538),
    "Ludhiana":       (30.9010, 75.8573),
    "Agra":           (27.1767, 78.0081),
    "Nashik":         (20.0059, 73.7910),
    "Faridabad":      (28.4089, 77.3178),
    "Meerut":         (28.9845, 77.7064),
    "Rajkot":         (22.3039, 70.8022),
    "Varanasi":       (25.3176, 82.9739),
    "Srinagar":       (34.0837, 74.7973),
    "Aurangabad":     (19.8762, 75.3433),
    "Dhanbad":        (23.7957, 86.4304),
    "Amritsar":       (31.6340, 74.8723),
    "Allahabad":      (25.4358, 81.8463),
    "Ranchi":         (23.3441, 85.3096),
    "Coimbatore":     (11.0168, 76.9558),
    "Mysuru":         (12.2958, 76.6394),
    "Kochi":          (9.9312,  76.2673),
    "Bhubaneswar":    (20.2961, 85.8245),
    "Guwahati":       (26.1445, 91.7362),
    "Chandigarh":     (30.7333, 76.7794),
}

def get_city_list():
    """Return a sorted list of all available city names."""
    return sorted(INDIAN_CITIES.keys())

def get_coordinates(city_name: str):
    """Return (latitude, longitude) tuple for a given city name."""
    return INDIAN_CITIES.get(city_name, None)

def get_cities_subset(city_names: list):
    """Return a dict of coordinates for a requested subset of cities."""
    return {city: INDIAN_CITIES[city] for city in city_names if city in INDIAN_CITIES}
