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

from distilagent.models.embeddings.base import Embeddings
from distilagent.models.embeddings.llamacpp import LlamaCppEmbeddings
from distilagent.models.embeddings.sentence_transformers import (
    SentenceTransformerEmbeddings,
)
from distilagent.models.embeddings.sglang import SGLangEmbeddings
from distilagent.models.embeddings.vllm import vLLMEmbeddings
from distilagent.models.image_generation.base import (
    AsyncImageGenerationModel,
    ImageGenerationModel,
)
from distilagent.models.image_generation.huggingface.inference_endpoints import (
    InferenceEndpointsImageGeneration,
)
from distilagent.models.image_generation.openai import OpenAIImageGeneration
from distilagent.models.llms.anthropic import AnthropicLLM
from distilagent.models.llms.anyscale import AnyscaleLLM
from distilagent.models.llms.azure import AzureOpenAILLM
from distilagent.models.llms.base import LLM, AsyncLLM
from distilagent.models.llms.cohere import CohereLLM
from distilagent.models.llms.groq import GroqLLM
from distilagent.models.llms.huggingface import InferenceEndpointsLLM, TransformersLLM
from distilagent.models.llms.litellm import LiteLLM
from distilagent.models.llms.llamacpp import LlamaCppLLM
from distilagent.models.llms.mistral import MistralLLM
from distilagent.models.llms.mlx import MlxLLM
from distilagent.models.llms.moa import MixtureOfAgentsLLM
from distilagent.models.llms.ollama import OllamaLLM
from distilagent.models.llms.openai import OpenAILLM
from distilagent.models.llms.openrouter import OpenRouterLLM
from distilagent.models.llms.sglang import ClientSGLang, SGLang
from distilagent.models.llms.together import TogetherLLM
from distilagent.models.llms.vertexai import VertexAILLM
from distilagent.models.llms.vllm import ClientvLLM, vLLM
from distilagent.models.mixins.cuda_device_placement import CudaDevicePlacementMixin
from distilagent.typing import GenerateOutput, HiddenState

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
