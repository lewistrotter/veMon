
import datetime
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt

#from statsmodels.tsa.seasonal import STL as stl

def _build_harm_matrix(
        ts_rads: np.ndarray,  # doys as radians in array
        ns: int,  # num of sin harmonics (e.g., 2)
        nc: int   # num of cos harmonics (e.g., 2)
) -> np.ndarray:
    """
    Builds a design harmonic matrix based on Brooks et al. 2014 eq. 8.
    Should be in format [1, sin(1t), cosh(1t), sin(2t), cos(2t), ...]
    :param ts_rads: Numpy Array. DOYs as radians.
    :param ns: Int. Number of sin harmonics (e.g., 2)
    :param nc: Int. Number of cos harmonics (e.g., 2)
    :return: Numpy Array. Harmonic design matrix.
    """

    # count num of doys (as rads) in time series
    num_ts = len(ts_rads)

    # create column of constants = 1
    con = np.full(num_ts, 1)

    # create sin harmonic coefficient as columns
    mat_sin = np.full((num_ts, ns), np.arange(ns) + 1).T
    sin = np.sin(mat_sin * ts_rads).T

    # create cos harmonic coefficient as columns
    mat_cos = np.full((num_ts, nc), np.arange(nc) + 1).T
    cos = np.cos(mat_cos * ts_rads).T

    # combine all columns together
    X = np.column_stack([con, sin, cos])

    return X


def ewmacd_per_pixel(
        pix,
        ns,
        nc,
        history_bound,
        doys,
        years,
        training_start,
        training_end,
        testing_end,
        xbar_limit_1,
        xbar_limit_2,
        low_thresh,
        lam,
        lam_sigs,
        rounding,
        persistence
) -> None:

    # FIXME: lots of below can be simplified with xr

    dates = len(pix)  # Convenience object
    tmp = np.repeat(-2222, dates)  # Coded 'No data' output, fills the output as an initial value
    beta = np.repeat(np.nan, ns + nc + 1)  # coded other 'No data' output for the coefficients
    tmp_2 = -4  # backup value for pix
    pix_00 = pix.copy()  # backup value for myPixel

    ind_00 = np.arange(0, dates)  # Index list for original data
    pix_01 = pix[0:history_bound + 1]  # Training data (lt added + 1)
    pix_02 = pix[history_bound + 1: dates]  # Testing data

    bkgd_ind_00 = np.where(~np.isnan(pix_00))[0] # Index for all non-missing data
    pix_0 = pix[bkgd_ind_00] # 'Present' data (i.e any non nan
    dates_00 = len(pix_0)  # Convenience object for number of dates where not nan
    bkgd_ind_01 = np.where(~np.isnan(pix_00) & (ind_00 <= history_bound))[0]  # Index for non-missing training data
    history_bound_01 = len(bkgd_ind_01)  # Adjustment of training cutoff to reflect present data only

    pix_1 = pix_00[bkgd_ind_01]  # Present training data
    timedat_01 = doys[bkgd_ind_01]  # Present training dates, note the implicit dependence on DOYS
    timedat_1 = timedat_01 * 2 * np.pi / 365  # Conversion of training dates only to [0,2pi]
    timedat_all = doys[bkgd_ind_00] * 2 * np.pi / 365  # Conversion of all present dates to [0,2pi]

    # Checking if there is data to work with...
    if (len(pix_1) > 0):
        # build harm reg component matrix for train and all periods
        X = _build_harm_matrix(timedat_1, ns, nc)
        X_all = _build_harm_matrix(timedat_all, ns, nc)  # TODO: r script uses dates_00 and timedat_all, but redundant? check.

        # if design matrix is of sufficient rank and non-singular...
        if len(pix_1) > (ns + nc + 1) and np.abs(np.linalg.det(np.dot(X.T, X))) >= 0.001:
            # solve least-squares estimation equation and fit based on brooks et al., 2014 eq. 4
            # see how to do above via statsmodel here https://github.com/ChadFulton/sm-notebooks-2021/blob/main/002-seasonal-adjustment.ipynb
            fit = np.linalg.solve(np.dot(X.T, X), np.dot(X.T, pix_1))
            preds_1 = np.dot(X, fit)

            # Block for X-bar chart anomaly filtering
            # lt: this is done to remvoe extreme residual outliers (clouds) in training residuals
            resids_1 = pix_1 - preds_1
            std = np.std(resids_1, ddof=1)  # note: ddof 1 to match r
            screen_1 = np.abs(resids_1) > (xbar_limit_1 * std)
            keeps = np.where(~screen_1)[0]

            # recompute a new estimate of the harmonic coefficients excluding outliers
            if len(keeps) > ns + nc + 1:
                X_k, pix_k = X[keeps], pix_1[keeps]
                beta = np.linalg.solve(np.dot(X_k.T, X_k), np.dot(X_k.T, pix_k))

            # testing
            #plt.plot(pix_1, color='blue')
            #plt.plot(preds_1, color='red')
            #plt.show()

            #plt.plot(resids_1, color='purple')
            #plt.show()

        # ewma component
        if not np.isnan(beta[0]):  # Checking for present Beta
            y_0 = pix_0 - np.dot(X_all, beta).T  # Residuals for all present data, based on training coefficients
            y_01 = y_0[0:history_bound_01]  # Training residuals only

            # testing
            #plt.plot(pix_0, color='blue')
            #plt.plot(np.dot(X_all, beta).T, color='purple')
            #plt.plot(y_0, color='red')
            #plt.show()

            # Testing residuals
            y_02 = []
            if len(y_0) > len(y_01):  # TODO: lt: wouldnt full vector always be > training subset..?
                y_02 = y_0[history_bound_01:len(y_0)]

            mu = np.mean(y_01)  # First estimate of historical mean (should be near 0)
            histsd = np.std(y_01, ddof=1)  # First estimate of historical SD.
            ind_0 = np.arange(len(y_0))  # Index for residuals
            ind_01 = ind_0[0:history_bound_01]  # Index for training residuals

            # Index for testing residuals
            ind_02 = []
            if len(y_0 > len(y_01)):
                ind_02 = ind_0[history_bound_01:len(y_0)]

            # Creating date information in linear form (days from a starting point instead of Julian days of the year)
            ea_year = np.insert(np.repeat(365, len(np.arange(training_start, testing_end))) + 1 * (np.arange(training_start, testing_end) % 4 == 0), 0, 0)
            cu_year = np.cumsum(ea_year)
            x_0 = (cu_year[years - training_start] + doys)[bkgd_ind_00]

            # Modifying SD estimates based on anomalous readings in the training data
            ucl_0 = np.concatenate([np.repeat(xbar_limit_1, len(ind_01)), np.repeat(xbar_limit_2, len(ind_02))]) * histsd  # Note that we don't want to filter out the changes in the testing data, so xBarLimit2 is much larger!
            x = x_0[(pix_0 > low_thresh) & (np.abs(y_0) < ucl_0)]  # Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
            y = y_0[(pix_0 > low_thresh) & (np.abs(y_0) < ucl_0)]  # Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
            ind = ind_0[(pix_0 > low_thresh) & (np.abs(y_0) < ucl_0)]  # Keeping only dates for which we have some vegetation and aren't anomalously far from 0 in the residuals
            histsd = np.std(y_01[(pix_1 > low_thresh) & (np.abs(y_01) < ucl_0[0:history_bound_01])], ddof=1)  ### Updating the training SD estimate.  This is the all-important driver of the EWMA control limits.

            if np.isnan(histsd):
                #return tmp
                raise

            totals = np.zeros_like(y_0)  # Future EWMA output
            tmp_2 = np.repeat(-2222, len(y))  # Coded values for the 'present' subset of the data

            ewma = y[[0]]  # Initialize the EWMA outputs with the first present residual
            for i in np.arange(1, len(y)):
                ewma = np.append(ewma, ewma[i - 1] * (1 - lam) + lam * y[i])   # Appending new EWMA values for all present data.

            # TODO: check this - added the arange 1 to + 1
            ucl = histsd * lam_sigs * np.sqrt(lam / (2 - lam) * (1 - (1 - lam) ** (2 * np.arange(1, len(y) + 1))))  # EWMA upper control limit.  This is the threshold which dictates when the chart signals a disturbance.

            if rounding is True:
                tmp_2 = np.sign(ewma) * np.floor(np.abs(ewma / ucl))  # Integer value for EWMA output relative to control limit (rounded towards 0).  A value of +/-1 represents the weakest disturbance signal
            elif rounding is False:
                tmp_2 = np.round(ewma, 0)  # EWMA outputs in terms of resdiual scales.

            # testing
            # plt.plot(pix_0, color='black')
            # plt.plot(np.dot(X_all, beta).T, color='green')  # hreg pred on all
            # plt.plot(y_0, color='blue')
            # plt.plot(ewma, color='orange')
            # plt.plot(tmp_2, color='red')
            # plt.plot(ucl, color='purple')
            # plt.show()

            #  Keeping only values for which a disturbance is sustained, using persistence as the threshold
            if persistence > 1 and len(tmp_2) > 3:  # Ensuring sufficent data for tmp_2
                tmp_sign = np.sign(tmp_2)  # Disturbance direction
                shift_points = np.concatenate([[0], np.where(tmp_sign[1:] != tmp_sign[:len(tmp_sign) - 1])[0], [len(tmp_sign) - 1]])  # Dates for which direction changes

                tmp_3 = np.repeat(0, len(tmp_sign))
                for i in np.arange(0, len(tmp_sign)):  # Counting the consecutive dates in which directions are sustained
                    tmp_3_lo = 0
                    tmp_3_hi = 0

                    while(i - tmp_3_lo >= 0):  # TODO: added >=
                        if tmp_sign[i] - tmp_sign[(i - tmp_3_lo)] == 0:
                            tmp_3_lo += 1
                        else:
                            break

                    while(tmp_3_hi + i < len(tmp_sign)):  # TODO: was <=
                        if tmp_sign[(i + tmp_3_hi)] - tmp_sign[i] == 0:
                            tmp_3_hi += 1
                        else:
                            break

                    tmp_3[i] = tmp_3_lo + tmp_3_hi - 1

                tmp_4 = np.repeat(0, len(tmp_3))
                for i in np.arange(len(tmp_3)):  # If sustained dates are long enough, keep; otherwise set to previous sustained state
                    if tmp_3[i] >= persistence:
                        tmp_4[i] = tmp_2[i]
                    else:
                        w_ = np.where(tmp_3[0:i + 1] >= persistence)[0]
                        if len(w_) == 0:
                            tmp_4[i] = 0
                        else:
                            m_ = np.argmax(tmp_3[w_])  # TODO: this whole rejigg is a mess, find a way to do this via pd
                            v_=np.max(tmp_2[m_], 0)
                            tmp_4[i] = v_

                tmp_2 = tmp_4

            tmp[bkgd_ind_00[ind]] = tmp_2  # Assigning EWMA outputs for present data to the original template.  This still leaves -2222's everywhere the data was missing or filtered.

            if tmp[0] == -2222:  # If the first date of myPixel was missing/filtered, then assign the EWMA output as 0 (no disturbance).
                tmp[0] = 0

            if tmp[0] != -2222:  # If we have EWMA information for the first date, then for each missing/filtered date in the record, fill with the last known EWMA value
                for stepper in np.arange(1, dates):
                    if tmp[stepper] == -2222:
                        tmp[stepper] = tmp[stepper - 1]

            # testing
            #plt.plot(pix_0, color='black')
            #plt.plot(np.dot(X_all, beta).T, color='green')  # hreg pred on all
            #plt.plot(tmp * 1, color='purple', marker='.')
            #plt.plot(ucl * 1, color='yellow')
            #plt.plot(ucl * -1, color='yellow')
            #plt.title('lam = ' + str(lam))
            #plt.show()

    #return tmp # Final output.  All -2222's if data were insufficient to run the algorithm, otherwise an EWMA record of relative (rounded=T) or raw-residual (rounded=F) format.

    # lt added this
    _years = years[bkgd_ind_00]
    _doys = doys[bkgd_ind_00]

    dates = []
    for y, d in zip(_years, _doys):
        dt = datetime.datetime(int(y), 1, 1) + datetime.timedelta(int(d) - 1)
        dates.append(dt)

    return dates, pix_0, np.dot(X_all, beta).T, tmp  # pix_0


def ewmacd(
        ds,
        training_start=None,
        training_end=None,
        testing_end=None,
        number_harmonics=2,  # 2
        xbar_limit_1=1.5,
        xbar_limit_2=20,
        low_thresh=100,
        lam=0.3, #0.3,  # close to 1 = only recent values influence ewma, close to 0 historical influence ewma more
        lam_sigs=3,  # 3 # constant factor to modify ucl - low is tighter ucl range (a lot will be outliers), higher value is leniant ucl range (only most extreme will be outliers)
        rounding=True, # True # turning this off gets a more nuanced ewma line
        persistence=3,
        number_cpu=4,
        write_file=False,
        file_name=None
):
    ns = nc = number_harmonics

    # lt: subset dates via xr easier
    ds = ds.sel(time=ds['time'].dt.year >= training_start)
    ds = ds.sel(time=ds['time'].dt.year < testing_end)

    # extract arrays of doys and years in order of xr
    doys = ds['time'].dt.dayofyear.values
    years = ds['time'].dt.year.values

    # get index of last year in training period
    history_bound = np.max(np.where(years < training_end))

    # FIXME: working on only 1 pixel for now, adapt to whole netcdf
    #pix = ds['ndvi'].isel(x=0, y=0).values
    #pix = ds['ndvi'].median(['x', 'y']).values
    pix = ds['ndvi'].values

    # call per-pixel ewmacd func
    dates, ndvi_y, harm_y, resi_y = ewmacd_per_pixel(pix,
                                                     ns,
                                                     nc,
                                                     history_bound,
                                                     doys,
                                                     years,
                                                     training_start,
                                                     training_end,
                                                     testing_end,
                                                     xbar_limit_1,
                                                     xbar_limit_2,
                                                     low_thresh,
                                                     lam,
                                                     lam_sigs,
                                                     rounding,
                                                     persistence)


    # calc the per-pixel ewmacd func
    # tmpOutput = EWMACD.pixel.
    # for .calc.lt(myPixel, ns, nc, historybound, DOYs, xBarLimit1, trainingStart, testingEnd, Years, xBarLimit2,
    # lowthresh, lambda, lambdasigs, rounding, persistence, trainingEnd)

    #return tmp
    return dates, ndvi_y, harm_y, resi_y


if __name__ == '__main__':

    print('derp')

    # # load raw dates csv
    # date_info = pd.read_csv('./EWMACD v1.3.0/Temporal Distribution with DOY.csv')
    #
    # # unpack into xr friendly datetime64
    # dates = []
    # for i, row in date_info.iterrows():
    #     y, m, d = str(row['Year']), str(row['Month']), str(row['Day'])
    #     dt = np.datetime64(f"{y.zfill(4)}-{m.zfill(2)}-{d.zfill(2)}")
    #     dates.append(dt)
    #
    # # open raw tif
    # ds = xr.open_dataset('./EWMACD v1.3.0/Sample Data - Angle Index x1000 Stack.tif')
    #
    # # clean up xr dataset
    # ds = ds.rename({'band': 'time', 'band_data': 'ndvi'})
    # ds['time'] = dates

    # set all negative values to nan
    # TODO: only need this for non-neg indices
    #ds = ds.where(ds >= 0)

    # call ewmacd main func
    # ewmacd(ds=ds,
    #        training_start=2005,
    #        training_end=2008,
    #        testing_end=2012,
    #        number_cpu=1)

    # testing: load netcdf normal
    ds = xr.open_dataset(r"C:\Users\Lewis\Desktop\efreo ndvi all at once\ndvi.nc")
    ds = ds.isel(x=slice(100, 200), y=slice(100, 200))
    ds = ds.resample(time='M').median()
    ds = ds * 10000   # FIXME: decimal values not working when rounding=False, need to * 10000
    #ds = ds.median(['x', 'y'])
    #ds = ds.isel(x=2, y=2)

    vec = ewmacd(ds=ds,
                 training_start=2018,
                 training_end=2021,
                 testing_end=2024,
                 number_harmonics=2,
                 lam=0.3,
                 lam_sigs=3,
                 low_thresh=100,
                 rounding=True,
                 number_cpu=1)

    None