"""Original editorial summaries. Unknown official constraints remain unavailable."""
import json
from pathlib import Path

SUMMARIES = {int(k): v for k, v in json.loads(
    Path(__file__).with_name('summaries.json').read_text(encoding='utf-8')).items()}
