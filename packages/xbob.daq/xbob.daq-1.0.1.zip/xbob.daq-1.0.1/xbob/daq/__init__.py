from bob.core import __from_extension_import__
__from_extension_import__('._daq', __package__, locals())
from bob.visioner import DEFAULT_DETECTION_MODEL

# Replace constructors with good defaults
CaptureSystem._old_init = CaptureSystem.__init__
def _CaptureSystem__init__(self, camera, model = DEFAULT_DETECTION_MODEL):
  self._old_init(camera, model)
CaptureSystem.__init__ = _CaptureSystem__init__
del _CaptureSystem__init__

VisionerFaceLocalization._old_init = VisionerFaceLocalization.__init__
def _VisionerFaceLocalization__init__(self, model = DEFAULT_DETECTION_MODEL):
  self._old_init(model)
VisionerFaceLocalization.__init__ = _VisionerFaceLocalization__init__
del _VisionerFaceLocalization__init__

# Access to header files
def get_includes():
  """Returns a list of directories where the header files are"""
  import os
  from pkg_resources import resource_filename
  return [os.path.realpath(resource_filename(__name__, os.path.join('ext'))),]

__all__ = [k for k in dir() if not k.startswith('_')]
