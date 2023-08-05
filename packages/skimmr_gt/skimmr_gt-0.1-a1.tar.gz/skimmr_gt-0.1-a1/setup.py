from distutils.core import setup

setup(name='skimmr_gt',
      version='0.1-a1',
      description='SKIMMR library and scipts for machine-aided skim-reading (the general-purpose package version for arbitrary texts)',
      long_description=open('README','r').read(),
      author='Vit Novacek, DERI, NUIG',
      author_email='vit.novacek@deri.org',
      url='http://www.skimmr.org',
      license='BSD-new',
      download_url='https://dl.dropbox.com/u/21379226/software/skimmr_gt-0.1-a1.tar.gz',
      packages=['skimmr_gt'],
      scripts=['bin/crkb_gt.py','bin/exst_gt.py','bin/ixkb_gt.py',
      'bin/srvr_gt.py','bin/prep_gt.py'],
      package_dir={'skimmr_gt':'skimmr_gt'},
      package_data={'skimmr_gt':['data/*.png','data/*.tmp','data/style.css',
      'data/file_list.txt']},
      requires=['nltk (>=2.0)', 'whoosh', 'pydot', 'psutil'],
      classifiers=['Development Status :: 3 - Alpha','Environment :: Console','Environment :: Web Environment','Intended Audience :: Education','Intended Audience :: End Users/Desktop','Intended Audience :: Healthcare Industry','Intended Audience :: Information Technology','Intended Audience :: Science/Research','License :: OSI Approved :: BSD License','Operating System :: OS Independent','Topic :: Scientific/Engineering :: Artificial Intelligence','Topic :: Scientific/Engineering :: Information Analysis']
     )
