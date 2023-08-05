# -*- coding: utf-8 -*-
## Copyright (C) 2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: config.py 52689 2007-10-30 14:42:22Z glenfant $
"""
Global customizable configuration data

To customize the values add this to your zope.conf:

<product-config ploneglossary>
  charset iso-8859-15 # Or any valid charset
  batch-size 50       # Any positive integer
</product-config>
"""

__author__ = 'Gilles Lenfant <gilles.lenfant@ingeniweb.com>'
__docformat__ = 'restructuredtext'

SITE_CHARSET = None  # Default: UTF-8
BATCH_SIZE = None  # Default: 30


def readZopeConf():
    """Read custom config from zope.conf or use defaults
    """
    global SITE_CHARSET, BATCH_SIZE
    from App.config import getConfiguration
    import codecs
    default_config = {
        'charset': 'UTF-8',
        'batch-size': 30
        }
    try:
        pg_config = getConfiguration().product_config['ploneglossary']
    except (KeyError, AttributeError):
        pg_config = default_config

    getConfData = lambda key: pg_config.get(key, default_config[key])

    SITE_CHARSET = getConfData('charset')
    BATCH_SIZE = int(getConfData('batch-size'))

    # Validating
    try:
        codecs.lookup(SITE_CHARSET)
    except LookupError:
        raise ValueError("%s is not a valid charset." % SITE_CHARSET)
    return

readZopeConf()
del readZopeConf
