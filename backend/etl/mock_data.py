"""
Mock data generator for development and testing.

Produces geographically realistic data for Ontario, focusing on areas
where data centers are actually being built or considered:
- GTA corridor (Toronto, Markham, Vaughan, Mississauga)
- Durham Region (Pickering, Ajax, Whitby)
- Cornwall / Eastern Ontario corridor
- Ottawa region
- Barrie / Simcoe County

All coordinates are in EPSG:4326 (WGS 84).
"""

import random
from typing import Any

# Seed for reproducible mock data.
random.seed(42)

# ---------------------------------------------------------------------------
# Known Ontario locations for realistic placement
# ---------------------------------------------------------------------------

# (name, lat, lon, voltage_kv, capacity_mva)
SUBSTATION_LOCATIONS: list[tuple[str, float, float, int, float]] = [
    # GTA / Southern Ontario 500kV
    ("Claireville TS", 43.740, -79.620, 500, 2000),
    ("Cherrywood TS", 43.835, -79.115, 500, 1800),
    ("Trafalgar TS", 43.435, -79.735, 500, 1500),
    ("Richview TS", 43.665, -79.535, 500, 1600),
    ("Parkway TS", 43.675, -79.340, 500, 1200),
    ("Manby TS", 43.625, -79.485, 500, 1400),
    # 230kV substations
    ("Buttonville MTS", 43.865, -79.375, 230, 800),
    ("Markham MTS", 43.870, -79.280, 230, 600),
    ("Vaughan MTS", 43.810, -79.520, 230, 700),
    ("Whitby TS", 43.880, -78.945, 230, 550),
    ("Ajax TS", 43.860, -79.040, 230, 500),
    ("Brampton MTS", 43.710, -79.750, 230, 650),
    ("Mississauga TS", 43.570, -79.650, 230, 600),
    ("Oshawa TS", 43.895, -78.860, 230, 500),
    ("Barrie TS", 44.380, -79.690, 230, 450),
    ("Ottawa South TS", 45.370, -75.690, 230, 700),
    ("Ottawa North TS", 45.430, -75.680, 230, 600),
    ("Cornwall TS", 45.020, -74.740, 230, 500),
    ("Kingston TS", 44.240, -76.490, 230, 400),
    ("Hamilton TS", 43.260, -79.870, 230, 550),
    # 115kV substations
    ("Agincourt TS", 43.795, -79.280, 115, 300),
    ("Leaside TS", 43.710, -79.360, 115, 350),
    ("Scarborough TS", 43.775, -79.195, 115, 280),
    ("Pickering TS", 43.840, -79.085, 115, 250),
    ("Newmarket TS", 44.050, -79.460, 115, 200),
    ("Milton TS", 43.510, -79.880, 115, 220),
    ("Guelph TS", 43.545, -80.260, 115, 200),
    ("Cambridge TS", 43.360, -80.315, 115, 180),
    ("Kitchener TS", 43.445, -80.490, 115, 250),
    ("London TS", 42.985, -81.250, 115, 300),
    ("St. Catharines TS", 43.160, -79.245, 115, 180),
    ("Peterborough TS", 44.300, -78.320, 115, 180),
    ("Belleville TS", 44.165, -77.385, 115, 160),
    ("North Bay TS", 46.310, -79.460, 115, 150),
    ("Sudbury TS", 46.490, -81.000, 115, 200),
    ("Sault Ste. Marie TS", 46.520, -84.340, 115, 170),
    ("Thunder Bay TS", 48.380, -89.250, 115, 200),
    ("Timmins TS", 48.475, -81.330, 115, 140),
    ("Windsor TS", 42.315, -83.035, 115, 250),
    ("Sarnia TS", 42.975, -82.400, 115, 160),
]

# Major transmission corridors (from, to).
TX_CORRIDORS: list[tuple[str, str, int]] = [
    ("Claireville TS", "Cherrywood TS", 500),
    ("Claireville TS", "Trafalgar TS", 500),
    ("Claireville TS", "Richview TS", 500),
    ("Richview TS", "Parkway TS", 230),
    ("Cherrywood TS", "Ajax TS", 230),
    ("Ajax TS", "Whitby TS", 230),
    ("Whitby TS", "Oshawa TS", 230),
    ("Claireville TS", "Brampton MTS", 230),
    ("Claireville TS", "Vaughan MTS", 230),
    ("Vaughan MTS", "Buttonville MTS", 230),
    ("Buttonville MTS", "Markham MTS", 230),
    ("Cherrywood TS", "Pickering TS", 115),
    ("Markham MTS", "Agincourt TS", 115),
    ("Ottawa South TS", "Ottawa North TS", 230),
    ("Cornwall TS", "Ottawa South TS", 230),
    ("Kingston TS", "Cornwall TS", 230),
    ("Belleville TS", "Kingston TS", 115),
    ("Oshawa TS", "Belleville TS", 115),
    ("Hamilton TS", "Trafalgar TS", 230),
    ("London TS", "Kitchener TS", 115),
    ("Kitchener TS", "Cambridge TS", 115),
    ("Guelph TS", "Kitchener TS", 115),
    ("Barrie TS", "Newmarket TS", 230),
]

# Fiber providers and their Ontario corridor anchors.
FIBER_PROVIDERS = ["Bell", "Rogers", "Cogeco", "Zayo", "Telus", "Beanfield"]

FIBER_CORRIDORS: list[tuple[str, list[tuple[float, float]]]] = [
    ("Bell", [(-79.38, 43.65), (-79.30, 43.80), (-79.25, 43.87), (-79.10, 43.84), (-78.86, 43.90)]),
    ("Bell", [(-79.38, 43.65), (-79.53, 43.67), (-79.63, 43.74), (-79.75, 43.71)]),
    ("Bell", [(-79.38, 43.65), (-75.69, 45.42)]),  # Toronto-Ottawa
    ("Rogers", [(-79.38, 43.65), (-79.28, 43.80), (-79.37, 43.87), (-79.46, 44.05)]),
    ("Rogers", [(-79.38, 43.65), (-79.65, 43.57), (-79.87, 43.26)]),
    ("Rogers", [(-79.38, 43.65), (-79.62, 43.74), (-79.69, 44.38)]),  # To Barrie
    ("Cogeco", [(-79.28, 43.87), (-79.04, 43.86), (-78.86, 43.90), (-78.32, 44.30)]),
    ("Zayo", [(-79.38, 43.65), (-79.20, 43.78), (-79.10, 43.84), (-74.74, 45.02)]),  # To Cornwall
    ("Zayo", [(-79.38, 43.65), (-80.26, 43.55), (-80.49, 43.45), (-81.25, 42.99)]),  # To London
    ("Beanfield", [(-79.38, 43.65), (-79.34, 43.68), (-79.28, 43.80), (-79.20, 43.85)]),
    ("Telus", [(-79.38, 43.65), (-79.53, 43.67), (-79.88, 43.51), (-80.49, 43.45)]),
]

# Municipalities and their approximate center + extent for parcel generation.
# (name, center_lat, center_lon, radius_deg)
PARCEL_ZONES: list[tuple[str, float, float, float]] = [
    ("Markham", 43.870, -79.290, 0.04),
    ("Vaughan", 43.820, -79.530, 0.04),
    ("Pickering", 43.840, -79.090, 0.03),
    ("Ajax", 43.860, -79.040, 0.02),
    ("Whitby", 43.880, -78.950, 0.03),
    ("Mississauga", 43.580, -79.650, 0.04),
    ("Brampton", 43.720, -79.760, 0.04),
    ("Milton", 43.520, -79.880, 0.03),
    ("Cornwall", 45.020, -74.740, 0.03),
    ("Ottawa", 45.400, -75.690, 0.05),
    ("Barrie", 44.380, -79.690, 0.03),
    ("Oshawa", 43.900, -78.860, 0.03),
    ("Hamilton", 43.260, -79.870, 0.04),
    ("Kitchener", 43.450, -80.490, 0.03),
    ("London", 42.985, -81.250, 0.04),
    ("Kingston", 44.240, -76.490, 0.03),
]

# Zoning types and their codes.
ZONE_TYPES = [
    ("M1", "Light Industrial", True),
    ("M2", "General Industrial", True),
    ("M3", "Heavy Industrial", True),
    ("EMP", "Employment Lands", True),
    ("C1", "Local Commercial", False),
    ("C4", "Mixed Use Commercial", False),
    ("AG", "Agricultural", False),
    ("RU", "Rural", False),
    ("R1", "Residential Low Density", False),
    ("OS", "Open Space", False),
]


# ---------------------------------------------------------------------------
# Generator functions
# ---------------------------------------------------------------------------

def _jitter(val: float, amount: float = 0.005) -> float:
    """Add small random jitter to a coordinate."""
    return val + random.uniform(-amount, amount)


def generate_substations() -> list[dict[str, Any]]:
    """Generate GeoJSON features for Ontario substations."""
    features = []
    for name, lat, lon, voltage, capacity in SUBSTATION_LOCATIONS:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [_jitter(lon, 0.002), _jitter(lat, 0.002)],
            },
            "properties": {
                "name": name,
                "voltage_kv": voltage,
                "capacity_mva": capacity + random.randint(-50, 50),
                "owner": random.choice(["Hydro One", "IESO", "Toronto Hydro"]) if voltage < 500 else "Hydro One",
                "source_id": f"mock_sub_{name.replace(' ', '_').lower()}",
            },
        })
    return features


def generate_transmission_lines() -> list[dict[str, Any]]:
    """Generate GeoJSON features for transmission line segments."""
    # Build a lookup of substation locations.
    sub_lookup = {name: (lon, lat) for name, lat, lon, *_ in SUBSTATION_LOCATIONS}

    features = []
    for from_name, to_name, voltage in TX_CORRIDORS:
        from_coords = sub_lookup.get(from_name)
        to_coords = sub_lookup.get(to_name)
        if not from_coords or not to_coords:
            continue

        # Create 3-5 intermediate points for a more realistic route.
        n_points = random.randint(3, 5)
        coords = [list(from_coords)]
        for i in range(1, n_points):
            t = i / n_points
            mid_lon = from_coords[0] + t * (to_coords[0] - from_coords[0])
            mid_lat = from_coords[1] + t * (to_coords[1] - from_coords[1])
            coords.append([_jitter(mid_lon, 0.01), _jitter(mid_lat, 0.01)])
        coords.append(list(to_coords))

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "name": f"{from_name} to {to_name}",
                "voltage_kv": voltage,
                "owner": "Hydro One",
                "source_id": f"mock_tx_{from_name}_{to_name}".replace(" ", "_").lower(),
            },
        })
    return features


def generate_fiber_routes() -> list[dict[str, Any]]:
    """Generate GeoJSON features for fiber backbone routes."""
    features = []
    for i, (provider, corridor) in enumerate(FIBER_CORRIDORS):
        # Add jitter to intermediate points.
        coords = []
        for lon, lat in corridor:
            coords.append([_jitter(lon, 0.005), _jitter(lat, 0.005)])

        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": coords},
            "properties": {
                "provider": provider,
                "route_type": random.choice(["backbone", "metro", "long_haul"]),
                "source_id": f"mock_fiber_{provider.lower()}_{i}",
            },
        })
    return features


def _random_parcel_polygon(
    center_lat: float, center_lon: float, size_acres: float
) -> list[list[float]]:
    """Generate a roughly rectangular parcel polygon."""
    # Convert acres to approximate degree extent.
    # 1 acre ≈ 4046.86 m², at ~44°N: 1° lat ≈ 111km, 1° lon ≈ 79km.
    area_m2 = size_acres * 4046.86
    side_m = area_m2 ** 0.5
    # Add some randomness to aspect ratio.
    aspect = random.uniform(0.5, 2.0)
    width_m = side_m * (aspect ** 0.5)
    height_m = side_m / (aspect ** 0.5)

    d_lon = width_m / 79000.0  # degrees longitude
    d_lat = height_m / 111000.0  # degrees latitude

    # Slight rotation via jitter.
    j = random.uniform(-0.0005, 0.0005)

    return [
        [center_lon - d_lon / 2 + j, center_lat - d_lat / 2],
        [center_lon + d_lon / 2, center_lat - d_lat / 2 + j],
        [center_lon + d_lon / 2 + j, center_lat + d_lat / 2],
        [center_lon - d_lon / 2, center_lat + d_lat / 2 + j],
        [center_lon - d_lon / 2 + j, center_lat - d_lat / 2],  # Close ring
    ]


def generate_parcels() -> list[dict[str, Any]]:
    """Generate ~200 realistic land parcels across Ontario municipalities."""
    features = []
    parcel_id = 0

    for municipality, center_lat, center_lon, radius in PARCEL_ZONES:
        # Generate 10-15 parcels per municipality.
        n = random.randint(10, 15)
        for _ in range(n):
            parcel_id += 1
            lat = center_lat + random.uniform(-radius, radius)
            lon = center_lon + random.uniform(-radius, radius)

            # Realistic size distribution (biased toward 10-100 acres).
            size_acres = random.choice([
                random.uniform(3, 10),    # Small
                random.uniform(10, 30),   # Medium
                random.uniform(30, 100),  # Large
                random.uniform(100, 300), # Very large
                random.uniform(5, 50),    # Mixed
            ])

            coords = _random_parcel_polygon(lat, lon, size_acres)
            area_sqm = size_acres * 4046.86

            use_options = [
                "Vacant Industrial", "Vacant Land", "Agricultural",
                "Commercial", "Light Industrial", "Warehouse",
                "Rural Residential", "Farm", "Mixed Use",
            ]

            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [coords]},
                "properties": {
                    "pin": f"0{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100, 999)}",
                    "municipality": municipality,
                    "area_sqm": round(area_sqm, 2),
                    "current_use": random.choice(use_options),
                    "source_id": f"mock_parcel_{parcel_id:04d}",
                },
            })

    return features


def generate_zoning() -> list[dict[str, Any]]:
    """Generate zoning polygons overlapping parcel areas."""
    features = []
    zone_id = 0

    for municipality, center_lat, center_lon, radius in PARCEL_ZONES:
        # Create 3-5 zoning zones per municipality.
        n_zones = random.randint(3, 5)
        for _ in range(n_zones):
            zone_id += 1
            zone_code, zone_desc, dc_compat = random.choice(ZONE_TYPES)

            # Larger polygons than parcels (zones cover multiple parcels).
            lat = center_lat + random.uniform(-radius * 0.5, radius * 0.5)
            lon = center_lon + random.uniform(-radius * 0.5, radius * 0.5)
            zone_radius = radius * random.uniform(0.3, 0.8)

            coords = [
                [lon - zone_radius, lat - zone_radius * 0.7],
                [lon + zone_radius, lat - zone_radius * 0.7],
                [lon + zone_radius * 1.1, lat + zone_radius * 0.5],
                [lon - zone_radius * 0.5, lat + zone_radius * 0.8],
                [lon - zone_radius, lat - zone_radius * 0.7],  # Close ring
            ]

            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [coords]},
                "properties": {
                    "zone_code": zone_code,
                    "zone_description": zone_desc,
                    "municipality": municipality,
                    "dc_compatible": dc_compat,
                    "source_id": f"mock_zone_{zone_id:04d}",
                },
            })

    return features


def generate_environmental_constraints() -> list[dict[str, Any]]:
    """Generate environmental constraint polygons (floodplains, wetlands)."""
    features = []

    # Floodplain areas along rivers and lakeshores.
    constraint_areas = [
        # Don River floodplain (Toronto)
        ("floodplain", "hard_block", [
            (-79.36, 43.68), (-79.35, 43.72), (-79.34, 43.76),
            (-79.33, 43.76), (-79.34, 43.72), (-79.35, 43.68), (-79.36, 43.68),
        ]),
        # Rouge River floodplain (Pickering/Markham)
        ("floodplain", "soft_block", [
            (-79.15, 43.80), (-79.14, 43.84), (-79.13, 43.87),
            (-79.12, 43.87), (-79.13, 43.84), (-79.14, 43.80), (-79.15, 43.80),
        ]),
        # Duffins Creek (Ajax/Pickering)
        ("floodplain", "soft_block", [
            (-79.06, 43.82), (-79.05, 43.86), (-79.04, 43.89),
            (-79.03, 43.89), (-79.04, 43.86), (-79.05, 43.82), (-79.06, 43.82),
        ]),
        # Humber River (Vaughan)
        ("floodplain", "hard_block", [
            (-79.54, 43.72), (-79.53, 43.76), (-79.52, 43.80),
            (-79.51, 43.80), (-79.52, 43.76), (-79.53, 43.72), (-79.54, 43.72),
        ]),
        # Wetland near Markham
        ("wetland", "soft_block", [
            (-79.32, 43.88), (-79.30, 43.89), (-79.29, 43.90),
            (-79.30, 43.91), (-79.32, 43.90), (-79.33, 43.89), (-79.32, 43.88),
        ]),
        # Wetland near Whitby
        ("wetland", "soft_block", [
            (-78.97, 43.90), (-78.95, 43.91), (-78.94, 43.92),
            (-78.95, 43.93), (-78.97, 43.92), (-78.98, 43.91), (-78.97, 43.90),
        ]),
        # Conservation area near Cornwall
        ("conservation_area", "review_required", [
            (-74.78, 45.00), (-74.75, 45.02), (-74.72, 45.03),
            (-74.73, 45.05), (-74.77, 45.04), (-74.79, 45.02), (-74.78, 45.00),
        ]),
        # Ottawa Greenbelt wetland
        ("wetland", "hard_block", [
            (-75.72, 45.36), (-75.70, 45.38), (-75.68, 45.39),
            (-75.69, 45.40), (-75.72, 45.39), (-75.73, 45.37), (-75.72, 45.36),
        ]),
    ]

    for i, (ctype, severity, coords) in enumerate(constraint_areas):
        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [coords]},
            "properties": {
                "constraint_type": ctype,
                "severity": severity,
                "source_id": f"mock_constraint_{i:04d}",
            },
        })

    return features
