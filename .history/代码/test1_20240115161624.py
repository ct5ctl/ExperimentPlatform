def geodetic_to_ecef(lat, lon, h):
    # WGS 84 ellipsiod constants
    a = 6378137  # semi-major axis in meters
    f = 1 / 298.257223563  # flattening
    b = a * (1 - f)  # semi-minor axis

    # Convert latitude and longitude to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)

    # Calculate the square of the first eccentricity
    e_sq = (a**2 - b**2) / a**2

    # Calculate the radius of curvature in the prime vertical
    N = a / math.sqrt(1 - e_sq * math.sin(lat_rad)**2)

    # Calculate ECEF coordinates
    X = (N + h) * math.cos(lat_rad) * math.cos(lon_rad)
    Y = (N + h) * math.cos(lat_rad) * math.sin(lon_rad)
    Z = (N * (1 - e_sq) + h) * math.sin(lat_rad)

    return X, Y, Z


X, Y, Z = geodetic_to_ecef(116.385532659999995530597516335546970367431640625, 39.904409979999996949118212796747684478759765625, 0)
pr