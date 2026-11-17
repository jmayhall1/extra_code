# coding=utf-8
import glob
import xarray as xr
import numpy as np

files = glob.glob('//uahdata/rstor/cm1r21.1/3d/cm1out_3d_combined_0008.nc')
for f in files:
    with xr.open_dataset(f) as ds:
        print(ds.variables)
        print(np.nanmax(ds.variables['qke_adv'].values))
        print(np.nanmax(ds.variables['qke'].values))
        exit()