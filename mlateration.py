from math import cos, sin, degrees, asin, atan2
from scipy.optimize import minimize
import numpy as np
import pyproj


def solve(stations):
    def error(x, c, r):
        return sum([(np.linalg.norm(x - c[idx]) - r[idx]) ** 2 for idx in range(len(c))])

    # extract data
    distances_to_station = []
    stations_coordinates = list()
    for sta in stations:
        distances_to_station.append(sta.tower_range * ((255.0 - sta.signal) / 255.0))
        stations_coordinates.append([sta.latitude, sta.longitude])

    count = len(stations)
    S = sum(distances_to_station)
    # compute weight vector for initial guess
    W = [((count - 1) * S) / (S - w) for w in distances_to_station]
    # get initial guess of point location
    x0 = 0
    for i in range(count):
        x0 += [stations_coordinates[i] * W[i]]

    # optimize distance from signal origin to border of spheres
    return minimize(error, x0, args=(stations_coordinates, distances_to_station), method='Nelder-Mead').x


def EarthRadiusAtLatitude(lat):
    rlat = np.deg2rad(lat)

    a = np.float64(6378137.0)
    b = np.float64(6356752.3)

    rad = np.sqrt(((a*a*np.cos(rlat))**2 + (b*b*np.sin(rlat))**2) /
                  ((a*np.cos(rlat))**2 + (b*np.sin(rlat))**2))
    return rad


def solve2(stations):
    A = []
    b = []
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    p = pyproj.Proj(proj='utm',  ellps='WGS84', preserve_units=False)

    for sta in stations:
        R = EarthRadiusAtLatitude(sta.latitude)
        x, y = p(sta.latitude, sta.longitude, radians=False)

        #x = cos(np.deg2rad(sta.longitude)) * cos(np.deg2rad(sta.latitude))
        #y = sin(np.deg2rad(sta.longitude)) * cos(np.deg2rad(sta.latitude))
        #z = sin(np.deg2rad(sta.latitude))
        dist = sta.tower_range * ((255.0 - sta.signal) / 255.0)
        Am = 2 * x
        Bm = 2 * y
       # Cm = 2 * z

        Dm = R * R + (pow(x, 2) + pow(y, 2)) - pow(dist, 2)
        A += [[Am, Bm]]
        b += [[Dm]]
    # Solve using Least Squares of an MxN System
    # A*x = b --> x = (ATA)_inv.AT.b = A+.b
    A = np.array(A)
    b = np.array(b)
    AT = A.T
    ATA = np.matmul(AT, A)
    ATA_inv = np.linalg.inv(ATA)
    Aplus = np.matmul(ATA_inv, AT)
    x = np.matmul(Aplus, b)
    # convert back to lat/long from ECEF
    # convert to degrees
    lat, lon = p( x[0], x[1], inverse=True)
   # lat = degrees(asin(x[2] / EarthRadiusAtLatitude(stations[0].latitude)))
   # lon = degrees(atan2(x[1], x[0]))
    return lat, lon
