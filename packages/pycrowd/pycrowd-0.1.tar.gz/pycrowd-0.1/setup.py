from distutils.core import setup

setup(name='pycrowd',
      version='0.1',
      description='Python Crowdsourcing',
      author='Bryan Marty',
      author_email='bxm156@case.edu',
      url='http://pycrowd.bryanmarty.com',
      packages=['pycrowd','pycrowd.cs_evaluator','pycrowd.cs_executor','pycrowd.cs_hits','pycrowd.cs_jobs',
          'pycrowd.cs_prediction','pycrowd.cs_query','pycrowd.cs_workers'],
      classifiers=[
          #Status
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Programming Language :: Python',
          ],
     )
