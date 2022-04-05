#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
References to all the resources this module needs.

These include paths on the device, as well as files on the host.
"""

import os

# DIRECTORIES
# ----------------------------------------------
_DIR = os.path.abspath(os.path.dirname(__file__))

# SCRIPTS
# ----------------------------------------------
MSL_COLLECT = os.path.join(_DIR, 'msl_collect_ios')
HOST_LATENCY_DTRACE = os.path.join(_DIR, 'latency_stats.d')

# SCRIPT DEVICE PATHS
# -----------------------------------------------
DEV_LATENCY_DTRACE = '/var/root/latency_stats.d'
