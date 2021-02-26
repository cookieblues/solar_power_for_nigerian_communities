import numpy as np
import numba as nb
from numba import jit, float32


@jit(nopython=True, fastmath=True)
def delta_t(year, month):
    """Difference between Universal Time (UT, defined by Earth's rotation)
    from Terrestrial Time (TT, independent of the Earth's rotation).

    Parameters
    ----------
    year : int
        Input year.
    
    month : int
        Input month.

    Returns
    -------
    delta_t : float
        Approximation of difference between UT and TT from 1980 to 2030.
    """
    decimal_year = year + (month-0.5)/12
    if 1980 <= decimal_year < 1986:
        A = [45.45, 1.067, -1/260, -1/718]
        constant = decimal_year-1975
    elif 1986 <= decimal_year < 2005:
        A = [63.86, 0.3345, -0.060374, 0.0017275, 6.518e-04, 2.374e-05]
        constant = decimal_year-2000
    elif 2005 <= decimal_year <= 2030:
        A = [63.48, 0.2040, 0.005576]
        constant = decimal_year-2000
    else:
        ValueError('Provided year out of range (1980-2030).')

    sum_ = 0
    for k, a in enumerate(A):
        sum_ += a*constant**k
    return sum_


@jit(nopython=True)
def universal_julian_date(year, month, day, hour):
    """The Universal Time Julian day corresponds to the decimal number of days
    starting from January 1, in the year -4712 at 12:00:00 UT.

    Parameters
    ----------
    year : int
        Year greater than 1582.

    month : int
        Month between 1 and 12.

    day : int
        Valid day number in given month and year.
    
    hour : float
        Decimal UT hour.

    Returns
    -------
    julian_date : float
        The universal julian date.
    """   
    if month == 1 or month == 2:
        year -= 1
        month += 12

    date = int(365.25*year) + int(30.6001*(month+1)) + day + 1720995

    # Check for Gregorian calendar switch
    if day+31*((month+1)+12*year) >= 588829:
        date += 2-int(0.01*year)+int(0.25*int(0.01*year))

    # Correct for half-day offset
    dayfrac = hour / 24 - 0.5
    if dayfrac < 0:
        dayfrac += 1
        date -= 1

    # Fraction of a day
    frac = dayfrac + (hour - int(hour)) / 1440 # minute frac
    return date + frac


@jit(nopython=True)
def terrestrial_julian_date(year, month, day, hour):
    """TBA.
    """
    jut = universal_julian_date(year, month, day, hour)
    dt = delta_t(year, month)
    return jut + (dt / 86400)


@jit(nopython=True)
def modified_universal_julian_date(uni_julian_date):
    """TBA.
    """
    return uni_julian_date - 2444239.5


@jit(nopython=True)
def modified_terrestrial_julian_date(terre_julian_date):
    """TBA.
    """
    return terre_julian_date - 2444239.5


@nb.jit(float32(float32), nopython=True, fastmath=True)
def earth_heliocentric_longitude(mod_terre_julian_date):
    """TBA.

    Returns
    -------
        longitude : float
            Radians.
    """
    mjtt = mod_terre_julian_date
    a = 1/58.130101
    b = 1.742145
    f = np.array([
        1/365.261278, 1/182.632412, 1/29.530634, 1/399.529850, 1/291.956812,
        1/583.598201, 1/4652.629372, 1/1450.236684, 1/199.459709, 1/365.355291
    ], dtype=np.float32)
    rho = np.array([
        3.401508e-02, 3.486440e-04, 3.136227e-05, 3.578979e-05, 2.676185e-05,
        2.333925e-05, 1.221214e-05, 1.217941e-05, 1.343914e-05, 8.499475e-04
    ], dtype=np.float32)
    phi = np.array([
        1.600780, 1.662976, -1.195905, -1.042052, 2.012613,
        -2.867714, 1.225038, -0.828601, -3.108253, -2.353709
    ], dtype=np.float32)

    sum_ = 0
    for i in range(10):
        sum_ += rho[i] * np.cos(2*np.pi * f[i] * mjtt - phi[i])
    
    return sum_ + a*mjtt + b


@jit(nopython=True)
def refraction_correction(elevation, annual_pressure=1013.25, annual_temp=27):
    """TBA.

    Parameters
    ----------
    elevation : float
        Sun topocentric elevation angle without refraction correction.

    annual_pressure : float
        Yearly average local air pressure expressed in hPa.

    annual_temp : float
        Yearly average local air temperature in Celsius.
    """
    K = (annual_pressure/1010) * (283/(273+annual_temp))
    if elevation > -0.01:
        correction = K * 2.96706*10e-04 / np.tan(elevation + 0.0031376/(elevation + 0.089186))
    else:
        correction = -K * 1.005516*10e-04 / np.tan(elevation)
    return correction


@jit(nopython=True)
def earth_heliocentric_latitude(terre_julian_date):
    """TBA.

    Returns
    -------
        latitude : float
            Radians.
    """
    terre_julian_century = (terre_julian_date-2451545)/36525
    JME = terre_julian_century/10

    B00 = 280 * np.cos(3.199 + 84334.662*JME)
    B01 = 102 * np.cos(5.422 + 5507.553*JME)
    B02 = 80 * np.cos(3.88 + 5223.69*JME)
    B03 = 44 * np.cos(3.7 + 2352.87*JME)
    B04 = 32 * np.cos(4 + 1577.34*JME)
    
    B10 = 9 * np.cos(3.9 + 5507.55*JME)
    B11 = 6 * np.cos(1.73 + 5223.69*JME)

    B0 = B00 + B01 + B02 + B03 + B04
    B1 = B10 + B11

    B = (B0 + B1 * JME) / 10**8
    return B


@jit(nopython=True)
def nutation_sun_geocentric_longitude(mod_terre_julian_date):
    """TBA.

    Returns
    -------
        longitude : float
            Radians.
    """
    mjtt = mod_terre_julian_date
    f = 1/6791.164405
    rho = 8.329092e-05
    phi = -2.052757
    
    return rho * np.cos(2*np.pi*f*mjtt - phi)
    

@jit(nopython=True)
def true_earth_obliguity(mod_terre_julian_date):
    """TBA.

    Returns
    -------
        obliguity : float
            Radians.
    """
    mjtt = mod_terre_julian_date
    a = -6.216374e-09
    b = 4.091383e-01
    f = 1/6791.164405
    rho = 4.456183e-05
    phi = 2.660352

    return rho * np.cos(2*np.pi*f * mjtt - phi) + a*mjtt + b


#@jit(nopython=True)
@nb.jit(nb.types.UniTuple(nb.float32,2)(nb.float32),nopython=True)
def apparent_sun_longitude(mod_terre_julian_date):
    """TBA.

    Returns
    -------
        longitude : float
            Radians.
    """
    Sigma = earth_heliocentric_longitude(mod_terre_julian_date) + np.pi
    delta_psi = nutation_sun_geocentric_longitude(mod_terre_julian_date)
    delta_tau = -9.9337353631981704e-05

    return Sigma + delta_psi + delta_tau, delta_psi


@nb.jit(nb.types.UniTuple(nb.float32,2)(nb.float32, nb.float32, nb.float32, nb.float32),nopython=True)
def H_and_delta(longitude, terre_julian_date, mod_terre_julian_date, mod_uni_julian_date):
    epsilon = true_earth_obliguity(mod_terre_julian_date)
    lambd, delta_psi = apparent_sun_longitude(mod_terre_julian_date)
    beta = -earth_heliocentric_latitude(terre_julian_date)

    # Calculate apparent sidereal time
    v0 = 6.300388099*mod_uni_julian_date + 1.742079 # ADJUSTED! removed one 0
    v = v0 + delta_psi*np.cos(epsilon)

    # Calculate sun right ascension
    numerator = np.sin(lambd)*np.cos(epsilon) - np.tan(beta)*np.sin(epsilon)
    denominator = np.cos(lambd)
    alpha = np.arctan2(numerator, denominator)

    # Calculate observer local hour angle
    H = v + longitude - alpha

    # Calculate geocentric declination
    delta = np.arcsin(
        np.sin(beta)*np.cos(epsilon) + np.cos(beta)*np.sin(epsilon)*np.sin(lambd)
    )

    return H, delta


@nb.jit(nb.types.UniTuple(nb.float32,2)(nb.float32, nb.float32, nb.float32, nb.float32, nb.float32, nb.float32),nopython=True)
def topocentric_coords(latitude, longitude, elevation, terre_julian_date, mod_terre_julian_date, mod_uni_julian_date):
    """TBA.
    """
    # Calculate observer local hour angle and geocentric declination
    H, delta = H_and_delta(
        longitude, terre_julian_date, mod_terre_julian_date, mod_uni_julian_date
    )

    # Geographical ellipsoid reference coordinates
    u = np.arctan((1-1/298.257282697) * np.tan(latitude))
    x = np.cos(u) + np.cos(latitude)*elevation/6378140
    y = (1-1/298.257282697) * np.sin(u) + np.sin(latitude) * elevation/6378140
    
    # Sun equatorial horizontal parallax
    xi = 4.263521e-05

    # Calculate topocentric declination
    delta_ = delta + (x*np.cos(H)*np.sin(delta) - y*np.cos(delta)) * xi

    # Calculate topocentric local hour angle
    numerator = -x*np.sin(xi)*np.sin(H)
    denominator = np.cos(delta) - x*np.sin(xi)*np.cos(H)
    delta_alpha = np.arctan2(numerator, denominator)

    H_ = H-delta_alpha

    return delta_, H_


@nb.jit(nb.types.UniTuple(nb.float32,2)(nb.float32, nb.float32, nb.float32, nb.float32, nb.float32, nb.float32),nopython=True)
def sun_topocentric_elevation_azimuth(latitude, longitude, elevation, terre_julian_date, mod_terre_julian_date, mod_uni_julian_date):
    # Calculate topocentric declination and local hour angle
    delta_, H_ = topocentric_coords(
        latitude, longitude, elevation, terre_julian_date, mod_terre_julian_date, mod_uni_julian_date
    )

    # Calculate the topocentric elevation without atmospheric refraction correction
    e0 = np.arcsin(
        np.sin(latitude)*np.sin(delta_) + np.cos(latitude)*np.cos(delta_)*np.cos(H_)
    )

    # Calculate topocentric elevation
    delta_e = refraction_correction(e0)
    elevation = e0 + delta_e

    # Calculate topocentric azimuth
    azimuth = np.arctan2(
        np.sin(H_),
        np.cos(H_)*np.sin(latitude) - np.tan(delta_)*np.cos(latitude)
    )

    return elevation, azimuth


@nb.jit(nb.types.UniTuple(nb.float32,2)(nb.float32, nb.float32, nb.float32, nb.float32, nb.float32, nb.float32, nb.float32),nopython=True)
def solar_position(latitude, longitude, elevation, year, month, day, hour):
    """TBA.

    Returns
    -------
    elevation : float
        In radians.

    azimuth : float
        In radians.
    """
    latitude = np.pi*latitude/180 # radians
    longitude = np.pi*longitude/180 # radians

    uni_julian_date = universal_julian_date(year, month, day, hour)
    terre_julian_date = terrestrial_julian_date(year, month, day, hour)
    mod_uni_julian_date = modified_universal_julian_date(uni_julian_date)
    mod_terre_julian_date = modified_terrestrial_julian_date(terre_julian_date)

    elevation, azimuth = sun_topocentric_elevation_azimuth(
        latitude, longitude, elevation,
        terre_julian_date, mod_terre_julian_date, mod_uni_julian_date
    )

    # change westward from south to eastward from north
    azimuth += np.pi
    azimuth %= 2*np.pi

    return elevation, azimuth



# from datetime import datetime

# import numpy as np
# from matplotlib import cm
# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs

# from src.spa import solar_position

# # time right now
# now = datetime.utcnow()
# year = now.year
# month = now.month
# day = now.day
# hour = now.hour

# #evaluate on a 2 degree grid
# lon  = np.linspace(-180,180,181)
# lat = np.linspace(-90,90,91)
# lons, lats = np.meshgrid(lon, lat)

# orig_shape = lons.shape
# lons = lons.reshape((-1,))
# lats = lats.reshape((-1,))

# elevs = list()
# azis = list()
# for i in range(len(lons)):
#     elev, azi = solar_position(lats[i], lons[i], 0, year, month, day, hour)
#     elevs.append(elev)
#     azis.append(azi)

# elevs = np.array(elevs).reshape(orig_shape)
# azis = np.array(azis).reshape(orig_shape)

# #convert azimuth to vectors
# u, v = np.cos((90-azis)*np.pi/180), np.sin((90-azis)*np.pi/180)

# #plot
# plt.figure(figsize=(13, 8))
# ax = plt.axes(projection=ccrs.PlateCarree())
# ax.stock_img()

# plt.imshow(
#     elevs,
#     cmap=cm.CMRmap,
#     origin='lower',
#     vmin=-90,
#     vmax=90,
#     extent=(-180, 180, -90, 90),
#     alpha=0.375
# )
# s = slice(5, -1, 5) # equivalent to 5:-1:5
# plt.quiver(lon[s], lat[s], u[s, s], v[s, s])
# plt.contour(lon,lat,elevs,[0])
# # #cb = plt.colorbar()
# # #cb.set_label('Elevation Angle (deg)')
# # plt.gca().set_aspect('equal')
# plt.xticks(np.arange(-180,181,45))
# plt.yticks(np.arange(-90,91,45))
# plt.show()
