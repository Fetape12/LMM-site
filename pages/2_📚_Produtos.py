import streamlit as st
import matplotlib.pyplot as plt
import metpy.calc as mpcalc
import matplotlib.gridspec as gridspec
import numpy as np
from metpy.units import units
from datetime import datetime
from siphon.simplewebservice.wyoming import WyomingUpperAir
from metpy.plots import SkewT,Hodograph

# Função para plotar o Skew-T
def plot_skewt(date, station):
    df = WyomingUpperAir.request_data(date, station)
    #Fazendo tabela pandas com dataframe
    # We will pull the data out of the example dataset into individual variables
    # and assign units.
    height_AGL = (df['height']-df['elevation']).values * units.m
    z = df['height'].values * units.m
    p = df['pressure'].values * units.hPa
    T = df['temperature'].values * units.degC
    Td = df['dewpoint'].values * units.degC
    wind_speed = df['speed'].values * units.knots
    wind_dir = df['direction'].values * units.degrees
    u, v = mpcalc.wind_components(wind_speed, wind_dir)

    # Create a new figure. The dimensions here give a good aspect ratio.
    ax = plt.figure(figsize=(9,9))

    # Grid for plots
    gs = gridspec.GridSpec(3, 3)
    skew = SkewT(ax, rotation=30, subplot=gs[:,:2])

    # Plot the data using normal plotting functions, in this case using
    # log scaling in Y, as dictated by the typical meteorological plot
    skew.plot(p, T, 'r', linewidth=1.5)
    skew.plot(p, Td, 'g', linewidth=1.5)
    skew.plot_barbs(p[::2], u[::2], v[::2], y_clip_radius=0.01)
    skew.ax.set_ylim(1000, 100)
    skew.ax.set_xlim(-50, 30)
    parcel_path = mpcalc.parcel_profile(p,T[0], Td[0])
    skew.plot(p,parcel_path, color = 'k',linewidth=1.5)
    skew.shade_cape(p,T,parcel_path)
    skew.shade_cin(p,T,parcel_path)
    skew.ax.set_xlabel('temperatura (\N{DEGREE CELSIUS})',
                       fontdict=dict(size=10))
    skew.ax.set_ylabel('Pressão (hPa)', fontdict=dict(size=10))

    # Calculate LCL height and plot as black dot
    lcl_pressure, lcl_temperature = mpcalc.lcl(p[0], T[0], Td[0])
    lfc_pressure, lfc_temperature = mpcalc.lfc(p, T, Td)
    lcl_hgt = np.round(mpcalc.pressure_to_height_std(lcl_pressure), decimals=3).to(units.meter)
    lfc_hgt = np.round(mpcalc.pressure_to_height_std(lfc_pressure), decimals=3).to(units.meter)
    k_index = mpcalc.k_index(p, T, Td)
    tt_index = mpcalc.total_totals_index(p, T, Td)

    skew.plot(lcl_pressure, lcl_temperature, 'ko', markerfacecolor='black')
    skew.plot(lfc_pressure, lfc_temperature, 'ko', markerfacecolor='blue')

    sb_cape, sb_cin = mpcalc.surface_based_cape_cin(p, T, Td)
    ml_cape, ml_cin = mpcalc.mixed_layer_cape_cin(p, T, Td)
    mu_cape, mu_cin = mpcalc.most_unstable_cape_cin(p, T, Td)
    lr_700_500 = np.round(-1 * np.divide(T[20]-T[14], (z[20]-z[14]).to(units.kilometer)),2)
    sbcape = np.round(sb_cape, 1)
    sbcin = np.round(sb_cin, 1)
    mlcape = np.round(ml_cape, 1)
    mlcin = np.round(ml_cin, 1)
    mucape = np.round(mu_cape, 1)

    u_shear01, v_shear01 = mpcalc.bulk_shear(p, u.to(units.meter/units.second), v.to(units.meter/units.second), depth = 1000 * units.meter)
    shear01 = np.round((np.sqrt(u_shear01**2 + v_shear01**2)), 1)
    u_shear06, v_shear06 = mpcalc.bulk_shear(p, u.to(units.meter/units.second), v.to(units.meter/units.second), depth = 6000 * units.meter)
    shear06 = np.round((np.sqrt(u_shear06**2 + v_shear06**2)), 1)
    rmover, lmover, mean = mpcalc.bunkers_storm_motion(p, u.to(units.meter/units.second), v.to(units.meter/units.second), z)
    srh_01_pos, srh_01_neg, srh_01_tot = mpcalc.storm_relative_helicity(z,u.to(units.meter/units.second), v.to(units.meter/units.second), depth = 1000 * units.meter, bottom = height_AGL[0], storm_u = lmover[0], storm_v = lmover[1])
    srh_01 = np.round(srh_01_neg, 1)
    srh_03_pos, srh_03_neg, srh_03_tot = mpcalc.storm_relative_helicity(z,u.to(units.meter/units.second), v.to(units.meter/units.second), depth = 3000 * units.meter, bottom = height_AGL[0], storm_u = lmover[0], storm_v = lmover[1])
    srh_03 = np.round(srh_03_neg, 1)

    plt.figtext( 0.65, 0.60, 'LCL Height:')
    plt.figtext( 0.8, 0.60, '{:~P}'.format(lcl_hgt))
    plt.figtext( 0.65, 0.58, 'LFC Height:')
    plt.figtext( 0.8, 0.58, '{:~P}'.format(lfc_hgt))
    plt.figtext( 0.65, 0.56, 'MLLR:')
    plt.figtext( 0.8, 0.56, '{:~P}'.format(lr_700_500))
    plt.figtext( 0.65, 0.54, 'IK:')
    plt.figtext( 0.8, 0.54, '{:~P}'.format(k_index))
    plt.figtext( 0.65, 0.52, 'TT:')
    plt.figtext( 0.8, 0.52, '{:~P}'.format(tt_index))

    plt.figtext( 0.65, 0.50, 'MLCAPE:')
    plt.figtext( 0.8, 0.50, '{:~P}'.format(mlcape))
    plt.figtext( 0.65, 0.48, 'MLCIN:')
    plt.figtext( 0.8, 0.48, '{:~P}'.format(mlcin))


    # Calculate full parcel profile and add to plot as black line
    prof = mpcalc.parcel_profile(p, T[0], Td[0]).to('degC')
    skew.plot(p, prof, 'k', linewidth=2)

    # An example of a slanted line at constant T -- in this case the 0
    # isotherm
    skew.ax.axvline(0, color='c', linestyle='--', linewidth=1)
    skew.ax.axvline(-20, color='c', linestyle='--', linewidth=1)

    # Add the relevant special lines
    skew.plot_dry_adiabats()
    skew.plot_moist_adiabats()
    skew.plot_mixing_lines()

    # Create a hodograph
    # Mask velocities to below 10 km only
    mask = z <= 10*units.km
    # Custom colorscale for the wind profile
    intervals = np.array([0, 1, 3, 5, 10]) * units.km
    colors = ['tab:red', 'tab:green', 'tab:blue', 'tab:olive']

    ax1 = ax.add_subplot(gs[0,-1])
    h = Hodograph(ax1, component_range=40.)
    h.add_grid(increment=5)
    u1 = u.to(units('m/s'))
    v1 = v.to(units('m/s'))
    h.plot_colormapped(u1[mask], v1[mask], z[mask], intervals=intervals, colors=colors)

    #plt.title('SMBT', loc='right', x=1.3, y=1)
    plt.title(station+'\nSondagem '+str(date), fontsize=20, fontweight='bold', loc='left', x=-2.7, y=1)

    return ax

# Configuração do aplicativo
st.title("Gerador de Gráfico Skew-T")

# Widgets para entrada de dados
date_input = st.date_input("Selecione a data:", min_value=datetime(1900, 1, 1), max_value=datetime.now())
hour = st.radio("Selecione a hora:", ["00", "12"])
station = st.text_input("Digite o código da estação (por exemplo, 'SBMT'):")

# Botão para gerar o gráfico
if st.button("Gerar Gráfico"):
    if date_input and station:
        date = datetime(date_input.year, date_input.month, date_input.day, 12)  # Hora fixa em 12
        #date = datetime(2019, 12, 23, 12)
        #station = 'SBMT'
        skew = plot_skewt(date, station)
        st.pyplot(skew)
    else:
        st.warning("Por favor, preencha ambos os campos.")

# Informações adicionais ou instruções
st.write("Este aplicativo permite que você gere um gráfico Skew-T para uma estação meteorológica e data específica.")
st.write("Certifique-se de fornecer uma data válida no formato apropriado (ano, mês, dia) e um código de estação válido.")

# Nota: Certifique-se de que você tem todas as bibliotecas necessárias instaladas para que o código funcione corretamente.
