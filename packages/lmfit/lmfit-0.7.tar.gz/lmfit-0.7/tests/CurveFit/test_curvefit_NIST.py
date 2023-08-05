#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test curvefit from scipy.optimize 
with NIST data
"""

from NISTModels import ReadNistData, Models
from scipy.optimize import curve_fit

import numpy as np

def test_curvefit(DataSet, start):

    print('-*'*25)
    print(DataSet)   

    # Get the Model
    func, npar, dimx = Models[DataSet]
    # Get Data Set
    NISTdata = ReadNistData(DataSet)
    x = NISTdata['x']
    y = NISTdata['y']


    start_param = []
    cval = []
    cerr = []
    for count in range(npar):
        cval.append(NISTdata['cert_values'][count])
        cerr.append(NISTdata['cert_stderr'][count])
        pval1 = NISTdata[start][count]
        start_param.append(pval1)
    try:
        print 'start at - > ', start
        popt, pcov, infodict, errmsg, ier = curve_fit(func, x, y, p0=start_param, full_output=True)
    except RuntimeError as e:
        print(e)
    else:
        residual = infodict['fvec']
        chisqr = (residual**2).sum()
        ndata = len(residual)
        nvarys = len(popt)
        nfree = (ndata - nvarys)
        
        print('Optimized -- Certified')
        for el in zip(popt, cval):
            print( str(el[0]) + '   ' + str(el[1]))

        errors =  np.array(popt) - np.array(cval)
        rel_errors = errors / np.array(cval)
        print('Highest relative error: '),
        print(np.max(rel_errors)) 


if __name__ == '__main__':

    #Get names of dataset
    datasets = sorted(Models.keys())
    # Run test
    for dataset in datasets:
        start = 'start2' #start1 or start2...
        test_curvefit(dataset, start)
