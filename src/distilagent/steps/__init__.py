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

from distilagent.steps.argilla.preference import PreferenceToArgilla
from distilagent.steps.argilla.text_generation import TextGenerationToArgilla
from distilagent.steps.base import (
    GeneratorStep,
    GlobalStep,
    Step,
    StepInput,
    StepResources,
)
from distilagent.steps.checkpointer import HuggingFaceHubCheckpointer
from distilagent.steps.clustering.dbscan import DBSCAN
from distilagent.steps.clustering.text_clustering import TextClustering
from distilagent.steps.clustering.umap import UMAP
from distilagent.steps.columns.combine import CombineOutputs
from distilagent.steps.columns.expand import ExpandColumns
from distilagent.steps.columns.group import GroupColumns
from distilagent.steps.columns.keep import KeepColumns
from distilagent.steps.columns.merge import MergeColumns
from distilagent.steps.decorator import step
from distilagent.steps.deita import DeitaFiltering
from distilagent.steps.embeddings.embedding_generation import EmbeddingGeneration
from distilagent.steps.embeddings.nearest_neighbour import FaissNearestNeighbour
from distilagent.steps.filtering.embedding import EmbeddingDedup
from distilagent.steps.filtering.minhash import MinHashDedup
from distilagent.steps.formatting.conversation import ConversationTemplate
from distilagent.steps.formatting.dpo import (
    FormatChatGenerationDPO,
    FormatTextGenerationDPO,
)
from distilagent.steps.formatting.sft import (
    FormatChatGenerationSFT,
    FormatTextGenerationSFT,
)
from distilagent.steps.generators.data import LoadDataFromDicts
from distilagent.steps.generators.data_sampler import DataSampler
from distilagent.steps.generators.huggingface import (
    LoadDataFromDisk,
    LoadDataFromFileSystem,
    LoadDataFromHub,
)
from distilagent.steps.generators.utils import make_generator_step
from distilagent.steps.globals.huggingface import PushToHub
from distilagent.steps.reward_model import RewardModelScore
from distilagent.steps.truncate import TruncateTextColumn
from distilagent.typing import GeneratorStepOutput, StepOutput

__all__ = [
    "DBSCAN",
    "UMAP",
    "CombineOutputs",
    "ConversationTemplate",
    "DataSampler",
    "DeitaFiltering",
    "EmbeddingDedup",
    "EmbeddingGeneration",
    "ExpandColumns",
    "FaissNearestNeighbour",
    "FormatChatGenerationDPO",
    "FormatChatGenerationSFT",
    "FormatTextGenerationDPO",
    "FormatTextGenerationSFT",
    "GeneratorStep",
    "GeneratorStepOutput",
    "GlobalStep",
    "GroupColumns",
    "HuggingFaceHubCheckpointer",
    "KeepColumns",
    "LoadDataFromDicts",
    "LoadDataFromDisk",
    "LoadDataFromFileSystem",
    "LoadDataFromHub",
    "MergeColumns",
    "MinHashDedup",
    "PreferenceToArgilla",
    "PushToHub",
    "RewardModelScore",
    "Step",
    "StepInput",
    "StepOutput",
    "StepResources",
    "TextClustering",
    "TextGenerationToArgilla",
    "TruncateTextColumn",
    "make_generator_step",
    "step",
]
