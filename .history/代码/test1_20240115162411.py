import math


def geodetic_to_ecef(lat, lon, h):
    lat = lat * math.pi / 180
    lon = lon * math.pi / 180
    Alpha_E = 0.335281066475e-2
    a_E = 6378137.0
    e2 = 2 * Alpha_E - Alpha_E * Alpha_E
    w = math.sqrt(1 - e2 * math.sin(lat) * math.sin(lat))




    return X, Y, Z


X, Y, Z = geodetic_to_ecef(116.385532, 39.9044099, 0)
print(X, Y, Z)