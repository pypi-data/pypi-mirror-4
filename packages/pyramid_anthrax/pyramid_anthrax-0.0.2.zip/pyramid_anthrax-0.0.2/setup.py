# vim set fileencoding=utf-8
from setuptools import setup

setup(
      name = 'pyramid_anthrax',
      version = '0.0.2',
      author = 'Szymon Pyżalski',
      author_email = 'zefciu <szymon@pythonista.net>',
      description =
        'Glue for using anthrax in pyramid projects',
      license = 'BSD',
      keywords = 'forms',
      
      install_requires = ['pyramid>=1.2', 'Anthrax>=0.0.3'],
      packages = ['pyramid_anthrax'],
      classifiers = [
          'Development Status :: 1 - Planning',
          'License :: OSI Approved :: BSD License',
          'Framework :: Pyramid',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
      ]
    
)
