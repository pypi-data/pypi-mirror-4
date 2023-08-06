#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Martin Raspaud

# Author(s):

#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Testing the geolocation module of pyorbital.
"""



from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from pyorbital.geoloc import *

def test_avhrr(t):
    # AVHRR

    #NOAA 19 2012 10 23 16:44 utc
    #1 33591U 09005A   12296.39620005  .00000491  00000-0  29525-3 0  5514
    #2 33591  98.8753 234.6683 0014558  24.8361 335.3526 14.11404892190957

    #attitude error according to ana:
    #> 2012/10/23 11:27:07 lxserv248.smhi.se 27301 ana_estatt.exe INFO : attitude yaw    (mrad)     0.0000000000D+00
    #> 2012/10/23 11:27:07 lxserv248.smhi.se 27301 ana_estatt.exe INFO : attitude roll   (mrad)     1.8625462311D+00
    #> 2012/10/23 11:27:07 lxserv248.smhi.se 27301 ana_estatt.exe INFO : attitude pitch  (mrad)    -7.5120984185D+00


    tle1 = "1 33591U 09005A   12296.39620005  .00000491  00000-0  29525-3 0  5514"
    tle2 = "2 33591  98.8753 234.6683 0014558  24.8361 335.3526 14.11404892190957"
    tle1 = "1 26536U 00055A   12312.31001555  .00000182  00000-0  12271-3 0  9594"
    tle2 = "2 26536  99.0767 356.5209 0011007  44.1314 316.0725 14.12803055625240"

    scanline_nb = 5428

    scan_points = np.arange(24, 2048, 40)

    #avhrr = np.vstack(((scan_points - 1023.5) / 1024 * np.deg2rad(-55.37),
    # AAPP uses 55.25°, not 55.37 for some reason...
    avhrr = np.vstack(((scan_points - 1023.5) / 1024 * np.deg2rad(-55.25),
                       np.zeros((len(scan_points),)))).transpose()
    avhrr = np.tile(avhrr, [scanline_nb, 1])
    # building the corresponding times array
    offset = np.arange(scanline_nb) * 0.1667
    times = (np.tile(scan_points * 0.000025 + 0.0025415, [scanline_nb, 1])
             + np.expand_dims(offset, 1))
    # build the scan geometry object
    sgeom = ScanGeometry(avhrr, times.ravel())

    
    #rpy = (1.8625462311e-3, -7.5120984185e-3, 0.0)
    #rpy = (0.5 * 1.8625462311e-3, 0.5 * -7.5120984185e-3, 0.0)

    rpy = [ 0.00015708,  0.00347321,  0.00019199]
    #rpy = [ 0, 0, 0]
    
    # print the lonlats for the pixel positions
    s_times = sgeom.times(t)
    pixels_pos = compute_pixels((tle1, tle2), sgeom, s_times, rpy)
    pos_time = get_lonlatalt(pixels_pos, s_times)
    return pos_time

def test_viirs(t):
        #  TLE comes from ftp://is.sci.gsfc.nasa.gov/ancillary/ephemeris/tle/drl.tle.2012030213
    # NPP
    npp_tle1 = "1 37849U 05001A   12061.00019361  .00000000  00000-0 -31799-4 2    06"
    npp_tle2 = "2 37849 098.7082 000.2437 0000785 084.9351 038.5818 14.19547815017683"


    # npp scanlines @ 375m
    # the sensor scans 48 taking 32 pixels at once (so the height of granule is 48 * 32 = 1536 pixels)
    scanline_nb = 48

    # building the npp angles, 6400 pixels from +55.84 to -55.84 degrees zenith
    #npp = np.vstack(((np.arange(6400) - 3199.5) / 3200 * np.deg2rad(-55.84), np.zeros((6400,)))).transpose()
    #npp = np.tile(npp, [scanline_nb, 1])

    #scan_pixels = 32
    #taking just borders and middle for now
    scan_pixels = 3
    #scan_pixels = 1

    across_track = (np.arange(6400) - 3199.5) / 3200 * np.deg2rad(-55.84)
    #npp = np.tile(npp_line_y, [scan_pixels, 1])

    # y rotation: np.arctan2(11.87/2, 824.0)

    y_max_angle = np.arctan2(11.87/2, 824.0)
    along_track = np.array([-y_max_angle, 0, y_max_angle])
    #along_track = np.array([0])

    scan = np.vstack((np.tile(across_track, scan_pixels),
                      np.repeat(along_track, 6400))).T
    
    npp = np.tile(scan, [scanline_nb, 1])

    # from the timestamp in the filenames, a granule takes 1:25.400 to record (85.4 seconds)
    # so 1.779166667 would be the duration of 1 scanline
    # dividing the duration of a single scan by a width of 6400 pixels results in 0.0002779947917 seconds for each column of 32 pixels in the scanline
    # what is the 0.0025415??  this still comes from the AVHRR example at github

    # the individual times per pixel are probably wrong, unless the scanning behaves the same as for AVHRR, The VIIRS sensor rotates to allow internal calibration before each scanline. This would imply that the scanline always moves in the same direction.
    # more info @ http://www.eoportal.org/directory/pres_NPOESSNationalPolarorbitingOperationalEnvironmentalSatelliteSystem.html

    offset = np.arange(scanline_nb) * 1.779166667
    #times = (np.tile(np.arange(6400) * 0.0002779947917 + 0.0025415, [scanline_nb, 1]) + np.expand_dims(offset, 1))

    times = (np.tile(np.arange(6400) * 0.0002779947917, [scanline_nb, scan_pixels]) + np.expand_dims(offset, 1))

    # build the scan geometry object
    sgeom = ScanGeometry(npp, times.ravel())

    # get the pixel locations
    stimes = sgeom.times(t)
    pixels_pos = compute_pixels((npp_tle1, npp_tle2), sgeom, stimes)

    pos_time = get_lonlatalt(pixels_pos, stimes)
    return pixels_pos, pos_time, sgeom

def global_test_viirs():
    ### VIIRS


   # starttime is taken from filename of the 'target' granule

    t = datetime.datetime(2012, 3, 2, 12, 27, 23)
    #    t2 = datetime.datetime(2012, 3, 2, 12, 27, 23) + timedelta(seconds=85.4)

    pixels_pos, pos_time, sg1 = test_viirs(t)
    #    pixels_pos2, pos_time2, sg2 = test_viirs(t2)
    import cProfile, pstats
    cProfile.run('test_viirs(t)', "fooprof")
    p = pstats.Stats('fooprof')
    p.sort_stats('time').print_stats()


    # Mercator map centered above the target granule, near South Africa
    m = Basemap(projection='merc',llcrnrlat=-45,urcrnrlat=-25,llcrnrlon=0,urcrnrlon=40,lat_ts=-35,resolution='l')

    # convert and plot the predicted pixels in red
    x, y = m(pos_time[0],pos_time[1])
    p1 = m.plot(x,y, marker='+', color='red', markerfacecolor='red', markeredgecolor='red', markersize=1, markevery=1, zorder=4, linewidth=0.0)

    # read the validation data from CSV, its lat and lon from the outer pixel edge in the geolocation file
    # source: GITCO_npp_d20120302_t1227233_e1228475_b01789_c20120303154859293970_noaa_ops.h5

    #bound = np.genfromtxt('D:\\GITCO_npp_d20120302_t1227233_e1228475_b01789_c20120303154859293970_noaa_ops_outer_edge.csv', delimiter=',', names=True)

    # convert and plot validation data in blue
    #tmpx, tmpy = m(bound['Lon'],bound['Lat'])
    #p2 = m.plot(tmpx,tmpy, marker='o', color='blue', markerfacecolor='blue', markeredgecolor='blue', markersize=0.1, markevery=1, zorder=5, linewidth=0.0)


    # general map beautification

    m.fillcontinents(color='0.85', lake_color=None, zorder=3)
    m.drawparallels(np.arange(-90.,90.,5.), labels=[1,0,1,0],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=1)
    m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,1,0,1],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=2)

    plt.title('NPP Granule (Start at 2012-03-02 12:27:23)')
    #    plt.show()
    #plt.savefig('granule_test.png', dpi=400)
    plt.show()


if __name__ == '__main__':
    #t = datetime.datetime(2012, 10, 23, 11, 15, 40, 404000)
    #t = datetime.datetime(2012, 11, 7, 9, 33, 46, 376000)
    t = datetime.datetime(2012, 11, 7, 9, 33, 46, 526000)

    pos_time = test_avhrr(t)

    m = Basemap(projection='stere', llcrnrlat=24, urcrnrlat=70, llcrnrlon=-25, urcrnrlon=120, lat_ts=58, lat_0=58, lon_0=14, resolution='l')


    # convert and plot the predicted pixels in red
    x, y = m(pos_time[0], pos_time[1])
    p1 = m.plot(x,y, marker='+', color='red', markerfacecolor='red', markeredgecolor='red', markersize=1, markevery=1, zorder=4, linewidth=0.0)



    try:
        lons, lats = np.load("/tmp/lons.npy"), np.load("/tmp/lats.npy")
    except IOError:
        from mpop.satellites import PolarFactory

        g = PolarFactory.create_scene("noaa", "16", "avhrr", t, orbit="62526")
        g.load()
        lons = g.area.lons[:, 24:2048:40]
        lats = g.area.lats[:, 24:2048:40]

        np.save("/tmp/lons.npy", lons)
        np.save("/tmp/lats.npy", lats)
        
    x, y = m(lons, lats)

        
        
    p2 = m.plot(x,y, marker='+', color='blue', markerfacecolor='blue', markeredgecolor='blue', markersize=1, markevery=1, zorder=4, linewidth=0.0)



    m.fillcontinents(color='0.85', lake_color=None, zorder=3)
    m.drawparallels(np.arange(-90.,90.,5.), labels=[1,0,1,0],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=1)
    m.drawmeridians(np.arange(-180.,180.,5.), labels=[0,1,0,1],fontsize=10, dashes=[1, 0], color=[0.8,0.8,0.8], zorder=2)

    plt.show()
