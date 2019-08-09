# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utils for image pre-processing before inference."""

from PIL import ImageOps


def ResamplingWithOriginalRatio(img, required_size, sample):
  """Resamples the image with original ratio.

  Args:
    img: PIL image object.
    required_size: (width, height), required image size.
    sample: Resampling filter on image resizing.

  Returns:
    (image, ratio). image is a PIL image object with required_size. ratio is
    tuple of floats means the ratio between new image's size and required
    size.
  """
  old_size = img.size
  # Resizing image with original ratio.
  resampling_ratio = min(
      required_size[0] / old_size[0],
      required_size[1] / old_size[1]
  )
  new_size = (
      int(old_size[0] * resampling_ratio),
      int(old_size[1] * resampling_ratio)
  )
  new_img = img.resize(new_size, sample)
  # Expand it to required size.
  delta_w = required_size[0] - new_size[0]
  delta_h = required_size[1] - new_size[1]
  padding = (0, 0, delta_w, delta_h)
  ratio = (new_size[0] / required_size[0], new_size[1] / required_size[1])
  return (ImageOps.expand(new_img, padding), ratio)
