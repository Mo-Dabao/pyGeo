# -*- coding: utf-8 -*-
"""
根据shp文件生成mask（掩膜）

@Time    : 2020/10/20 21:29
@Author  : modabao
"""

import numpy as np
from osgeo import gdal, osr


def shp2mask(shp_path, description, mask_path='mask'):
    """从shp文件生成mask

    从shp_name的多边形生成形如description的mask

    Args:
        shp_path: shapfile的路径
        description: 
            若description为6个数字组成的序列(upper_left_x, upper_left_y, pixel_width, pixel_height, rows, cols)，则返回
            如description所描述的WGS84地理坐标系下的无旋转mask;
            若description为geotiff文件的路径字符串，则返回形如该tif且相同投影的mask
        mask_path: 生成的mask文件名，支持.tif和.npy格式，否则两种格式都生成

    Returns:
        None
    """
    driver_mem = gdal.GetDriverByName('MEM')
    if isinstance(description, str):
        ds_origin = gdal.Open(description)
        ds_mid = driver_mem.CreateCopy('', ds_origin)
        ds_mid.GetRasterBand(1).WriteArray(np.ones((ds_origin.RasterYSize, ds_origin.RasterXSize), dtype=np.bool))
    else:
        (upper_left_x, upper_left_y, pixel_width, pixel_height, rows, cols) = description
        ds_mid = driver_mem.Create('', cols, rows, 1, gdal.GDT_Byte)
        ds_mid.SetGeoTransform([upper_left_x, pixel_width, 0, upper_left_y, 0, pixel_height])
        ds_mid.SetMetadataItem('AREA_OR_POINT', 'Point')
        ds_mid.GetRasterBand(1).WriteArray(np.ones((rows, cols), dtype=np.bool))
        srs = osr.SpatialReference()
        srs.SetWellKnownGeogCS('WGS84')
        ds_mid.SetProjection(srs.ExportToWkt())
    ds_mask = gdal.Warp('', ds_mid, format='MEM', cutlineDSName=shp_name)
    out_format = mask_path[-4:]
    if out_format == '.tif':
        ds2GTiff(ds_mask, mask_path)
    elif out_format == '.npy':
        ds2npy(ds_mask, mask_path)
    else:
        ds2GTiff(ds_mask, mask_path+'.tif')
        ds2npy(ds_mask, mask_path+'.npy')
    del ds_mid, ds_mask

def ds2GTiff(ds, tif_name):
    gtiff = gdal.GetDriverByName('GTiff')
    result = gtiff.CreateCopy(tif_name, ds)
    result.FlushCache()
    del result

def ds2npy(ds, npy_name):
    np.save(npy_name, ds.ReadAsArray().astype(np.bool), allow_pickle=False)
