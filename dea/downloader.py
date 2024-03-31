
import os
import shutil
import time
import datetime
import shapely
import geopandas as gpd
import xarray as xr

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from dea import stac, cube

def download_new_site_cube(
        in_poly: list,
        out_nc: str,
        stac_cb_fn,  #: float,
        mask_cb_fn,  #: float,
        band_cb_fn,  #: float,
        text_cb_fn  #: str
) -> xr.Dataset:

    # set up parameters
    # in_lyr = r'C:\Users\Lewis\Desktop\arcdea\studyarea.shp'
    # out_nc = r'C:\Users\Lewis\Desktop\arcdea\s2_oh.nc'
    #in_start_date = datetime.datetime(2016, 1, 1)
    #in_end_date = datetime.datetime.now()
    #in_collections = "'Sentinel 2A';'Sentinel 2B'"
    #in_band_assets = "'Red';'NIR 1'"
    #in_mask_algorithm = 'S2Cloudless'  # 'fMask'  # FIXME: s2cloudless removes a lot of images... even at 50%!
    #in_quality_flags = "Valid"  # "'Valid';'Shadow';'Snow';'Water'"
    #in_max_out_of_bounds = 5
    #in_max_invalid_pixels = 5
    in_keep_mask = False
    #in_nodata_value = -999
    #in_srs = 'GDA94 Australia Albers (EPSG: 3577)'
    #in_res = 10
    #in_max_threads = None

    # region PREPARE PARAMETERS
    text_cb_fn('Preparing DEA STAC query parameters...')

    xs = [xy[0] for xy in in_poly]
    ys = [xy[1] for xy in in_poly]
    fc_bbox = [min(xs), min(ys), max(xs), max(ys)]

    fc_epsg = 4326

    start_date = '2016-01-01' #'2023-01-01' #'2016-01-01'
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')

    collections = ['ga_s2am_ard_3', 'ga_s2bm_ard_3']
    assets = ['red', 'nir_1']

    quality_flags = [1]
    mask_algorithm = 'oa_s2cloudless_mask'
    assets = assets + [mask_algorithm]

    max_out_of_bounds = 5.0
    max_invalid_pixels = 5.0

    out_nodata = -999
    out_epsg = 3577
    out_res = 10.0
    out_dtype = 'int16'

    # max_threads = shared.prepare_max_threads(in_max_threads)  # if user gave none, uses max cpus - 1
    max_threads = 8

    time.sleep(1)

    # endregion

    # region QUERY STAC ENDPOINT

    text_cb_fn('Querying DEA STAC endpoint...')

    try:
        stac_cb_fn(0)

        # reproject stac bbox to wgs 1984, fetch all available stac items
        stac_bbox = fc_bbox
        stac_features = stac.fetch_all_stac_feats(collections,
                                                  start_date,
                                                  end_date,
                                                  stac_bbox,
                                                  100)

        stac_cb_fn(100)

    except Exception as e:
        text_cb_fn('Error occurred during DEA STAC query. See messages.')
        text_cb_fn(str(e))
        raise  # return

    if len(stac_features) == 0:
        text_cb_fn('No STAC features were found.')
        raise  # return

    time.sleep(1)

    # endregion

    # region PREPARING STAC FEATURES

    text_cb_fn('Preparing STAC downloads...')

    root_folder = os.path.dirname(out_nc)
    tmp_folder = os.path.join(root_folder, 'tmp')

    if os.path.exists(tmp_folder):
        shutil.rmtree(tmp_folder)

    if not os.path.exists(tmp_folder):
        os.mkdir(tmp_folder)

    try:
        # TODO: needs rework for threading
        geom = shapely.Polygon(in_poly)
        poly = gpd.GeoDataFrame(index=[0], crs=f'epsg:{fc_epsg}', geometry=[geom])
        poly = poly.to_crs(f'epsg:{out_epsg}')
        out_bbox = list(poly.total_bounds)

        stac_downloads = stac.convert_stac_feats_to_stac_downloads(stac_features,
                                                                   assets,
                                                                   mask_algorithm,
                                                                   quality_flags,
                                                                   max_out_of_bounds,
                                                                   max_invalid_pixels,
                                                                   out_bbox,
                                                                   out_epsg,
                                                                   out_res,
                                                                   out_nodata,
                                                                   out_dtype,
                                                                   tmp_folder)

    except Exception as e:
        text_cb_fn('Error occurred during STAC download preparation.')
        text_cb_fn(str(e))
        raise

    stac_downloads = stac.group_stac_downloads_by_solar_day(stac_downloads)

    if len(stac_downloads) == 0:
        text_cb_fn('No valid downloads were found.')
        raise

    time.sleep(1)

    # endregion

    # region DOWNLOAD WCS MASK DATA

    text_cb_fn('\n' + 'Downloading and validating mask data...')

    try:
        mask_cb_fn(0)
        i = 0
        with ThreadPoolExecutor(max_workers=max_threads) as pool:
            futures = []
            for stac_download in stac_downloads:
                task = pool.submit(cube.worker_read_mask_and_validate, stac_download)
                futures.append(task)

            for future in as_completed(futures):
                msg = '-' + ' ' + future.result()
                text_cb_fn(msg)

                i += 1
                if i % 1 == 0:
                    mask_cb_fn((i / len(stac_downloads) * 100))

    except Exception as e:
        text_cb_fn('Error occurred while downloading and validating mask data.')
        text_cb_fn(str(e))
        raise

    stac_downloads = cube.remove_mask_invalid_downloads(stac_downloads)

    if len(stac_downloads) == 0:
        text_cb_fn('No valid downloads were found.')
        raise

    time.sleep(1)

    # endregion

    # region DOWNLOAD WCS VALID DATA

    text_cb_fn('\n' + 'Downloading valid data...')

    try:
        band_cb_fn(0)
        i = 0
        with ThreadPoolExecutor(max_workers=max_threads) as pool:
            futures = []
            for download in stac_downloads:
                task = pool.submit(cube.worker_read_bands_and_export, download)
                futures.append(task)

            for future in as_completed(futures):
                msg = '-' + ' ' + future.result()
                text_cb_fn(msg)

                i += 1
                if i % 1 == 0:
                    band_cb_fn((i / len(stac_downloads) * 100))

    except Exception as e:
        text_cb_fn('Error occurred while downloading valid data. See messages.')
        text_cb_fn(str(e))
        raise  # return

    time.sleep(1)

    # endregion

    # region CLEAN AND COMBINE NETCDFS

    text_cb_fn('\n' + 'Cleaning and combining NetCDFs...')

    try:
        ds = cube.fix_xr_meta_and_combine(stac_downloads)

    except Exception as e:
        text_cb_fn('Error occurred while cleaning and combining NetCDFs. See messages.')
        text_cb_fn(str(e))
        raise  # return

    time.sleep(1)

    # endregion

    # region MASK OUT INVALID NETCDF PIXELS

    text_cb_fn('Masking out invalid NetCDF pixels...')

    try:
        ds = cube.apply_xr_mask(ds,
                                quality_flags,
                                out_nodata,
                                in_keep_mask)

    except Exception as e:
        text_cb_fn('Error occurred while masking out invalid NetCDF pixels. See messages.')
        text_cb_fn(str(e))
        raise # return

    time.sleep(1)

    # endregion

    # region EXPORT COMBINED NETCDF

    text_cb_fn('Exporting combined NetCDF...')

    try:
        ds.load()
        cube.export_xr_to_nc(ds, out_nc)

    except Exception as e:
        text_cb_fn('Error occurred while exporting combined NetCDF. See messages.')
        text_cb_fn(str(e))
        raise # return

    time.sleep(1)

    # endregion

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # region CLEAN UP ENVIRONMENT

    text_cb_fn('Cleaning up environment...')

    cube.safe_close_ncs(tmp_folder)  # TODO: surely there is better way

    # shared.drop_temp_folder(tmp_folder)
    try:
        if os.path.exists(tmp_folder):
            shutil.rmtree(tmp_folder)
    except:
        pass

    time.sleep(1)

    text_cb_fn('\n' + 'Finished!')

    # endregion

    return ds
