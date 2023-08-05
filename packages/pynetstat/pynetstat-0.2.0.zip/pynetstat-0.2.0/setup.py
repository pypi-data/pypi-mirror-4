"""python module parse netstat command output into list of namedtuple:inet_connection

 see the in souce docstring(in pynetstat.py) for more detailed help and example
 http://www.iesensor.com/blog/2012/12/11/pynetstat/
"""

classifiers = """
Development Status :: 4 - Beta
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Environment :: Console
Intended Audience :: System Administrators
Topic :: Software Development :: Libraries :: Python Modules
Topic :: System :: Networking :: Monitoring
Operating System :: POSIX
Operating System :: Microsoft
"""

from setuptools import setup    #more powerful than standard module  distutils
#from distutils.core import setup

doclines = __doc__.split("\n")

setup(name="pynetstat",
      version="0.2.0",
      maintainer="Qingfeng Xia",
      maintainer_email="Qingfeng.Xia[]gmail.com",
      url = "http://www.iesensor.com/blog/2012/12/11/pynetstat/",
      license = "BSD",
      platforms = ["any"],
      #data_files=[  ('path', ['filelist'])]# file other than *.py
      description = doclines[0],
      classifiers = filter(None, classifiers.split("\n")),
      long_description = "\n".join(doclines[2:]),
      )