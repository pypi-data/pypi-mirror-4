# -*- coding: utf-8 -*-
from setuptools import setup,Extension
import sys
sys.path.append('./src')
sys.path.append('./test')
version = file('VERSION').read().strip()

setup(name='pyccv',
      version=version,
      description="Calculate color coherence vector for similar image search",
      long_description=file('README').read(),
      classifiers=[],
      keywords=('image-processing computer-vision'),
      author='Shunsuke Aihara',
      author_email='s.aihara@gmail.com',
      url='http://www.bitbucket.org/aihara/pyccv',
      license='MIT License',
      package_dir={'': 'src'},
      packages=['pyccv'],
      ext_modules=[
          Extension(
              'pyccv._ccv', [
                  'ccv/ccv.cpp',
              ],
              include_dirs=['ccv'],
              extra_compile_args=[],
          ),
      ],
      install_requires=["numpy","PIL"],
      test_suite = 'test_ccv.suite'
      )
