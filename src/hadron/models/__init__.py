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

from hadron.models.embeddings.base import Embeddings
from hadron.models.embeddings.llamacpp import LlamaCppEmbeddings
from hadron.models.embeddings.sentence_transformers import (
    SentenceTransformerEmbeddings,
)
from hadron.models.embeddings.sglang import SGLangEmbeddings
from hadron.models.embeddings.vllm import vLLMEmbeddings
from hadron.models.image_generation.base import (
    AsyncImageGenerationModel,
    ImageGenerationModel,
)
from hadron.models.image_generation.huggingface.inference_endpoints import (
    InferenceEndpointsImageGeneration,
)
from hadron.models.image_generation.openai import OpenAIImageGeneration
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
from hadron.models.llms.openrouter import OpenRouterLLM
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
    "AsyncImageGenerationModel",
    "AsyncLLM",
    "AzureOpenAILLM",
    "ClientSGLang",
    "ClientvLLM",
    "CohereLLM",
    "CudaDevicePlacementMixin",
    "Embeddings",
    "GenerateOutput",
    "GroqLLM",
    "HiddenState",
    "ImageGenerationModel",
    "InferenceEndpointsImageGeneration",
    "InferenceEndpointsLLM",
    "LiteLLM",
    "LlamaCppEmbeddings",
    "LlamaCppLLM",
    "MistralLLM",
    "MixtureOfAgentsLLM",
    "MlxLLM",
    "OllamaLLM",
    "OpenAIImageGeneration",
    "OpenAILLM",
    "OpenRouterLLM",
    "SGLang",
    "SGLangEmbeddings",
    "SentenceTransformerEmbeddings",
    "TogetherLLM",
    "TransformersLLM",
    "VertexAILLM",
    "vLLM",
    "vLLMEmbeddings",
]
