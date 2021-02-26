import numpy as np
from numba import njit, jit, prange


@jit(nopython=True)
def radius_correction(year, month, day):
    """TBA.
    """
    if year % 4:
        year_ratio = ((month-1)/12) + (day/365)
    else:
        year_ratio = ((month-1)/12) + (day/366)
    day_angle = 2 * np.pi * year_ratio
    rc = 1.000110 + 0.034221*np.cos(day_angle) + 0.001280*np.sin(day_angle) \
        + 0.000719*np.cos(2*day_angle) + 0.000077*np.sin(2*day_angle)
    return rc


@jit(nopython=True)
def total_solar_irradiance(radius_correction, solar_constant=1361):
    """TBA.
    """
    return radius_correction*solar_constant


@jit(nopython=True)
def atmospheric_air_mass(air_mass, altitude=None):
    """If the atmosphere is treated as a horizontal slab of material of unit
    thickness, the shortest path length is along the vertical to the local
    horizontal. This path length is defined as "air mass," M.

    Parameters
    ----------
    air_mass : float
        The geometric air mass.
    
    altitude : float
        The site altitude.

    Returns
    -------
    M : float
        The air mass

    References:
    - Revised optical air mass tables and approximation formula
    """
    # if elev_deg < 20: # is this right?
    #     refraction = 0.50572 * (6.07995+elev_deg)**(-1.6364)
    #     air_mass += refraction
    if altitude:
        #local_pressure = 101.324 * np.exp(-0.000832 * altitude / 1000)
        return air_mass * np.exp(-0.000832 * altitude / 1000)
    else:
        return air_mass


@jit(nopython=True)
def rayleigh_transmittance(atm_air_mass):
    """TBA.

    Parameters
    ----------
    atm_air_mass : float
        The atmospheric adjusted air mass.

    Returns
    -------
    Tr : float
        Rayleigh transmittance by Bird and Hulstrom (eq. 3.6).
    """
    return np.exp(-0.0903 * (atm_air_mass**0.84) * (1 + atm_air_mass - atm_air_mass**1.01))


@jit(nopython=True)
def mixed_gas_transmittance(atm_air_mass):
    """TBA.
    
    Parameters
    ----------
    atm_air_mass : float
        The atmospheric adjusted air mass.

    Returns
    -------
    Tg : float
        Mixed gas transmittance (eq. 3.7).
    """
    return np.exp(-0.0127 * atm_air_mass**0.26)


@jit(nopython=True)
def ozone_transmittance(oz, geo_air_mass):
    """TBA.

    Parameters
    ----------
    oz : float
        Total column ozone amount in kg m**-2.
    
    geo_air_mass : float
        The geometric air mass.

    Returns
    -------
    To : float
        Ozone transmittance (eq. 3.8 and 3.9).
    """
    ozm = oz * geo_air_mass / 10 # divide by 10 to make kg m**-2 into atm-cm
    return 1-0.1611 * ozm * (1 + 139.48*ozm)**(-0.3035) - (0.002715*ozm)/(1 + 0.044*ozm + 0.0003*ozm**2)


@jit(nopython=True)
def water_vapor_transmittance(pw, geo_air_mass):
    """TBA.

    Parameters
    ----------
    pw : float
        Preciptable water vapor amount in kg m**-2.
    
    geo_air_mass : float
        The geometric air mass.

    Returns
    -------
    Tw : float
        Water vapour transmittance (eq. 3.10 and 3.11).
    """
    w = pw * geo_air_mass / 10 # divide by 10 to make kg m**-2 into atm-cm
    return 1-2.4959*w / ((1 + 79.034*w)**0.6828 + 6.385*w)


@jit(nopython=True)
def aerosol_transmittance(aod, geo_air_mass, angstrom=1.3):
    """TBA.

    Parameters
    ----------
    aod : float
        Aerosol optical depth at 550nm.
    """
    ta3 = aod*(380/550)**(-angstrom)
    ta5 = aod*(500/550)**(-angstrom)
    tau = 0.2758*ta3 + 0.35*ta5 # eq. 3.12
    return np.exp(-tau**0.873 * (1+tau - tau**0.7088) * geo_air_mass**0.9108) # eq. 3.13


@jit(nopython=True)
def aerosol_absorptance(geo_air_mass, aerosol_transmittance):
    """TBA.
    """
    numerator = 1 - geo_air_mass + geo_air_mass**1.06
    denominator = 10*(1-aerosol_transmittance)
    return 1 - (numerator/denominator)


@jit(nopython=True)
def sky_diffuse_radiation(tsi, elev_angle, Tg, To, Tw, Taa):
    """TBA.
    """
    return 0.79*tsi * np.cos((np.pi/2)-elev_angle) * Tg*To*Tw*Taa


@jit(nopython=True)
def direct_horizontal_irradiance(dni, elev_angle, ds, geo_air_mass, Tr, Ta, Taa, albedo):
    """TBA.
    
    Parameters
    ----------
    ds : float
        Sky diffuse radiation.
    """
    numerator = 0.5*(1-Tr) + 0.85*(1-(Ta/Taa))
    denominator = 1 - geo_air_mass + geo_air_mass**1.02
    ihs = ds * (numerator/denominator)
    Rs = 0.0685 + 0.16*(1-(Ta/Taa))
    ghi = (dni * np.cos((np.pi/2)-elev_angle) + ihs)/(1-(albedo*Rs))
    return ghi - (dni * np.cos((np.pi/2)-elev_angle))


@jit(nopython=True)
def ground_reflected_irradiance(dni, dhi, elev_angle, albedo, tilt_angle=0.10471975511965978):
    """TBA.
    """
    ghi = dni*np.cos((np.pi/2)-elev_angle) + dhi
    view_factor = (1-np.cos(tilt_angle))/2
    return ghi * albedo * view_factor


@njit(parallel=True)
def clear_sky_irradiance(elevs, aois, dem, ozs, wvs, aods, albedos, clouds, year, month, day):
    """TBA.

    Parameters
    ----------
    elevs : array
        Array of site elevation angles.
    
    dem : array
        Array of site altitudes (in meters).
    
    ozs : array
        Array of column ozone amount.

    wvs : array
        Array of precipitable water vapor amount.

    aods : array
        Array of aerosol optical depths at 550nm.

    year : float
        Year.

    month : float
        Month.

    day : float
        Day.

    Returns
    -------
    """
    # Calculate total solar irradiation
    radius = radius_correction(year, month, day)
    tsi = total_solar_irradiance(radius)
    irradiance = np.full(dem.shape, -32768.0)

    # Calculate stepsizes
    n_rows, n_cols = dem.shape
    elev_stepsize = np.round(n_rows / elevs.shape[0])
    trans_stepsize = np.round(n_rows / ozs.shape[0])
    albedo_stepsize = np.round(n_rows / albedos.shape[0])

    # Geometric air mass
    geo_air_mass = 1/np.sin(elevs)

    # Calculate transmittances
    for y in prange(n_cols):
        # if y % (n_cols // 100) == 0:
        #     print(100*y/n_cols, 'percent done')
        for x in range(n_rows):
            if dem[x, y] == -32768:
               continue
            cur_altitude = dem[x, y]
            x_elev = int(x/elev_stepsize)
            y_elev = int(y/elev_stepsize)

            x_trans = np.abs(np.arange(ozs.shape[0])-int(x/trans_stepsize)).argmin()
            y_trans = np.abs(np.arange(ozs.shape[1])-int(y/trans_stepsize)).argmin()

            x_alb = np.abs(np.arange(albedos.shape[0])-int(x/albedo_stepsize)).argmin()
            y_alb = np.abs(np.arange(albedos.shape[1])-int(y/albedo_stepsize)).argmin()

            # Calculate atmospheric adjusted air mass
            cur_geo_air_mass = geo_air_mass[x_elev, y_elev]
            cur_atm_air_mass = atmospheric_air_mass(cur_geo_air_mass, cur_altitude)
            #air_mass[x, y] = cur_geo_air_mass * np.exp(-0.000832 * cur_altitude / 1000)

            ### DIRECT NORMAL IRRADIANCE
            # Calculate rayleigh transmittance
            Tr = rayleigh_transmittance(cur_atm_air_mass)

            # Calculate mixed gas transmittance
            Tg = mixed_gas_transmittance(cur_atm_air_mass)

            # Calculate ozone transmittance
            To = ozone_transmittance(ozs[x_trans, y_trans], cur_geo_air_mass)

            # Calculate water vapour transmittance
            Tw = water_vapor_transmittance(wvs[x_trans, y_trans], cur_geo_air_mass)

            # Calculate aerosol transmittance
            Ta = aerosol_transmittance(aods[x_trans, y_trans], cur_geo_air_mass)

            # Calculate total transmittance
            total_trans = Tr * Tg * To * Tw * Ta

            # Calculate DNI
            dni = tsi * total_trans
            
            ### DIFFUSE HORIZONTAL IRRADIANCE
            # Calculate aerosol absorptance
            Taa = aerosol_absorptance(cur_geo_air_mass, Ta)

            # Calculate sky diffuse irradiance
            Ds = sky_diffuse_radiation(tsi, elevs[x_elev, y_elev], Tg, To, Tw, Taa)

            # Calculate DHI
            dhi = direct_horizontal_irradiance(dni, elevs[x_elev, y_elev], Ds, cur_geo_air_mass, Tr, Ta, Taa, albedos[x_alb, y_alb])

            ### GROUND REFLECTED IRRADIANCE
            Eg = ground_reflected_irradiance(dni, dhi, elevs[x_elev, y_elev], albedos[x_alb, y_alb])

            ### IRRADIANCE
            aoi = aois[x_elev, y_elev]
            clear = dni*np.cos(aoi) + dhi + Eg
            # Check if cloud
            cloud_index = 1
            if clouds[x_alb, y_alb] != -32768:
                cloud_index -= clouds[x_alb, y_alb]
            irradiance[x, y] = clear * cloud_index
            #irradiance[x, y] = Taa

            # if x % 2500 == 0:
            #     print('taa', Taa)
            #     print('ta', Ta)
            #     print('dni', dni)
            #     print('tr', Tr)
            #     print('ds', Ds)
    return irradiance
    