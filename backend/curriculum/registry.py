"""Join curated metadata and executable fixtures using stable LeetCode IDs."""
from dataclasses import dataclass
from typing import Optional
from backend.curriculum.catalogue import CURATED_CATALOGUE
from backend.curriculum.models import CurriculumProblem
from backend.curriculum.identity import stable_id
from backend.eval.dataset import EVALUATION_DATASET, EvalProblem


@dataclass(frozen=True)
class RegisteredProblem:
    metadata: CurriculumProblem
    execution: Optional[EvalProblem]

    @property
    def id(self):
        return stable_id(self.metadata.leetcode_id)

    @property
    def is_executable(self):
        return self.execution is not None


def get_registry():
    fixtures = {p.leetcode_id: p for p in EVALUATION_DATASET}
    if len(fixtures) != len(EVALUATION_DATASET):
        raise ValueError('Duplicate executable problem identity')
    catalogue_ids = {p.leetcode_id for p in CURATED_CATALOGUE}
    if len(catalogue_ids) != len(CURATED_CATALOGUE) or fixtures.keys() - catalogue_ids:
        raise ValueError('Executable problems must join unique curated identities')
    return [RegisteredProblem(p, fixtures.get(p.leetcode_id)) for p in CURATED_CATALOGUE]
