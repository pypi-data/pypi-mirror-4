from distutils.core import setup

setup(name='skimmr_bm',
      version='0.1-a1',
      description='SKIMMR library and scipts for machine-aided skim-reading (the specific package version for biomedical texts)',
      long_description=open('README','r').read(),
      author='Vit Novacek, DERI, NUIG',
      author_email='vit.novacek@deri.org',
      url='http://www.skimmr.org',
      license='BSD-new',
      download_url='https://dl.dropbox.com/u/21379226/software/skimmr_bm-0.1-a1.tar.gz',
      packages=['skimmr_bm'],
      scripts=['bin/crkb_bm.py','bin/exst_bm.py','bin/ixkb_bm.py',
      'bin/srvr_bm.py','bin/prep_bm.py','bin/dwnl_bm.py'],
      package_dir={'skimmr_bm':'skimmr_bm'},
      package_data={'skimmr_bm':['data/*.png','data/*.tmp','data/style.css',
      'data/file_list.txt']},
      requires=['nltk (>=2.0)', 'whoosh', 'pydot', 'psutil', 'Bio'],
      classifiers=['Development Status :: 3 - Alpha','Environment :: Console','Environment :: Web Environment','Intended Audience :: Education','Intended Audience :: End Users/Desktop','Intended Audience :: Healthcare Industry','Intended Audience :: Information Technology','Intended Audience :: Science/Research','License :: OSI Approved :: BSD License','Operating System :: OS Independent','Topic :: Scientific/Engineering :: Artificial Intelligence','Topic :: Scientific/Engineering :: Information Analysis','Topic :: Scientific/Engineering :: Bio-Informatics','Intended Audience :: Healthcare Industry']
     )
