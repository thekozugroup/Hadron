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

from typing import Optional

from distilagent.constants import DISTILAGENT_DOCS_URL

# The sitemap can be visited for the full list of pages:
# SITEMAP_URL: Final[str] = ""

class DistilAgentError:
    """A mixin class for common functionality shared by all DistilAgent-specific errors.

    Attributes:
        message: A message describing the error.
        page: An optional error code from PydanticErrorCodes enum.

    Examples:
        ```python
        raise DistilAgentUserError("This is an error message.")
        This is an error message.

        raise DistilAgentUserError("This is an error message.", page="sections/getting_started/faq/")
        This is an error message.
        For further information visit ''
        ```
    """

    def __init__(self, message: str, *, page: Optional[str] = None) -> None:
        self.message = message
        self.page = page

    def __str__(self) -> str:
        if self.page is None:
            return self.message
        else:
            return f"{self.message}\n\nFor further information visit '{DISTILAGENT_DOCS_URL}{self.page}'"

class DistilAgentUserError(DistilAgentError, ValueError):
    """ValueError that we can redirect to a given page in the documentation."""

    pass

class DistilAgentTypeError(DistilAgentError, TypeError):
    """TypeError that we can redirect to a given page in the documentation."""

    pass

class DistilAgentNotImplementedError(DistilAgentError, NotImplementedError):
    """NotImplementedError that we can redirect to a given page in the documentation."""

    pass
