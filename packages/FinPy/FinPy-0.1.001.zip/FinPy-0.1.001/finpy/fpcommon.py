"""
(c) 2013 Tsung-Han Yang
This source code is released under the Apache license.  
blacksburg98@yahoo.com
Created on April 1, 2013
"""
import datetime as dt
import fpdateutil as du
import numpy as np
import pandas as pd
def pre_timestamps(ldt_timestamps, window):
    """
    Return an list of timestamps.
    Start roughly from ldt_timestamps[0] - window.
    End at ldt_timestamps[0] - 1
    """
    dt_timeofday = dt.timedelta(hours=16)
    days_delta = dt.timedelta(days=(np.ceil(window*7/5)+20))
    dt_start = ldt_timestamps[0] - days_delta
    dt_end = ldt_timestamps[0] - dt.timedelta(days=1)
    pre_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday)
    return pre_timestamps 

def get_max_draw_down(ts_vals):
    """
    @summary Returns the max draw down of the returns.
    @param ts_vals: 1d numpy array or fund list
    @return Max draw down

    """
    MDD = 0
    DD = 0
    peak = -99999
    for value in ts_vals:
        if (value > peak):
            peak = value
        else:
            DD = (peak - value) / peak
        if (DD > MDD):
            MDD = DD
    return MDD/peak
