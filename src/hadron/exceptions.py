# Copyright 2026-present, thekozugroup
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Tuple

class HadronException(Exception):
    """Base exception (can be gracefully handled) for `hadron` framework."""

    pass

class HadronGenerationException(HadronException):
    """Base exception for `LLM` generation errors."""

    pass

class HadronOfflineBatchGenerationNotFinishedException(
    HadronGenerationException
):
    """Exception raised when a batch generation is not finished."""

    jobs_ids: Tuple[str, ...]

    def __init__(self, jobs_ids: Tuple[str, ...]) -> None:
        self.jobs_ids = jobs_ids
        super().__init__(f"Batch generation with jobs_ids={jobs_ids} is not finished")
