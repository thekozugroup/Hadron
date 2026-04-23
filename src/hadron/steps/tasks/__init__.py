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

from hadron.steps.tasks.apigen.execution_checker import APIGenExecutionChecker
from hadron.steps.tasks.apigen.generator import APIGenGenerator
from hadron.steps.tasks.apigen.semantic_checker import APIGenSemanticChecker
from hadron.steps.tasks.autoreason.task import AutoReasonedGeneration
from hadron.steps.tasks.base import GeneratorTask, ImageTask, Task
from hadron.steps.tasks.clair import CLAIR
from hadron.steps.tasks.complexity_scorer import ComplexityScorer
from hadron.steps.tasks.decorator import task
from hadron.steps.tasks.evol_instruct.base import EvolInstruct
from hadron.steps.tasks.evol_instruct.evol_complexity.base import EvolComplexity
from hadron.steps.tasks.evol_instruct.evol_complexity.generator import (
    EvolComplexityGenerator,
)
from hadron.steps.tasks.evol_instruct.generator import EvolInstructGenerator
from hadron.steps.tasks.evol_quality.base import EvolQuality
from hadron.steps.tasks.generate_embeddings import GenerateEmbeddings
from hadron.steps.tasks.genstruct import Genstruct
from hadron.steps.tasks.image_generation import ImageGeneration
from hadron.steps.tasks.improving_text_embeddings import (
    BitextRetrievalGenerator,
    EmbeddingTaskGenerator,
    GenerateLongTextMatchingData,
    GenerateShortTextMatchingData,
    GenerateTextClassificationData,
    GenerateTextRetrievalData,
    MonolingualTripletGenerator,
)
from hadron.steps.tasks.instruction_backtranslation import (
    InstructionBacktranslation,
)
from hadron.steps.tasks.magpie.base import Magpie
from hadron.steps.tasks.magpie.generator import MagpieGenerator
from hadron.steps.tasks.math_shepherd.completer import MathShepherdCompleter
from hadron.steps.tasks.math_shepherd.generator import MathShepherdGenerator
from hadron.steps.tasks.math_shepherd.utils import FormatPRM
from hadron.steps.tasks.pair_rm import PairRM
from hadron.steps.tasks.prometheus_eval import PrometheusEval
from hadron.steps.tasks.quality_scorer import QualityScorer
from hadron.steps.tasks.self_instruct import SelfInstruct
from hadron.steps.tasks.sentence_transformers import GenerateSentencePair
from hadron.steps.tasks.structured_generation import StructuredGeneration
from hadron.steps.tasks.text_classification import TextClassification
from hadron.steps.tasks.text_generation import ChatGeneration, TextGeneration
from hadron.steps.tasks.text_generation_with_image import TextGenerationWithImage
from hadron.steps.tasks.ultrafeedback import UltraFeedback
from hadron.steps.tasks.urial import URIAL
from hadron.typing import ChatItem, ChatType

__all__ = [
    "CLAIR",
    "URIAL",
    "APIGenExecutionChecker",
    "APIGenGenerator",
    "APIGenSemanticChecker",
    "AutoReasonedGeneration",
    "BitextRetrievalGenerator",
    "ChatGeneration",
    "ChatItem",
    "ChatType",
    "ComplexityScorer",
    "EmbeddingTaskGenerator",
    "EvolComplexity",
    "EvolComplexityGenerator",
    "EvolInstruct",
    "EvolInstructGenerator",
    "EvolQuality",
    "FormatPRM",
    "GenerateEmbeddings",
    "GenerateLongTextMatchingData",
    "GenerateSentencePair",
    "GenerateShortTextMatchingData",
    "GenerateTextClassificationData",
    "GenerateTextRetrievalData",
    "GeneratorTask",
    "Genstruct",
    "ImageGeneration",
    "ImageTask",
    "InstructionBacktranslation",
    "Magpie",
    "MagpieGenerator",
    "MathShepherdCompleter",
    "MathShepherdGenerator",
    "MonolingualTripletGenerator",
    "MonolingualTripletGenerator",
    "PairRM",
    "PrometheusEval",
    "QualityScorer",
    "SelfInstruct",
    "StructuredGeneration",
    "Task",
    "Task",
    "TextClassification",
    "TextGeneration",
    "TextGenerationWithImage",
    "UltraFeedback",
    "task",
]
