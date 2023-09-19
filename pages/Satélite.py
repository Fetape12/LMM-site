import streamlit as st
import shutil
# Required modules
import requests                      # HTTP library for Python
import time as t                     # Time access and conversion
from osgeo import gdal                              # Python bindings for GDAL
import matplotlib.pyplot as plt                     # Plotting library
import cartopy, cartopy.crs as ccrs                 # Plot maps
import cartopy.io.shapereader as shpreader          # Import shapefiles
import os                                           # Miscellaneous operating system interfaces
import numpy as np                                  # Scientific computing with Python
from matplotlib import cm                           # Colormap handling utilities
from datetime import timedelta, date, datetime  # Basic Dates and time types

import sys
sys.path.append(r'C:\Users\LUCAS\Documents\GitHub\LMM-site\backend')

from get_satelite import download_CMI                  # Our function for download
from get_satelite import reproject                     # Our function for reproject
from get_satelite import loadCPT                       # Import the CPT convert function
import tempfile
from log_time import log_execution_time

#-----------------------------------------------------------------------------------------------------------
st.title("Imagem de Satélite - GOES 16")
temp_dir = None
# Função para validar a data e hora inseridas pelo usuário
def validate_datetime(date, time):
    try:
        selected_datetime = datetime.combine(date, time)
        if selected_datetime < datetime(1900, 1, 1, 0, 0) or selected_datetime > datetime.now():
            st.error("A data e hora devem estar entre 1900-01-01 00:00 e o momento atual.")
            return None
        return selected_datetime
    except Exception as e:
        st.error("Erro ao validar a data e hora. Certifique-se de inserir valores válidos.")
        return None

# Adicione um seletor de data
selected_date = st.date_input("Selecione a data:", min_value=datetime(1900, 1, 1), max_value=datetime.now())

# Adicione um seletor de hora
selected_time = st.time_input("Selecione a hora:")

selected_datetime = validate_datetime(selected_date, selected_time) # Combine a data e a hora selecionadas em um único objeto datetime

if selected_datetime and st.button("Gerar Mapa"):
  try:
    log_execution_time.last_time = t.time()
    dt = datetime(selected_date.year, selected_date.month, selected_date.day, selected_time.hour, selected_time.minute)
    # Transforme a data dt em um formato yyyymmddhh
  # Start the time counter
    start_time = t.time()

    ##########################################################################################################
    # ALTERAR A DATA DESEJADA AQUI!!! 
    # Desired date (last 10 days only!): Format - 'YYYY, MM, DD, HH'
    ##########################################################################################################


    yyyymmddhhmn = (f'{dt:%Y%m%d%H}00') # Data e hora da imagem de satélite

    #-----------------------------------------------------------------------------------------------------------

    # Download directory temp
    temp_dir = tempfile.mkdtemp()
    log_execution_time(f"Criou diretório temp_dir")
    # Desired date (last 10 days only!): Format - 'YYYYMMDD'
    #date = datetime.today().strftime('%Y%m%d')
    date = (f'{dt:%Y%m%d}')

    # Desired extent - COLOCAR AQUI ENTRE ASPAS POIS É UMA STRING
    # longitude de -180 a 180
    min_lon = '-100.'
    max_lon = '-10.'
    min_lat = '-67.50'
    max_lat = '0.'

    # Desired resolution: '25' or '50' or '1'
    resolution = '1'

    # Desired run: '00' or '06' or '12' or '18'
    #hour_run = '00'
    hour_run=(f'{dt:%H}')

    # Desired forecast hours
    hour_ini = 0  # Init time
    hour_end = 0 # End time
    hour_int = 3  # Interval

    if (resolution == '25'):
      res = 'pgrb2.0p'+resolution+'.f'
    elif (resolution == '50'):
      res = 'pgrb2.0p'+resolution+'.f'
    elif (resolution == '1'):
      res = 'pgrb2.'+resolution+'p00.f'
      
    gdal.PushErrorHandler('CPLQuietErrorHandler')       # Ignore GDAL warnings
    #-----------------------------------------------------------------------------------------------------------

    # Select the extent [min. lon, min. lat, max. lon, max. lat]
    #lembrar que longitude está definida entre -180 e 180
    extent = [float(min_lon), float(min_lat), float(max_lon), float(max_lat)]

    # Input and output directories
    input = temp_dir
    output = temp_dir
    log_execution_time(f"def input output")
    #-----------------------------------------------------------------------------------------------------------
    date = (f'{dt:%Y%m%d}')
    yyyymmddhhmn = (f'{dt:%Y%m%d%H}00') # Data e hora da imagem de satélite
    hour_run=(f'{dt:%H}')

    # Download the ABI file channel 13 - Clean IR
    file_ir = download_CMI(yyyymmddhhmn, 13, input)
    log_execution_time(f"dowload CMI")
    #-----------------------------------------------------------------------------------------------------------
    # Variable
    var = 'CMI'

    # Open the file
    img = gdal.Open(f'NETCDF:{input}/{file_ir}.nc:' + var)
    log_execution_time(f"criou img")
    # Read the header metadata
    metadata = img.GetMetadata()
    scale = float(metadata.get(var + '#scale_factor'))
    offset = float(metadata.get(var + '#add_offset'))
    undef = float(metadata.get(var + '#_FillValue'))
    dtime = metadata.get('NC_GLOBAL#time_coverage_start')
    log_execution_time(f"ler img")
    # Load the data
    ds_cmi = img.ReadAsArray(0, 0, img.RasterXSize, img.RasterYSize).astype(float)
    log_execution_time(f"load img")
    # Apply the scale, offset and convert to celsius
    ds_cmi = (ds_cmi * scale + offset) - 273.15

    # Reproject the file
    filename_ret = f'{output}/IR_{yyyymmddhhmn}.nc'
    reproject(filename_ret, img, ds_cmi, extent, undef)
    log_execution_time(f"reprojeta")
    # Open the reprojected GOES-R image
    file = gdal.Open(filename_ret)

    # Get the pixel values
    data = file.GetRasterBand(1).ReadAsArray()
    log_execution_time(f"abrir e obter os pixels do IR")
    #-----------------------------------------------------------------------------------------------------------

    # plotando sat + mslp + esp + vbarbs
    # Choose the plot size (width x height, in inches)
    plt.figure(figsize=(15,15))

    # Use the Geostationary projection in cartopy
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([extent[0], extent[2], extent[1], extent[3]], ccrs.PlateCarree())

    # Define the image extent
    img_extent = [extent[0], extent[2], extent[1], extent[3]]

    # Define the color scale based on the channel
    # Converts a CPT file to be used in Python
    cpt = loadCPT(r'sat_shp/IR4AVHRR6.cpt')
    colormap = cm.colors.LinearSegmentedColormap('cpt', cpt)
    log_execution_time(f"loadCPT")
    # Plot the image
    img1 = ax.imshow(data, origin='upper', vmin=-80, vmax=60, extent=img_extent, cmap=colormap, alpha=0.7)
    log_execution_time(f"criou img1")
    # Add a colorbar
    #plt.colorbar(img1, label='Brightness Temperatures (°C)', extend='both', orientation='horizontal', pad=0.03, aspect = 50)

    # Plot thickness with multiple colors
    clevs = (np.arange(0, 540, 6),
            np.array([540]),
            np.arange(546, 700, 6))
    colors = ('tab:blue', 'b', 'tab:red')
    kw_clabels = {'fontsize': 11, 'inline': True, 'inline_spacing': 5, 'fmt': '%i',
                  'rightside_up': True, 'use_clabeltext': True}


    # Plot the barbs
    skip=8
    bcolor='dimgrey'

    # Add a shapefile
    # https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2019/Brasil/BR/br_unidades_da_federacao.zip
    shapefile = list(shpreader.Reader(r'sat_shp/BR_UF_2019.shp').geometries())
    ax.add_geometries(shapefile, ccrs.PlateCarree(), edgecolor='white',facecolor='none', linewidth=0.3)
    log_execution_time(f"ler shapefile")
    # Add coastlines, borders and gridlines
    ax.coastlines(resolution='10m', color='white', linewidth=0.8)
    ax.add_feature(cartopy.feature.BORDERS, edgecolor='white', linewidth=0.5)
    gl = ax.gridlines(crs=ccrs.PlateCarree(), color='white', alpha=1.0, linestyle='--', linewidth=0.25, xlocs=np.arange(-180, 180, 5), ylocs=np.arange(-90, 90, 5), draw_labels=True)
    gl.top_labels = False
    gl.right_labels = False

    # Use definition to plot H/L symbols
    #plot_maxmin_points(lons, lats, prmls, 'max', 50, symbol='H', color='b',  transform=ccrs.PlateCarree())
    #plot_maxmin_points(lons, lats, prmls, 'min', 25, symbol='L', color='r', transform=ccrs.PlateCarree())

    # Extract date
    date = (datetime.strptime(dtime, '%Y-%m-%dT%H:%M:%S.%fZ'))

    # Add a title
    plt.title('GOES-16 Ch13 ' + date.strftime('%Y-%m-%d %H:%M') + ' UTC', fontweight='bold', fontsize=10, loc='left')
    #plt.title('Reg.: ' + str(extent) , fontsize=10, loc='right')
    #-----------------------------------------------------------------------------------------------------------
    # Save the image
    #plt.savefig(f'{output}/Sat_mslp_Esp_V.png', bbox_inches='tight', pad_inches=0, dpi=300)

    # Show the image
    st.pyplot(plt)
    log_execution_time(f"plotou")
  finally:
    st.stop()
    #shutil.rmtree(temp_dir)
  
  
  