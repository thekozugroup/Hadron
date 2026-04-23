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

# ruff: noqa: E402

import warnings

deprecation_message = (
    "Importing from 'hadron.llms' is deprecated and will be removed in a version 1.7.0. "
    "Import from 'hadron.models' instead."
)

warnings.warn(deprecation_message, DeprecationWarning, stacklevel=2)

from hadron.models.llms.anthropic import AnthropicLLM
from hadron.models.llms.anyscale import AnyscaleLLM
from hadron.models.llms.azure import AzureOpenAILLM
from hadron.models.llms.base import LLM, AsyncLLM
from hadron.models.llms.cohere import CohereLLM
from hadron.models.llms.groq import GroqLLM
from hadron.models.llms.huggingface import InferenceEndpointsLLM, TransformersLLM
from hadron.models.llms.litellm import LiteLLM
from hadron.models.llms.llamacpp import LlamaCppLLM
from hadron.models.llms.mistral import MistralLLM
from hadron.models.llms.mlx import MlxLLM
from hadron.models.llms.moa import MixtureOfAgentsLLM
from hadron.models.llms.ollama import OllamaLLM
from hadron.models.llms.openai import OpenAILLM
from hadron.models.llms.sglang import ClientSGLang, SGLang
from hadron.models.llms.together import TogetherLLM
from hadron.models.llms.vertexai import VertexAILLM
from hadron.models.llms.vllm import ClientvLLM, vLLM
from hadron.models.mixins.cuda_device_placement import CudaDevicePlacementMixin
from hadron.typing import GenerateOutput, HiddenState

__all__ = [
    "LLM",
    "AnthropicLLM",
    "AnyscaleLLM",
    "AsyncLLM",
    "AzureOpenAILLM",
    "ClientSGLang",
    "ClientvLLM",
    "CohereLLM",
    "CudaDevicePlacementMixin",
    "GenerateOutput",
    "GroqLLM",
    "HiddenState",
    "InferenceEndpointsLLM",
    "LiteLLM",
    "LlamaCppLLM",
    "MistralLLM",
    "MixtureOfAgentsLLM",
    "MlxLLM",
    "OllamaLLM",
    "OpenAILLM",
    "SGLang",
    "TogetherLLM",
    "TransformersLLM",
    "VertexAILLM",
    "vLLM",
]
