#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST

import os
from setuptools import setup, find_packages, dist
dist.Distribution(dict(setup_requires='xbob.extension'))
from xbob.extension import Extension, build_ext

# Generates the MOC file required for Qt
def generate_mocs():
  from subprocess import Popen, PIPE

  p = Popen(['pkg-config', 'QtGui', '--variable=moc_location'], stdout=PIPE,
      stderr=PIPE)
  out, err = p.communicate()

  if p.returncode != 0:
    add_error = ""
    if err: add_error = ": `%s'" % err.strip()
    raise RuntimeError, "Could not find Qt's MOC compiler%s" % add_err

  moc = out.strip()

  basedir = ('xbob', 'daq', 'ext')
  filenames = ('QtDisplay',)
  retval = []

  for filename in filenames:
    input = os.sep.join(basedir + (filename + '.h',))
    src = os.sep.join(basedir + (filename + '.cc',))
    output = os.sep.join(basedir + ('MOC_' + filename + '.cc',))

    if not os.path.exists(output):
      p = Popen([moc, '-o'+output, input], stdout=PIPE, stderr=PIPE)
      out, err = p.communicate()

      if p.returncode != 0:
        raise RuntimeError, "Could not update MOC file `%s' -> `%s': `%s'" % \
            (input, output, err.strip())

    retval.extend([src, output])

  return retval

def v4l2_available():
  return os.path.exists('/usr/include/linux/videodev2.h')

def v4l2_sources():
  if v4l2_available():
    return ['xbob/daq/ext/V4LCamera.cc']
  else:
    return []

def v4l2_macros():
  if v4l2_available():
    return [('HAVE_V4L2', 1),]
  else:
    return []

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    name='xbob.daq',
    version='1.0.4',
    description='Data-Acquisition Extension for Bob-based Applications',
    url='http://pypi.python.org/pypi/xbob.daq',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    namespace_packages=[
      "xbob",
      ],

    setup_requires = [
      'xbob.extension'
      ],

    install_requires=[
      "setuptools",
      "bob >= 1.2.0a0",
    ],

    cmdclass = {
      'build_ext': build_ext,
      },

    ext_modules=[
      Extension("xbob.daq._daq",
        [
          "xbob/daq/ext/BobOutputWriter.cc",
          "xbob/daq/ext/Camera.cc",
          "xbob/daq/ext/CaptureSystem.cc",
          "xbob/daq/ext/ConsoleDisplay.cc",
          "xbob/daq/ext/Controller.cc",
          "xbob/daq/ext/Display.cc",
          "xbob/daq/ext/FaceLocalization.cc",
          "xbob/daq/ext/OpenCVFaceLocalization.cc",
          "xbob/daq/ext/OutputWriter.cc",
          "xbob/daq/ext/SimpleController.cc",
          "xbob/daq/ext/VideoReaderCamera.cc",
          "xbob/daq/ext/VisionerFaceLocalization.cc",
          "xbob/daq/ext/all.cc",
          "xbob/daq/ext/version.cc",
          "xbob/daq/ext/main.cc",
          ] + generate_mocs() + v4l2_sources(),
        pkgconfig = [
          'bob-io',
          'bob-visioner',
          'QtCore',
          'QtGui',
          'opencv',
          ],
        define_macros = [
          ('__STDC_CONSTANT_MACROS', None),
          ] + v4l2_macros(),
        extra_compile_args = [
          '-Wno-unused-function',
          ]
        ),
      ],

    entry_points={

      'console_scripts': [
        'daq_example.py = xbob.daq.example.capture:main',
        ],

      'bob.test': [
        'daq = xbob.daq.test.test_all:DaqTest',
        ],

      },

)
