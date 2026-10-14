"""Stable identities; legacy slugs remain resolvable during non-destructive migration."""
LEGACY_IDS = {
    'two_sum_ii': 167, 'valid_palindrome': 125, 'maximum_subarray': 53,
    'binary_search': 704, 'buy_sell_stock': 121, 'max_depth_tree': 104,
    'num_islands': 200, 'climbing_stairs': 70,
    'longest_substring_no_repeats': 3, 'next_greater_element_i': 496,
}


def stable_id(leetcode_id: int) -> str:
    return f'lc_{leetcode_id}'
