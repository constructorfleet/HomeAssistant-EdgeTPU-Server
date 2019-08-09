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

"""Python wrapper for ImprintingEngine."""

import edgetpu.swig.edgetpu_cpp_wrapper


class ImprintingEngine(edgetpu.swig.edgetpu_cpp_wrapper.ImprintingEngine):
  """Python wrapper for Imprinting Engine."""

  def TrainAll(self, input_data):
    """Trains model given input of all categories.

    Args:
      input_data: {string : list of numpy.array}, map between new
        category's label and training data.

    Returns:
      map between output id and label {int, string}.
    """
    ret = {}
    for category, tensors in input_data.items():
      ret[self.Train(tensors)] = category
    return ret
