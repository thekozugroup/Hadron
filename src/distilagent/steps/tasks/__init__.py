# Copyright 2023-present, Argilla, Inc.
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

from distilagent.steps.tasks.apigen.execution_checker import APIGenExecutionChecker
from distilagent.steps.tasks.apigen.generator import APIGenGenerator
from distilagent.steps.tasks.apigen.semantic_checker import APIGenSemanticChecker
from distilagent.steps.tasks.argilla_labeller import ArgillaLabeller
from distilagent.steps.tasks.autoreason.task import AutoReasonedGeneration
from distilagent.steps.tasks.base import GeneratorTask, ImageTask, Task
from distilagent.steps.tasks.clair import CLAIR
from distilagent.steps.tasks.complexity_scorer import ComplexityScorer
from distilagent.steps.tasks.decorator import task
from distilagent.steps.tasks.evol_instruct.base import EvolInstruct
from distilagent.steps.tasks.evol_instruct.evol_complexity.base import EvolComplexity
from distilagent.steps.tasks.evol_instruct.evol_complexity.generator import (
    EvolComplexityGenerator,
)
from distilagent.steps.tasks.evol_instruct.generator import EvolInstructGenerator
from distilagent.steps.tasks.evol_quality.base import EvolQuality
from distilagent.steps.tasks.generate_embeddings import GenerateEmbeddings
from distilagent.steps.tasks.genstruct import Genstruct
from distilagent.steps.tasks.image_generation import ImageGeneration
from distilagent.steps.tasks.improving_text_embeddings import (
    BitextRetrievalGenerator,
    EmbeddingTaskGenerator,
    GenerateLongTextMatchingData,
    GenerateShortTextMatchingData,
    GenerateTextClassificationData,
    GenerateTextRetrievalData,
    MonolingualTripletGenerator,
)
from distilagent.steps.tasks.instruction_backtranslation import (
    InstructionBacktranslation,
)
from distilagent.steps.tasks.magpie.base import Magpie
from distilagent.steps.tasks.magpie.generator import MagpieGenerator
from distilagent.steps.tasks.math_shepherd.completer import MathShepherdCompleter
from distilagent.steps.tasks.math_shepherd.generator import MathShepherdGenerator
from distilagent.steps.tasks.math_shepherd.utils import FormatPRM
from distilagent.steps.tasks.pair_rm import PairRM
from distilagent.steps.tasks.prometheus_eval import PrometheusEval
from distilagent.steps.tasks.quality_scorer import QualityScorer
from distilagent.steps.tasks.self_instruct import SelfInstruct
from distilagent.steps.tasks.sentence_transformers import GenerateSentencePair
from distilagent.steps.tasks.structured_generation import StructuredGeneration
from distilagent.steps.tasks.text_classification import TextClassification
from distilagent.steps.tasks.text_generation import ChatGeneration, TextGeneration
from distilagent.steps.tasks.text_generation_with_image import TextGenerationWithImage
from distilagent.steps.tasks.ultrafeedback import UltraFeedback
from distilagent.steps.tasks.urial import URIAL
from distilagent.typing import ChatItem, ChatType

__all__ = [
    "CLAIR",
    "URIAL",
    "APIGenExecutionChecker",
    "APIGenGenerator",
    "APIGenSemanticChecker",
    "ArgillaLabeller",
    "ArgillaLabeller",
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
