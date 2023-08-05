'''
=============
Kalman Module
=============

This module provides inference methods for state-space estimation in continuous
spaces.
'''

from .standard import KalmanFilter
from .unscented import AdditiveUnscentedKalmanFilter, UnscentedKalmanFilter
import datasets
import sqrt
