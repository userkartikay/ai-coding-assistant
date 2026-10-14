# Curated DSA Placement Curriculum & LeetCode Repository Review

**Document Version**: 1.0\
**Target Goal**: Software Engineering Placement Preparation (Service-Based Company Top Tiers: TCS Digital/Prime, Infosys SP/DSE, Cognizant GenC Next; and Transition to Product Company Rounds).\
**Repository Inspected**: [userkartikay/leetcode-solutions](https://github.com/userkartikay/leetcode-solutions)\

---

## 1. Review of Existing LeetCode Solutions Repository

We manually inspected the commit history, directory structure, and categorized problem set of `userkartikay/leetcode-solutions` (70+ questions).

### A. Current Coverage Distribution

| Pattern Family | Problems in Repository | Representative Questions | Assessment |
| :--- | :---: | :--- | :--- |
| **Arrays & Two Pointers** | High (12) | Two Sum, Container With Most Water, Sort Colors, Valid Palindrome, Two Sum II, Move Zeroes | Strong baseline for linear two-pointer techniques. |
| **Sliding Window** | High (11) | Longest Substring Without Repeating, Min Size Subarray Sum, Fruit Into Baskets, Max Consecutive Ones III | Comprehensive coverage of variable and fixed windows. |
| **Prefix Sum & Hashing** | Moderate (8) | Subarray Sum Equals K, Range Sum Query, Find Pivot Index | Good coverage of prefix frequency hashing. |
| **Binary Search** | Moderate (9) | Search Insert, 2D Matrix, Find Peak, Single Element in Sorted Array, Koko Bananas, Ship Packages | Solid coverage of both standard binary search and binary search on answer. |
| **Monotonic Stack** | Moderate (6) | Largest Rectangle in Histogram, Next Greater Element I & II, Asteroid Collision, Subarray Minimums | Excellent coverage of monotonic stack archetypes. |
| **Linked Lists** | Moderate (10) | Reverse List, Cycle I & II, Intersection, Merge Two Sorted, Remove Nth Node, Odd Even List | Good coverage of pointer manipulation and fast/slow pointers. |
| **Trees & BST** | Low-Moderate (7) | Inorder/Preorder/Postorder, Level Order, Max Depth, Balanced Tree, Diameter, BST Search/Insert | Basic traversals covered, but critical tree reasoning problems are missing. |
| **Recursion & Backtracking** | Moderate (8) | Subsets, Subsets II, Combination Sum I/II/III, N-Queens, Word Search, Generate Parentheses | Good recursion tree and pruning practice. |
| **Heap / Priority Queue** | Low (4) | Kth Largest Element, Sort Characters By Frequency, Last Stone Weight | Adequate basics, but median/stream heaps are absent. |
| **Dynamic Programming** | Low (6) | Climbing Stairs, House Robber, Coin Change, Min Cost Climbing Stairs | Limited to basic 1D DP and unbounded knapsack. |
| **Graphs** | **Critically Missing (0)** | None | **Zero representation of general graphs, grid traversal, topological sort, cycle detection, or shortest paths.** |
| **Intervals** | **Missing (0)** | None | **Zero representation of interval merging or scheduling.** |
| **Database / SQL** | ~15 | Combine Two Tables, Second Highest Salary, Duplicate Emails | Present in repository but outside C++ DSA scope. |

---

### B. Redundancies and Low-Yield Repetitions Flagged

1. **Prefix Sum + Hash Map Redundancy**:
   - `0560-subarray-sum-equals-k`, `0930-binary-subarrays-with-sum`, `0974-subarray-sums-divisible-by-k`, and `1248-count-number-of-nice-subarrays` all exercise virtually the identical prefix sum frequency lookup logic.
   - *Recommendation*: Retain `560` (canonical) and `930` (binary array variant); treat `974` and `1248` as optional supplementary drill rather than core curriculum milestones.
2. **Trivial String & Math Repetition**:
   - `0344-reverse-string` and `0345-reverse-vowels-of-a-string` are trivial 2-pointer exercises that provide negligible interview preparation beyond `0125-valid-palindrome`.
   - `0231-power-of-two` and `0326-power-of-three` duplicate basic modulo/bitwise checks.
3. **Database / SQL Scripts**:
   - While useful for database interviews, SQL questions should be isolated from the DSA tutor pipeline to avoid polluting compiler execution.

---

### C. Critical Blind Spots & Missing High-Yield Patterns

Placement technical interviews (particularly for top compensation bands like TCS Prime, Infosys Specialist Programmer, and Cognizant Digital) consistently test four areas where the repository has near-zero coverage:

1. **Graphs (Completely Missing)**:
   - **Grid Graph Traversal**: `200. Number of Islands` (connected components via DFS/BFS) and `994. Rotting Oranges` (multi-source BFS).
   - **Topological Sorting & Cycle Detection**: `207. Course Schedule` (Kahn's algorithm using indegree queue).
   - **Disjoint Set Union (DSU)**: `547. Number of Provinces`.
   - **Shortest Paths**: `743. Network Delay Time` (Dijkstra with priority queue).
2. **Trees & BST Advanced Reasoning**:
   - `98. Validate Binary Search Tree` (ancestral range propagation `(min_val, max_val)`).
   - `235. Lowest Common Ancestor of a BST` (value split branching).
3. **Dynamic Programming Breadth**:
   - **Longest Increasing Subsequence (LIS)**: `300. Longest Increasing Subsequence` (O(N^2) state checking vs O(N log N) patience sorting via binary search).
   - **2D String DP**: `1143. Longest Common Subsequence` (LCS grid).
   - **2D Grid Path DP**: `62. Unique Paths`.
4. **Intervals & Custom Sorting**:
   - `56. Merge Intervals` and `435. Non-overlapping Intervals` (sorting by start vs end time).

---

## 2. Master Curated Placement Curriculum (50 High-Yield Problems)

Below is the master curriculum organized across 15 core patterns.
- **Provenance**: `user_repo` (incorporated from your existing GitHub repository) vs `curated_core` (added to bridge blind spots).
- **Status**: `VERIFIED` (currently runnable in CLI with driver harness & test suite) vs `PLANNED` (scheduled for Phase 2 verification).

| ID | Problem Title | Difficulty | Primary Pattern | Subpattern | Provenance | Solved? | Status |
| :---: | :--- | :---: | :--- | :--- | :---: | :---: | :---: |
| **167** | [Two Sum II - Sorted Array](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Med | Two Pointers | Opposite-Direction Collision | `user_repo` | Yes | **VERIFIED** |
| **125** | [Valid Palindrome](https://leetcode.com/problems/valid-palindrome/) | Easy | Two Pointers | Collision with Character Filtering | `user_repo` | Yes | **VERIFIED** |
| **11** | [Container With Most Water](https://leetcode.com/problems/container-with-most-water/) | Med | Two Pointers | Greedy Boundary Contraction | `user_repo` | Yes | PLANNED |
| **15** | [3Sum](https://leetcode.com/problems/3sum/) | Med | Two Pointers | Sorted Array 2-Pointer with Dedup | `curated_core` | No | PLANNED |
| **75** | [Sort Colors](https://leetcode.com/problems/sort-colors/) | Med | Two Pointers | Dutch National Flag 3-Way Partition | `user_repo` | Yes | PLANNED |
| **3** | [Longest Substring Without Repeating](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Med | Sliding Window | Dynamic Window with Hash Map Lookup | `user_repo` | Yes | **VERIFIED** |
| **643** | [Maximum Average Subarray I](https://leetcode.com/problems/maximum-average-subarray-i/) | Easy | Sliding Window | Fixed Window (size k) | `user_repo` | Yes | PLANNED |
| **209** | [Minimum Size Subarray Sum](https://leetcode.com/problems/minimum-size-subarray-sum/) | Med | Sliding Window | Dynamic Window Minimization | `user_repo` | Yes | PLANNED |
| **76** | [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/) | Hard | Sliding Window | Multi-Frequency Character Matching | `user_repo` | Yes | PLANNED |
| **560** | [Subarray Sum Equals K](https://leetcode.com/problems/subarray-sum-equals-k/) | Med | Prefix Sum | Prefix Sum Frequency Hashing | `user_repo` | Yes | PLANNED |
| **1** | [Two Sum](https://leetcode.com/problems/two-sum/) | Easy | Hash Table | One-Pass Complement Lookup | `user_repo` | Yes | PLANNED |
| **724** | [Find Pivot Index](https://leetcode.com/problems/find-pivot-index/) | Easy | Prefix Sum | Running Left vs Right Comparison | `user_repo` | Yes | PLANNED |
| **704** | [Binary Search](https://leetcode.com/problems/binary-search/) | Easy | Binary Search | Exact Target Search (left <= right) | `curated_core` | Yes (35) | **VERIFIED** |
| **33** | [Search in Rotated Sorted Array](https://leetcode.com/problems/search-in-rotated-sorted-array/) | Med | Binary Search | Modified Search on Sorted Half | `curated_core` | No | PLANNED |
| **875** | [Koko Eating Bananas](https://leetcode.com/problems/koko-eating-bananas/) | Med | Binary Search | Search on Answer Space (Monotonic) | `user_repo` | Yes | PLANNED |
| **1011** | [Capacity To Ship Packages](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) | Med | Binary Search | Search on Answer Space (Greedy) | `user_repo` | Yes | PLANNED |
| **162** | [Find Peak Element](https://leetcode.com/problems/find-peak-element/) | Med | Binary Search | Slope / Gradient Comparison | `user_repo` | Yes | PLANNED |
| **496** | [Next Greater Element I](https://leetcode.com/problems/next-greater-element-i/) | Easy | Monotonic Stack | Decreasing Stack Next Greater | `user_repo` | Yes | **VERIFIED** |
| **739** | [Daily Temperatures](https://leetcode.com/problems/daily-temperatures/) | Med | Monotonic Stack | Next Greater Distance (Index Stack) | `curated_core` | No | PLANNED |
| **84** | [Largest Rectangle in Histogram](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Hard | Monotonic Stack | Previous & Next Smaller Boundaries | `user_repo` | Yes | PLANNED |
| **206** | [Reverse Linked List](https://leetcode.com/problems/reverse-linked-list/) | Easy | Linked List | In-Place Pointer Reversal | `user_repo` | Yes | PLANNED |
| **141** | [Linked List Cycle](https://leetcode.com/problems/linked-list-cycle/) | Easy | Linked List | Floyd's Tortoise and Hare | `user_repo` | Yes | PLANNED |
| **21** | [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/) | Easy | Linked List | Dummy Head Splicing | `user_repo` | Yes | PLANNED |
| **19** | [Remove Nth Node From End](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | Med | Linked List | Fixed Gap Two Pointers | `user_repo` | Yes | PLANNED |
| **104** | [Maximum Depth of Binary Tree](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | Easy | Tree | DFS Bottom-Up Return Value | `user_repo` | Yes | **VERIFIED** |
| **102** | [Binary Tree Level Order Traversal](https://leetcode.com/problems/binary-tree-level-order-traversal/) | Med | Tree | BFS Level-Sizing Queue | `user_repo` | Yes | PLANNED |
| **543** | [Diameter of Binary Tree](https://leetcode.com/problems/diameter-of-binary-tree/) | Easy | Tree | Post-Order DFS with Global Max | `user_repo` | Yes | PLANNED |
| **98** | [Validate Binary Search Tree](https://leetcode.com/problems/validate-binary-search-tree/) | Med | BST | Range Invariant Propagation | `curated_core` | No | PLANNED |
| **235** | [LCA of a BST](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) | Med | BST | Value Split Branching | `curated_core` | No | PLANNED |
| **200** | [Number of Islands](https://leetcode.com/problems/number-of-islands/) | Med | Graph | Grid DFS Connected Components | `curated_core` | No | **VERIFIED** |
| **994** | [Rotting Oranges](https://leetcode.com/problems/rotting-oranges/) | Med | Graph | Multi-Source BFS with Level Time | `curated_core` | No | PLANNED |
| **547** | [Number of Provinces](https://leetcode.com/problems/number-of-provinces/) | Med | Graph | Adjacency Matrix DFS / DSU | `curated_core` | No | PLANNED |
| **207** | [Course Schedule](https://leetcode.com/problems/course-schedule/) | Med | Graph | Directed Cycle / Kahn's TopoSort | `curated_core` | No | PLANNED |
| **133** | [Clone Graph](https://leetcode.com/problems/clone-graph/) | Med | Graph | DFS/BFS with Cloned Node Cache | `curated_core` | No | PLANNED |
| **743** | [Network Delay Time](https://leetcode.com/problems/network-delay-time/) | Med | Graph | Dijkstra Shortest Path (Min-Heap) | `curated_core` | No | PLANNED |
| **70** | [Climbing Stairs](https://leetcode.com/problems/climbing-stairs/) | Easy | Dynamic Prog | 1D Linear Recurrence (Fibonacci) | `user_repo` | Yes | **VERIFIED** |
| **198** | [House Robber](https://leetcode.com/problems/house-robber/) | Med | Dynamic Prog | Take / Skip Binary Choice | `user_repo` | Yes | PLANNED |
| **322** | [Coin Change](https://leetcode.com/problems/coin-change/) | Med | Dynamic Prog | Unbounded Knapsack Minimization | `user_repo` | Yes | PLANNED |
| **300** | [Longest Increasing Subsequence](https://leetcode.com/problems/longest-increasing-subsequence/) | Med | Dynamic Prog | Subsequence Patience Sort (O(NlogN)) | `curated_core` | No | PLANNED |
| **1143** | [Longest Common Subsequence](https://leetcode.com/problems/longest-common-subsequence/) | Med | Dynamic Prog | 2D String Grid DP (Match/Mismatch) | `curated_core` | No | PLANNED |
| **62** | [Unique Paths](https://leetcode.com/problems/unique-paths/) | Med | Dynamic Prog | 2D Grid Path Accumulation | `curated_core` | No | PLANNED |
| **56** | [Merge Intervals](https://leetcode.com/problems/merge-intervals/) | Med | Intervals | Sort by Start & Merge Overlaps | `curated_core` | No | PLANNED |
| **435** | [Non-overlapping Intervals](https://leetcode.com/problems/non-overlapping-intervals/) | Med | Intervals | Greedy Scheduling (Sort by End) | `curated_core` | No | PLANNED |
| **215** | [Kth Largest Element in an Array](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Med | Heap | Min-Heap of Size K vs Quickselect | `user_repo` | Yes | PLANNED |
| **1046** | [Last Stone Weight](https://leetcode.com/problems/last-stone-weight/) | Easy | Heap | Max-Heap Simulation | `user_repo` | Yes | PLANNED |
| **78** | [Subsets](https://leetcode.com/problems/subsets/) | Med | Backtracking | Cascading Power Set (Include/Exclude)| `user_repo` | Yes | PLANNED |
| **39** | [Combination Sum](https://leetcode.com/problems/combination-sum/) | Med | Backtracking | Unbounded Choice with Pruning | `user_repo` | Yes | PLANNED |
| **22** | [Generate Parentheses](https://leetcode.com/problems/generate-parentheses/) | Med | Backtracking | Constrained State Construction | `user_repo` | Yes | PLANNED |
| **208** | [Implement Trie](https://leetcode.com/problems/implement-trie-prefix-tree/) | Med | Trie | N-ary Prefix Node Design | `user_repo` | Yes | PLANNED |
| **121** | [Best Time to Buy and Sell Stock](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Easy | Greedy | Track Minimum Prefix | `user_repo` | Yes | **VERIFIED** |
| **53** | [Maximum Subarray](https://leetcode.com/problems/maximum-subarray/) | Med | DP / Kadane | Contiguous Subarray Optimization | `user_repo` | Yes | **VERIFIED** |
| **136** | [Single Number](https://leetcode.com/problems/single-number/) | Easy | Bit Manip | XOR Involutive Cancellation | `user_repo` | Yes | PLANNED |

---

## 3. Curriculum Phasing & Transition to Phase 2

1. **Immediate Phase 1 (Milestone 1.3 CLI)**:
   - 10 problems are **VERIFIED** with end-to-end C++ driver harnesses, test cases, canonical solutions, and buggy evaluation submissions.
   - Live testing confirmed that all 10 problems compile and evaluate deterministically via `CppRunner` and receive Socratic tutor diagnoses.
2. **Phase 2 Expansion (Database & Full Harnesses)**:
   - The remaining 40 planned problems from the master curriculum will be systematically seeded into SQLite with comprehensive test suites, reference C++ code, and edge cases.


## Remediation status (2026-10-12)

The curriculum has 53 stable lc_<LeetCode number> identities. Curated metadata and
provenance remain intact; backend/curriculum/registry.py joins executable fixtures by
LeetCode number. Ten entries have reference code, an explicit function signature,
a harness, and boundary/maximum-input tests. The other 43 entries are catalogue-only
and must not be offered for judging until their fixtures are verified. There are 19
current primary-pattern labels across 15 teaching families. No importer, scraper,
embedding index, or automatic repository sync has been added.
