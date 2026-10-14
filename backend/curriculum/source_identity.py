"""Contract for future external sources; no invented LeetCode numbers."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class SourceIdentity(BaseModel):
    model_config = ConfigDict(extra='forbid')
    source: Literal['leetcode', 'local']
    source_id: str = Field(min_length=1, max_length=80)
    leetcode_id: int | None = Field(default=None, gt=0, strict=True)

    @model_validator(mode='after')
    def consistent(self):
        if self.source == 'leetcode':
            if self.leetcode_id is None or self.source_id != str(self.leetcode_id):
                raise ValueError('LeetCode identity must use its official numeric source ID')
        elif self.leetcode_id is not None:
            raise ValueError('A non-LeetCode source cannot assign a LeetCode number')
        return self
