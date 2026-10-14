# Catalogue coverage — 133 official LeetCode identities

80 additions; original 53 records preserved exactly. 10 verified executable fixtures;
123 catalogue-only. Official identity metadata was checked against LeetCode; this
does not verify numerical constraints, editorial summaries, or execution harnesses.

## Coverage by teaching family

| Family | Questions | Starter subpatterns |
| --- | ---: | ---: |
| Arrays & Hashing | 7 | 3 |
| Two Pointers | 10 | 3 |
| Sliding Window | 8 | 3 |
| Binary Search | 11 | 3 |
| Prefix Sum | 6 | 3 |
| Strings | 7 | 3 |
| Stacks & Queues | 9 | 3 |
| Linked Lists | 9 | 3 |
| Trees & BST | 14 | 3 |
| Graph Traversal | 12 | 4 |
| Dynamic Programming | 14 | 4 |
| Greedy & Intervals | 9 | 3 |
| Heaps & Priority Queues | 5 | 3 |
| Backtracking | 5 | 3 |
| Tries | 2 | 3 |
| Bit Manipulation | 5 | 3 |

50 starter lesson subpatterns group 133 problem-specific subpattern labels.
Existing labels and curated provenance were retained rather than renamed.

## Question-to-subpattern map

| Official question | Primary pattern | Subpattern | Status |
| --- | --- | --- | --- |
| [#1 — Two Sum](https://leetcode.com/problems/two-sum/) | Hash Table | One-Pass Complement Lookup | Catalogue only |
| [#2 — Add Two Numbers](https://leetcode.com/problems/add-two-numbers/) | Linked List | Digit carry propagation | Catalogue only |
| [#3 — Longest Substring Without Repeating Characters](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Sliding Window | Dynamic/Variable Window with Hash Map / Direct Lookup | Verified suite |
| [#11 — Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Two Pointers | Greedy Boundary Contraction | Catalogue only |
| [#14 — Longest Common Prefix](https://leetcode.com/problems/longest-common-prefix/) | String Matching | Vertical Scanning / Trie Simulation | Catalogue only |
| [#15 — 3Sum](https://leetcode.com/problems/3sum/) | Two Pointers | Sorting + 2-Pointer Collision with Duplicate Skipping | Catalogue only |
| [#19 — Remove Nth Node From End of List](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | Linked List | Fixed Gap Two Pointers | Catalogue only |
| [#20 — Valid Parentheses](https://leetcode.com/problems/valid-parentheses/) | Stacks & Queues | Balanced delimiters | Catalogue only |
| [#21 — Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | Linked List | Dummy Head Splicing | Catalogue only |
| [#22 — Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | Backtracking | Constrained State Construction (Open vs Close Balances) | Catalogue only |
| [#26 — Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Two Pointers | Read and write positions | Catalogue only |
| [#27 — Remove Element](https://leetcode.com/problems/remove-element/) | Two Pointers | In-place filtering | Catalogue only |
| [#28 — Find the Index of the First Occurrence in a String](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) | Strings | Substring matching | Catalogue only |
| [#33 — Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | Binary Search | Modified Binary Search on Sorted Half | Catalogue only |
| [#34 — Find First and Last Position of Element in Sorted Array](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) | Binary Search | First and last boundaries | Catalogue only |
| [#35 — Search Insert Position](https://leetcode.com/problems/search-insert-position/) | Binary Search | Insertion boundary | Catalogue only |
| [#39 — Combination Sum](https://leetcode.com/problems/combination-sum/) | Backtracking | Unbounded Choice with Pruning | Catalogue only |
| [#45 — Jump Game II](https://leetcode.com/problems/jump-game-ii/) | Greedy | Reachable frontier layers | Catalogue only |
| [#46 — Permutations](https://leetcode.com/problems/permutations/) | Backtracking | Permutation choices | Catalogue only |
| [#49 — Group Anagrams](https://leetcode.com/problems/group-anagrams/) | Arrays & Hashing | Canonical grouping key | Catalogue only |
| [#53 — Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | Dynamic Programming / Kadane | Contiguous Subarray Optimization (Local vs Global Best) | Verified suite |
| [#55 — Jump Game](https://leetcode.com/problems/jump-game/) | Greedy | Farthest reachable prefix | Catalogue only |
| [#56 — Merge Intervals](https://leetcode.com/problems/merge-intervals/) | Intervals | Sorting by Start Time & Merging Overlaps | Catalogue only |
| [#57 — Insert Interval](https://leetcode.com/problems/insert-interval/) | Intervals | Ordered insertion and merge | Catalogue only |
| [#62 — Unique Paths](https://leetcode.com/problems/unique-paths/) | Dynamic Programming | 2D Grid Path Accumulation | Catalogue only |
| [#63 — Unique Paths II](https://leetcode.com/problems/unique-paths-ii/) | Dynamic Programming | Grid obstacles | Catalogue only |
| [#69 — Sqrt(x)](https://leetcode.com/problems/sqrtx/) | Binary Search | Integer answer boundary | Catalogue only |
| [#70 — Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | Dynamic Programming | 1D Linear Recurrence (Fibonacci State) | Verified suite |
| [#74 — Search a 2D Matrix](https://leetcode.com/problems/search-a-2d-matrix/) | Binary Search | Flattened ordered matrix | Catalogue only |
| [#75 — Sort Colors](https://leetcode.com/problems/sort-colors/) | Two Pointers | Dutch National Flag (Three-Way Partition) | Catalogue only |
| [#76 — Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | Sliding Window | Variable Window with Multi-Frequency Matching | Catalogue only |
| [#78 — Subsets](https://leetcode.com/problems/subsets/) | Backtracking | Cascading Power Set / Pick vs Skip | Catalogue only |
| [#84 — Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Monotonic Stack | Previous & Next Smaller Element Boundaries | Catalogue only |
| [#88 — Merge Sorted Array](https://leetcode.com/problems/merge-sorted-array/) | Two Pointers | Backward merge | Catalogue only |
| [#90 — Subsets II](https://leetcode.com/problems/subsets-ii/) | Backtracking | Duplicate-aware subsets | Catalogue only |
| [#94 — Binary Tree Inorder Traversal](https://leetcode.com/problems/binary-tree-inorder-traversal/) | Tree | Inorder traversal | Catalogue only |
| [#98 — Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) | Binary Search Tree | Valid Range Invariant Propagation (min_val < node->val < max_val) | Catalogue only |
| [#100 — Same Tree](https://leetcode.com/problems/same-tree/) | Tree | Paired structural traversal | Catalogue only |
| [#101 — Symmetric Tree](https://leetcode.com/problems/symmetric-tree/) | Tree | Mirrored subtree comparison | Catalogue only |
| [#102 — Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) | Tree | Breadth-First Search (Queue with Level Sizing) | Catalogue only |
| [#104 — Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | Tree | Depth-First Search (Bottom-Up Return Value) | Verified suite |
| [#110 — Balanced Binary Tree](https://leetcode.com/problems/balanced-binary-tree/) | Tree | Postorder height balance | Catalogue only |
| [#112 — Path Sum](https://leetcode.com/problems/path-sum/) | Tree | Root-to-leaf accumulation | Catalogue only |
| [#121 — Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Greedy / One-Pass | Track Minimum Prefix | Verified suite |
| [#122 — Best Time to Buy and Sell Stock II](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) | Greedy | Positive successive gains | Catalogue only |
| [#125 — Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | Two Pointers | Opposite-Directional with Filtering | Verified suite |
| [#128 — Longest Consecutive Sequence](https://leetcode.com/problems/longest-consecutive-sequence/) | Arrays & Hashing | Sequence starts | Catalogue only |
| [#133 — Clone Graph](https://leetcode.com/problems/clone-graph/) | Graph | Graph Copying with Visited Node Hash Mapping (DFS/BFS) | Catalogue only |
| [#136 — Single Number](https://leetcode.com/problems/single-number/) | Bit Manipulation | XOR Involutive Cancellation (A ^ A = 0) | Catalogue only |
| [#139 — Word Break](https://leetcode.com/problems/word-break/) | Dynamic Programming | Prefix segmentation | Catalogue only |
| [#141 — Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | Linked List | Floyd's Tortoise and Hare (Fast & Slow) | Catalogue only |
| [#150 — Evaluate Reverse Polish Notation](https://leetcode.com/problems/evaluate-reverse-polish-notation/) | Stacks & Queues | Postfix evaluation | Catalogue only |
| [#152 — Maximum Product Subarray](https://leetcode.com/problems/maximum-product-subarray/) | Dynamic Programming | Minimum and maximum states | Catalogue only |
| [#153 — Find Minimum in Rotated Sorted Array](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | Binary Search | Rotated minimum | Catalogue only |
| [#155 — Min Stack](https://leetcode.com/problems/min-stack/) | Stacks & Queues | Minimum tracking | Catalogue only |
| [#160 — Intersection of Two Linked Lists](https://leetcode.com/problems/intersection-of-two-linked-lists/) | Linked List | Equalized path lengths | Catalogue only |
| [#162 — Find Peak Element](https://leetcode.com/problems/find-peak-element/) | Binary Search | Slope / Derivative Comparison | Catalogue only |
| [#167 — Two Sum II - Input Array Is Sorted](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Two Pointers | Opposite-Directional (Collision) | Verified suite |
| [#169 — Majority Element](https://leetcode.com/problems/majority-element/) | Arrays & Hashing | Majority voting | Catalogue only |
| [#190 — Reverse Bits](https://leetcode.com/problems/reverse-bits/) | Bit Manipulation | Bit reversal | Catalogue only |
| [#191 — Number of 1 Bits](https://leetcode.com/problems/number-of-1-bits/) | Bit Manipulation | Set-bit counting | Catalogue only |
| [#198 — House Robber](https://leetcode.com/problems/house-robber/) | Dynamic Programming | Take / Skip Decision | Catalogue only |
| [#200 — Number of Islands](https://leetcode.com/problems/number-of-islands/) | Graph | Grid Traversal (Connected Components via DFS/BFS) | Verified suite |
| [#203 — Remove Linked List Elements](https://leetcode.com/problems/remove-linked-list-elements/) | Linked List | Dummy-head removal | Catalogue only |
| [#205 — Isomorphic Strings](https://leetcode.com/problems/isomorphic-strings/) | Strings | Bidirectional character mapping | Catalogue only |
| [#206 — Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) | Linked List | In-Place Pointer Reversal (Iterative & Recursive) | Catalogue only |
| [#207 — Course Schedule](https://leetcode.com/problems/course-schedule/) | Graph | Cycle Detection in Directed Graph / Topological Sort (Kahn's) | Catalogue only |
| [#208 — Implement Trie (Prefix Tree)](https://leetcode.com/problems/implement-trie-prefix-tree/) | Trie | N-ary Prefix Tree Node Design | Catalogue only |
| [#209 — Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) | Sliding Window | Dynamic Window Minimization | Catalogue only |
| [#210 — Course Schedule II](https://leetcode.com/problems/course-schedule-ii/) | Graph | Topological ordering | Catalogue only |
| [#211 — Design Add and Search Words Data Structure](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | Trie | Wildcard prefix traversal | Catalogue only |
| [#213 — House Robber II](https://leetcode.com/problems/house-robber-ii/) | Dynamic Programming | Circular exclusion | Catalogue only |
| [#215 — Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Heap (Priority Queue) | Min-Heap of Size K (vs Quickselect) | Catalogue only |
| [#217 — Contains Duplicate](https://leetcode.com/problems/contains-duplicate/) | Arrays & Hashing | Membership set | Catalogue only |
| [#225 — Implement Stack using Queues](https://leetcode.com/problems/implement-stack-using-queues/) | Stacks & Queues | Queue rotation | Catalogue only |
| [#226 — Invert Binary Tree](https://leetcode.com/problems/invert-binary-tree/) | Tree | Recursive symmetry transform | Catalogue only |
| [#230 — Kth Smallest Element in a BST](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) | Binary Search Tree | Ordered rank traversal | Catalogue only |
| [#232 — Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | Stacks & Queues | Two-stack queue | Catalogue only |
| [#234 — Palindrome Linked List](https://leetcode.com/problems/palindrome-linked-list/) | Linked List | Half reversal comparison | Catalogue only |
| [#235 — Lowest Common Ancestor of a Binary Search Tree](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) | Binary Search Tree | BST Value Splitting Traversal | Catalogue only |
| [#238 — Product of Array Except Self](https://leetcode.com/problems/product-of-array-except-self/) | Arrays & Hashing | Prefix and suffix products | Catalogue only |
| [#242 — Valid Anagram](https://leetcode.com/problems/valid-anagram/) | Arrays & Hashing | Character frequency | Catalogue only |
| [#268 — Missing Number](https://leetcode.com/problems/missing-number/) | Bit Manipulation | XOR missing value | Catalogue only |
| [#283 — Move Zeroes](https://leetcode.com/problems/move-zeroes/) | Two Pointers | Stable compaction | Catalogue only |
| [#290 — Word Pattern](https://leetcode.com/problems/word-pattern/) | Strings | Symbol to word bijection | Catalogue only |
| [#300 — Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) | Dynamic Programming | Subsequence Extension & Patience Sorting (O(N^2) to O(N log N)) | Catalogue only |
| [#303 — Range Sum Query - Immutable](https://leetcode.com/problems/range-sum-query-immutable/) | Prefix Sum | Immutable range sum | Catalogue only |
| [#322 — Coin Change](https://leetcode.com/problems/coin-change/) | Dynamic Programming | Unbounded Knapsack (Minimization) | Catalogue only |
| [#338 — Counting Bits](https://leetcode.com/problems/counting-bits/) | Bit Manipulation | Bit-count recurrence | Catalogue only |
| [#344 — Reverse String](https://leetcode.com/problems/reverse-string/) | Strings | In-place reversal | Catalogue only |
| [#347 — Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | Heap (Priority Queue) | Frequency selection | Catalogue only |
| [#367 — Valid Perfect Square](https://leetcode.com/problems/valid-perfect-square/) | Binary Search | Exact integer predicate | Catalogue only |
| [#387 — First Unique Character in a String](https://leetcode.com/problems/first-unique-character-in-a-string/) | Strings | First unique character | Catalogue only |
| [#392 — Is Subsequence](https://leetcode.com/problems/is-subsequence/) | Strings | Subsequence scanning | Catalogue only |
| [#416 — Partition Equal Subset Sum](https://leetcode.com/problems/partition-equal-subset-sum/) | Dynamic Programming | Subset-sum reachability | Catalogue only |
| [#424 — Longest Repeating Character Replacement](https://leetcode.com/problems/longest-repeating-character-replacement/) | Sliding Window | Frequency budget | Catalogue only |
| [#435 — Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | Intervals | Greedy Interval Scheduling (Sort by End Time) | Catalogue only |
| [#438 — Find All Anagrams in a String](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | Sliding Window | Anagram window positions | Catalogue only |
| [#452 — Minimum Number of Arrows to Burst Balloons](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/) | Intervals | End-point greedy cover | Catalogue only |
| [#455 — Assign Cookies](https://leetcode.com/problems/assign-cookies/) | Greedy | Smallest sufficient resource | Catalogue only |
| [#496 — Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) | Monotonic Stack | Next Greater Element (Decreasing Stack) | Verified suite |
| [#503 — Next Greater Element II](https://leetcode.com/problems/next-greater-element-ii/) | Monotonic Stack | Circular next greater | Catalogue only |
| [#509 — Fibonacci Number](https://leetcode.com/problems/fibonacci-number/) | Dynamic Programming | Two-state recurrence | Catalogue only |
| [#523 — Continuous Subarray Sum](https://leetcode.com/problems/continuous-subarray-sum/) | Prefix Sum | Prefix remainder matching | Catalogue only |
| [#525 — Contiguous Array](https://leetcode.com/problems/contiguous-array/) | Prefix Sum | Balanced signed prefix | Catalogue only |
| [#542 — 01 Matrix](https://leetcode.com/problems/01-matrix/) | Graph | Multi-source distance | Catalogue only |
| [#543 — Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | Tree | Post-Order DFS with Global Maximum Tracking | Catalogue only |
| [#547 — Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | Graph | Adjacency Matrix Connected Components (DFS / DSU) | Catalogue only |
| [#560 — Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Prefix Sum | Prefix Sum Frequency Hashing | Catalogue only |
| [#567 — Permutation in String](https://leetcode.com/problems/permutation-in-string/) | Sliding Window | Fixed frequency window | Catalogue only |
| [#643 — Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) | Sliding Window | Fixed Window Size (k) | Catalogue only |
| [#695 — Max Area of Island](https://leetcode.com/problems/max-area-of-island/) | Graph | Component area | Catalogue only |
| [#700 — Search in a Binary Search Tree](https://leetcode.com/problems/search-in-a-binary-search-tree/) | Binary Search Tree | Ordered branch selection | Catalogue only |
| [#701 — Insert into a Binary Search Tree](https://leetcode.com/problems/insert-into-a-binary-search-tree/) | Binary Search Tree | Ordered insertion | Catalogue only |
| [#703 — Kth Largest Element in a Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | Heap (Priority Queue) | Streaming kth largest | Catalogue only |
| [#704 — Binary Search](https://leetcode.com/problems/binary-search/) | Binary Search | Exact Target Search | Verified suite |
| [#724 — Find Pivot Index](https://leetcode.com/problems/find-pivot-index/) | Prefix Sum | Running Left Sum vs Total Sum | Catalogue only |
| [#733 — Flood Fill](https://leetcode.com/problems/flood-fill/) | Graph | Flood fill | Catalogue only |
| [#739 — Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | Monotonic Stack | Next Greater Distance (Index Stack) | Catalogue only |
| [#743 — Network Delay Time](https://leetcode.com/problems/network-delay-time/) | Graph | Shortest Path (Dijkstra's with Min-Heap) | Catalogue only |
| [#746 — Min Cost Climbing Stairs](https://leetcode.com/problems/min-cost-climbing-stairs/) | Dynamic Programming | Minimum prefix cost | Catalogue only |
| [#785 — Is Graph Bipartite?](https://leetcode.com/problems/is-graph-bipartite/) | Graph | Two-color constraints | Catalogue only |
| [#875 — Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) | Binary Search | Binary Search on Answer Space (Monotonic Predicate) | Catalogue only |
| [#876 — Middle of the Linked List](https://leetcode.com/problems/middle-of-the-linked-list/) | Linked List | Fast and slow positions | Catalogue only |
| [#973 — K Closest Points to Origin](https://leetcode.com/problems/k-closest-points-to-origin/) | Heap (Priority Queue) | Distance selection | Catalogue only |
| [#977 — Squares of a Sorted Array](https://leetcode.com/problems/squares-of-a-sorted-array/) | Two Pointers | Extreme magnitudes | Catalogue only |
| [#994 — Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | Graph | Multi-Source Breadth-First Search (Level Sizing) | Catalogue only |
| [#1004 — Max Consecutive Ones III](https://leetcode.com/problems/max-consecutive-ones-iii/) | Sliding Window | Bounded zero budget | Catalogue only |
| [#1011 — Capacity To Ship Packages Within D Days](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) | Binary Search | Binary Search on Answer Space (Greedy Capacity) | Catalogue only |
| [#1046 — Last Stone Weight](https://leetcode.com/problems/last-stone-weight/) | Heap (Priority Queue) | Max-Heap Simulation | Catalogue only |
| [#1143 — Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) | Dynamic Programming | 2D String Grid DP (Match vs Mismatch) | Catalogue only |
| [#1480 — Running Sum of 1d Array](https://leetcode.com/problems/running-sum-of-1d-array/) | Prefix Sum | Running accumulation | Catalogue only |
| [#1971 — Find if Path Exists in Graph](https://leetcode.com/problems/find-if-path-exists-in-graph/) | Graph | Reachability | Catalogue only |
