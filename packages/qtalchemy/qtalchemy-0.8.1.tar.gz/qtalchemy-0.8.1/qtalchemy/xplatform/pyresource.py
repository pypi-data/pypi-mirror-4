# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################
"""
This module contains a python zip file extractor that works with py2exe.

It is not perfect, but it is a proof-of-concept that I'd rather not lose.
"""

from pkg_resources import resource_stream

resource_temp_dir = None

# http://old.nabble.com/resource_filename%28%29-breaks-cxfreeze-%28py2exe-%29-td1104344.html
# this is the motivation for the following function
def resource_to_tempfile(module, resource):
    """
    Read a pkg_resources stream and dump it to a temp file.
    Return the file name of the new temp file.

    TODO:  get smart about cacheing files and temp dir management!
    """
    import tempfile
    import os
    global resource_temp_dir

    if resource_temp_dir is None:
        resource_temp_dir = tempfile.mkdtemp()
    #print temp_dir,module,resource
    file_name = os.path.join(resource_temp_dir,module,resource)
    if not os.path.exists(file_name):
        my_stream = resource_stream(module,resource)
        if not os.path.exists(os.path.join(resource_temp_dir,module)):
            os.mkdir(os.path.join(resource_temp_dir,module))
        f = open(file_name,"wb")
        f.write(my_stream.read())
        f.close()
    return file_name
