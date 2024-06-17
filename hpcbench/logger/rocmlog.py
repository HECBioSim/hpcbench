#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 13:28:45 2024

@author: rob
"""

import argparse
import json
import subprocess
import time
from hpcbench.logger.util import GracefulKiller, exists, parse_smi
import sys
import os

