#from distutils.core import setup
from setuptools import setup
setup(name='Colonyzer2',
      version='1.0.51',
      description='Image analysis for microbial cultures growing on solid agar surfaces',
      long_description=open('README.txt').read(),
      entry_points={"console_scripts":["AnalyzeIndependent=AnalyzeIndependent.main:main","AnalyzeTimecourse=AnalyzeTimecourse.main:main"]},
      author='Conor Lawless',
      author_email='conor.lawless@ncl.ac.uk',
      url='http://research.ncl.ac.uk/colonyzer/',
      py_modules=['colonyzer2'],
      scripts=['bin/AnalyzeIndependent.py','bin/AnalyzeTimecourse.py'],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Intended Audience :: Science/Research'
        ]      
      )
