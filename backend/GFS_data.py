#%matplotlib inline
from siphon.catalog import TDSCatalog
from xarray.backends import NetCDF4DataStore
import xarray as xr
from datetime import datetime, timedelta
import numpy as np
from netCDF4 import num2date
from metpy.units import units
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from metpy.plots import ctables

def get_GFS():
    best_gfs = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/grib/NCEP/GFS/'
                      'Global_0p25deg/catalog.xml?dataset=grib/NCEP/GFS/Global_0p25deg/Best')
    best_ds = list(best_gfs.datasets.values())[0]
    ncss = best_ds.subset()
    return ncss

def plot_GFS(ncss,variable):

  query = ncss.query()

  latmax = 0
  latmin = -40
  lonmax = 360
  lonmin = 200

  query.lonlat_box(north=latmax, south=latmin-5, east=lonmax, west=lonmin).time(datetime.utcnow()+timedelta(hours=3))
  query.accept('netcdf4')
  query.variables(variable)

  data = ncss.get_data(query)
  data = xr.open_dataset(NetCDF4DataStore(data))

  temp_3d = data[variable]

  # Helper function for finding proper time variable
  def find_time_var(var, time_basename='time'):
      for coord_name in var.coords:
          if coord_name.startswith(time_basename):
              return var.coords[coord_name]
      raise ValueError('No time variable found for ' + var.name)


  time_1d = find_time_var(temp_3d)
  lat_1d = data['latitude']
  lon_1d = data['longitude']

  # Reduce the dimensions of the data and get as an array with units
  temp_2d = temp_3d.metpy.unit_array.squeeze()

  # Combine latitude and longitudes 
  lon_2d, lat_2d = np.meshgrid(lon_1d, lat_1d)

  # Create a new figure
  fig = plt.figure(figsize=(15, 12))

  # Add the map and set the extent
  ax = plt.axes(projection=ccrs.PlateCarree())
  ax.set_extent([-70, -30, latmin, latmax])

  # Retrieve the state boundaries using cFeature and add to plot
  ax.add_feature(cfeature.STATES, edgecolor='gray')

  # Contour temperature at each lat/long
  contours = ax.contourf(lon_2d, lat_2d, temp_2d, 200, transform=ccrs.PlateCarree(),
                        cmap='RdBu_r')
  #Plot a colorbar to show temperature and reduce the size of it
  plt.colorbar(contours, orientation='vertical', pad=0.05, aspect=50, extendrect=True)

  #ax.set_extent([-60, -35, 0, -43])   # regional map (x0, x1, y0, y1)
  ax.coastlines()
  ax.gridlines(draw_labels=True)
  ax.add_feature(cfeature.OCEAN)
  ax.add_feature(cfeature.LAND, edgecolor='black')
  ax.add_feature(cfeature.STATES)

  # Make a title with the time value
  ax.set_title(f'Temperature forecast [K] for {time_1d[0].values}Z', fontsize=20)

  # Plot markers for each lat/long to show grid points for 0.25 deg GFS
  #ax.plot(lon_2d.flatten(), lat_2d.flatten(), linestyle='none', marker='o',
  #        color='black', markersize=2, alpha=0.3, transform=ccrs.PlateCarree());

  return fig