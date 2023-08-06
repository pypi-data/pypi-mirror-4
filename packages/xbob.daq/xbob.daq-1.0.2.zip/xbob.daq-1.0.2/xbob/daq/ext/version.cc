/**
 * @file version.cc
 * @date Mon 06 Feb 2012 15:21:59 CET
 * @author Andre Anjos <andre.anjos@idiap.ch>
 *
 * @brief Describes ways to retrieve version information about all dependent
 * packages.
 *
 * Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, version 3 of the License.
 * 
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <boost/python.hpp>
#include <boost/format.hpp>

using namespace boost::python;

/**
 * OpenCV version
 */
static str opencv_version() {
#if defined(HAVE_OPENCV)
  return str(OPENCV_VERSION);
#else
  return str("unavailable");
#endif
}

/**
 * V4L2 (kernel) version
 */
static str v4l2_version() {
#if defined(HAVE_V4L2)
  return str("compiled-in");
#else
  return str("unavailable");
#endif
}

/**
 * Qt4 version
 */
static str qt4_version() {
#if defined(HAVE_QTCORE)
  return str(QTCORE_VERSION);
#else
  return str("unavailable");
#endif
}

/**
 * Bob version
 */
static str bob_version() {
#if defined(HAVE_BOB_PYTHON)
  return str(BOB_PYTHON_VERSION);
#else
  return str("unavailable");
#endif
}

void bind_daq_version() {
  dict vdict;
  vdict["OpenCV"] = opencv_version();
  vdict["Qt4"] = qt4_version();
  vdict["Bob"] = bob_version();
  vdict["V4L2"] = v4l2_version();
  scope().attr("dependencies") = vdict;
}
