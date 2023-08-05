# -*- coding: utf-8 -*-
"""pypel package, simple receipts management tool.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2012 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""

VERSION = (0, 1)

def get_version():
    """Returns project version in a human readable form."""
    return '.'.join(str(v) for v in VERSION)
