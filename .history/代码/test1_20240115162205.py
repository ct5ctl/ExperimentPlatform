import math


def geodetic_to_ecef(lat, lon, h):
    lat = lat * math.pi / 180
    lon = lon * math.pi / 180
    Alpha = 0.3352810



    return X, Y, Z


X, Y, Z = geodetic_to_ecef(116.385532, 39.9044099, 0)
print(X, Y, Z)