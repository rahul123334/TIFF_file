#!/usr/bin/env python
# coding: utf-8
# author: Rahul Kumar



pip install ee
pip install earthengine-api

import ee


# ee.Authenticate()
ee.Initialize()


minLon = 77.00;
minLat = 12.14;
maxLon = 77.25;
maxLat = 12.39;

aoi = ee.Geometry.Rectangle([77.00, 12.14, 77.25, 12.39]);

# target_projection = input.image.projection.getInfo()["wkt"]
# target_scale = 10
global aoi



def ndvi_s2(image):
    ndvi = image.normalizedDifference(["B8","B4"]).rename("NDVI")
    return image.addBands(ndvi)

def ndvi_modis(image):
    ndvi = image.normalizedDifference(["sur_refl_b02","sur_refl_b01"]).rename("NDVI")
    return image.addBands(ndvi)

def clip_aoi(image):
    return image.clip(aoi)

def resample_and_reproject(image):
    resample_image = image.resample("bilinear").reproject(crs = "EPSG:32643" , scale = 10)
    return resample_image





s2_dataset = (ee.ImageCollection("COPERNICUS/S2_SR")
              .filterDate("2022-01-01","2023-01-01")
              .filterBounds(aoi)
              .map(ndvi_s2).select("NDVI")
              .map(clip_aoi))


modis_dataset = (ee.ImageCollection("MODIS/061/MOD09Q1")
                 .filterDate("2022-01-01","2023-01-01")
                 .filterBounds(aoi)
                 .map(ndvi_modis).select("NDVI")
                 .map(clip_aoi)
                 .map(resample_and_reproject))
print(modis_dataset)




import numpy as np
get_modis_date = np.vectorize(lambda x: x["properties"]["system:index"][:10])
modis_features = modis_dataset.getInfo()["features"]
modis_dates = get_modis_date(modis_features)

updated_modis_dates = [date.replace("_","")for date in modis_dates]
updated_modis_dates


import geemap
geemap.ee_export_image_collection(modis_dataset, out_dir = "R:\\TIFF IMAGE\\modis_16day_250m\\", region = aoi, scale = 250)


get_s2_dates = np.vectorize(lambda x: x["properties"]["system:index"][:8])
s2_features = s2_dataset.getInfo()["features"]
s2_dates = get_s2_dates(s2_features)
s2_features

common_dates = np.intersect1d(s2_dates, updated_modis_dates)
common_dates

s2_time_series = s2_dataset.toList(s2_dataset.size())
s2_time_series



for i in range((s2_dataset.size()).getInfo()):
    image = ee.Image(s2_time_series.get(i))
    s2_date = image.getInfo()["id"][17:25]
    if s2_date in updated_modis_dates:
        geemap.ee_export_image(image, filename= f"R:\\TIFF IMAGE\\image_16\\image_{s2_date}.tif", region = aoi, scale = 10)


s2_date = image.getInfo()["id"][17:25]
print(s2_date)

get_modis_dates = np.vectorize(lambda x : x["properties"]["system:index"][:10])
modis_features = modis_dataset.getInfo()["features"]
modis_dates = get_modis_dates(modis_features)
modis_features


geemap.ee_export_image_collection(modis_dataset, out_dir=  "R:\\TIFF IMAGE\\resample_reproject_modis_8d\\", region = aoi, scale = 10)




