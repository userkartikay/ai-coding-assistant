"""Read-only verification; never renumber, replace metadata, or touch learner data."""
import httpx
from backend.curriculum.catalogue import CURATED_CATALOGUE

def main():
    response = httpx.get('https://leetcode.com/api/problems/all/', timeout=40)
    response.raise_for_status()
    official = {x['stat']['frontend_question_id']: x for x in response.json()['stat_status_pairs']}
    assert len({p.leetcode_id for p in CURATED_CATALOGUE}) == len(CURATED_CATALOGUE)
    for p in CURATED_CATALOGUE:
        raw = official[p.leetcode_id]
        stat = raw['stat']
        assert p.title == stat['question__title'], p.leetcode_id
        assert p.official_link == f"https://leetcode.com/problems/{stat['question__title_slug']}/", p.leetcode_id
        assert p.difficulty.value == {1:'Easy',2:'Medium',3:'Hard'}[raw['difficulty']['level']], p.leetcode_id
    print(f'Verified {len(CURATED_CATALOGUE)} official number/title/URL/difficulty mappings.')

if __name__ == '__main__': main()
