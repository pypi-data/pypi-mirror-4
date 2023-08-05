#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Mon Dec 10 14:29:51 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""This is the Bob database entry for the CAS-PEAL database.
  The database itself can be downloaded from http://www.jdl.ac.cn/peal/index.html, and the data is not provided in this interface.

  The CAS-PEAL database consists of several ten thousand images of Chinese people (CAS = Chinese Academy of Science).
  Overall, there are 1040 identities contained in the database.
  For these identities, images with different `P`ose, `E`xpression, `A`ging and `L`ighting (PEAL) conditions, as well as accessories, image backgrounds and camera distances are provided.

  Included in the database, there are file lists defining identification experiments.
  All the experiments rely on a gallery that consists of the frontal and frontally illuminated images with neutral expression and no accessories.
  For each of the variations, probe sets including exactly that variation are available.

  The training set consists of a subset of the frontal images (some images are both in the training and in the development set).
  This also means that there is no training set defined for the pose images.
  Additionally, the database defines only a development set, but no test set.
"""

from .query import Database

__all__ = ['Database']
