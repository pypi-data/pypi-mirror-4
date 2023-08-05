# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@axiastudio.it>
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#

from os.path import join, split
import sys
from setuptools import setup, find_packages

sys.path.insert(0, join(split(__file__)[0], 'lib'))
from alfREST import __version__

setup(name = "alfREST",
      version = __version__,
      description = "Alfresco REST web services client library for python",
      author = "Tiziano Lattisi",
      author_email = "tiziano@axiastudio.it",
      license = "GPL",
      url = "http://www.axiastudio.it/",
      keywords = ["python", "alfresco", "REST", "RESTful"],

      long_description = """\
Alfresco REST web services client library for python
----------------------------------------------------

A ligthweight python library based on the Alfresco RESTful web services.
""",

      packages = find_packages('lib'),
      package_dir = { '': 'lib' },

      scripts = ["alfRESTtest.py"],

      install_requires = [],

      package_data = {},

      zip_safe = False,

)
