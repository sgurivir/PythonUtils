#!/usr/bin/python -u
# -*- coding: utf-8 -*-

"""
Usage:

python3 setup.py install

python3 msl_postprocessing.py <memgraph on host>

# This will download a bunch of debug symbols... so grab a coffee.

"""

import sys
import logging
from perfcommon.util.msl_attribution import MSLAttribution, MSLAttributionJob

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


regex = MSLAttribution.prefix_class_regex(["CL", "CM", "RT", "SP", "GEO", "IDS", "MDM", "CK"])
MSLAttributionJob.run(
    None, [sys.argv[1]],
    filter_src=MSLAttribution.SUGGESTED_FILTER_SRC,
    preferred_src_attribution_order=['locationd', 'com.apple.'],
    replace_signature_regex=regex,
    filter_signature_regex=".*(CLDaemon|CLNotifier|CLSilo)",
    logger=logger
)
