#-*- coding: iso-8859-1 -*-

# Extracted from sqlite3.dbapi2 (see comment after copyright notice)

# pysqlite2/dbapi2.py: the DB-API 2.0 interface
#
# Copyright (C) 2004-2005 Gerhard Häring <gh@ghaering.de>
#
# This file is part of pysqlite.
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.
#
# GR: copied and altered version to re-register original datetime,
# most of the code is for the converter and needed not to be duplicated
# due to the fact that original converters/adapters are not importable.
# (check "cleanup namespace" comment)
# the original code can be found under sqlite3/ in the main python lib

from mock_dt import original_datetime

from _sqlite3 import register_adapter


def adapt_datetime(val):
    return val.isoformat(" ")

register_adapter(original_datetime, adapt_datetime)
