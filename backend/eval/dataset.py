"""Version-controlled evaluation dataset containing verified DSA problems and representative buggy solutions."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.runner.schemas import TestCase
from backend.core.schemas import MistakeCategory


class EvalProblem(BaseModel):
    __test__ = False
    id: str
    leetcode_id: int
    function_signature: str
    title: str
    description: str
    constraints: str
    primary_pattern: str
    subpattern: str
    target_complexity: str
    test_cases: List[TestCase]
    harness_template: str = Field(
        description="C++ driver harness to wrap student function with standard I/O for testing."
    )
    canonical_solution: str
    buggy_submission: str
    intended_mistake_category: MistakeCategory
    mistake_description: str


# 5 Curated Canonical Problems with Verified Buggy Solutions
EVALUATION_DATASET: List[EvalProblem] = [
    # 1. Two Sum II - State transition / Pointer movement bug
    EvalProblem(
        id="lc_167",
        leetcode_id=167,
        function_signature="vector<int> twoSum(vector<int>& numbers, int target)",
        title="Two Sum II - Input Array Is Sorted",
        description="Given a 1-indexed sorted array of integers, find two numbers at distinct indices that add up to target. Exactly one valid pair exists. Return 1-based indices.",
        constraints="2 <= numbers.length <= 3 * 10^4, numbers sorted in non-decreasing order.",
        primary_pattern="Two Pointers",
        subpattern="Opposite-Directional (Collision)",
        target_complexity="O(N) time, O(1) space",
        test_cases=[
            TestCase(id="ts2_1", input_data="4\n2 7 11 15\n9\n", expected_output="1 2\n"),
            TestCase(id="ts2_2", input_data="4\n2 7 11 15\n18\n", expected_output="2 3\n"),
            TestCase(id="ts2_3", input_data="3\n2 3 4\n6\n", expected_output="1 3\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) cin >> nums[i];
    int target;
    cin >> target;
    vector<int> res = twoSum(nums, target);
    if (res.size() == 2) cout << res[0] << " " << res[1] << endl;
    else cout << "NOT_FOUND" << endl;
    return 0;
}
""",
        canonical_solution="""vector<int> twoSum(vector<int>& numbers, int target) {
    int left = 0, right = numbers.size() - 1;
    while (left < right) {
        int sum = numbers[left] + numbers[right];
        if (sum == target) return {left + 1, right + 1};
        else if (sum < target) left++;
        else right--;
    }
    return {};
}""",
        buggy_submission="""vector<int> twoSum(vector<int>& numbers, int target) {
    int left = 0, right = numbers.size() - 1;
    while (left < right) {
        int sum = numbers[left] + numbers[right];
        if (sum == target) {
            return {left + 1, right + 1};
        } else if (sum < target) {
            left++;
        } else {
            left++; // BUG: moving left instead of right when sum is too big
        }
    }
    return {};
}""",
        intended_mistake_category=MistakeCategory.STATE_TRANSITION,
        mistake_description="Incrementing left pointer when sum > target, increasing sum further instead of decreasing it."
    ),

    # 2. Valid Palindrome - Unhandled normalization / edge cases
    EvalProblem(
        id="lc_125",
        leetcode_id=125,
        function_signature="bool isPalindrome(const string& s)",
        title="Valid Palindrome",
        description="A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.",
        constraints="1 <= s.length <= 2 * 10^5, s consists only of printable ASCII characters.",
        primary_pattern="Two Pointers",
        subpattern="Opposite-Directional with Filtering",
        target_complexity="O(N) time, O(1) space",
        test_cases=[
            TestCase(id="vp_1", input_data="A man, a plan, a canal: Panama\n", expected_output="true\n"),
            TestCase(id="vp_2", input_data="race a car\n", expected_output="false\n"),
            TestCase(id="vp_3", input_data=" \n", expected_output="true\n")
        ],
        harness_template="""#include <iostream>
#include <string>
#include <cctype>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    string s;
    if (getline(cin, s)) {
        cout << (isPalindrome(s) ? "true" : "false") << endl;
    }
    return 0;
}
""",
        canonical_solution="""bool isPalindrome(const string& s) {
    int left = 0, right = (int)s.size() - 1;
    while (left < right) {
        while (left < right && !isalnum(s[left])) left++;
        while (left < right && !isalnum(s[right])) right--;
        if (tolower(s[left]) != tolower(s[right])) return false;
        left++;
        right--;
    }
    return true;
}""",
        buggy_submission="""bool isPalindrome(const string& s) {
    int left = 0, right = (int)s.size() - 1;
    // BUG: Comparing raw characters without skipping non-alphanumeric or lowercasing
    while (left < right) {
        if (s[left] != s[right]) return false;
        left++;
        right--;
    }
    return true;
}""",
        intended_mistake_category=MistakeCategory.UNHANDLED_EDGE_CASE,
        mistake_description="Comparing raw characters without filtering non-alphanumeric characters or converting case."
    ),

    # 3. Maximum Subarray - Negative array state reset bug
    EvalProblem(
        id="lc_53",
        leetcode_id=53,
        function_signature="int maxSubArray(vector<int>& nums)",
        title="Maximum Subarray",
        description="Given an integer array nums, find the subarray with the largest sum, and return its sum.",
        constraints="1 <= nums.length <= 10^5, -10^4 <= nums[i] <= 10^4.",
        primary_pattern="Dynamic Programming / Kadane",
        subpattern="Contiguous Subarray Optimization",
        target_complexity="O(N) time, O(1) space",
        test_cases=[
            TestCase(id="ms_1", input_data="9\n-2 1 -3 4 -1 2 1 -5 4\n", expected_output="6\n"),
            TestCase(id="ms_2", input_data="1\n1\n", expected_output="1\n"),
            TestCase(id="ms_3", input_data="3\n-3 -2 -1\n", expected_output="-1\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) cin >> nums[i];
    cout << maxSubArray(nums) << endl;
    return 0;
}
""",
        canonical_solution="""int maxSubArray(vector<int>& nums) {
    int max_sum = nums[0];
    int current_sum = nums[0];
    for (size_t i = 1; i < nums.size(); ++i) {
        current_sum = max(nums[i], current_sum + nums[i]);
        max_sum = max(max_sum, current_sum);
    }
    return max_sum;
}""",
        buggy_submission="""int maxSubArray(vector<int>& nums) {
    int max_sum = 0; // BUG: Initialized to 0, fails when all numbers are negative!
    int current_sum = 0;
    for (int x : nums) {
        current_sum += x;
        if (current_sum > max_sum) max_sum = current_sum;
        if (current_sum < 0) current_sum = 0;
    }
    return max_sum;
}""",
        intended_mistake_category=MistakeCategory.INVARIANT_VIOLATION,
        mistake_description="Initializing max_sum to 0 rather than nums[0], producing 0 instead of -1 for all-negative arrays."
    ),

    # 4. Binary Search - Boundary condition off-by-one
    EvalProblem(
        id="lc_704",
        leetcode_id=704,
        function_signature="int search(vector<int>& nums, int target)",
        title="Binary Search",
        description="Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, return its index. Otherwise, return -1.",
        constraints="1 <= nums.length <= 10^4, -10^4 < nums[i], target < 10^4. All integers are unique, sorted.",
        primary_pattern="Binary Search",
        subpattern="Exact Target Search",
        target_complexity="O(log N) time, O(1) space",
        test_cases=[
            TestCase(id="bs_1", input_data="6\n-1 0 3 5 9 12\n9\n", expected_output="4\n"),
            TestCase(id="bs_2", input_data="6\n-1 0 3 5 9 12\n2\n", expected_output="-1\n"),
            TestCase(id="bs_3", input_data="1\n5\n5\n", expected_output="0\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> nums(n);
    for (int i = 0; i < n; ++i) cin >> nums[i];
    int target;
    cin >> target;
    cout << search(nums, target) << endl;
    return 0;
}
""",
        canonical_solution="""int search(vector<int>& nums, int target) {
    int left = 0, right = (int)nums.size() - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;
        if (nums[mid] == target) return mid;
        else if (nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}""",
        buggy_submission="""int search(vector<int>& nums, int target) {
    int left = 0, right = (int)nums.size() - 1;
    // BUG: while (left < right) instead of left <= right; fails for single-element arrays
    while (left < right) {
        int mid = (left + right) / 2;
        if (nums[mid] == target) return mid;
        else if (nums[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}""",
        intended_mistake_category=MistakeCategory.BOUNDARY_OFF_BY_ONE,
        mistake_description="Loop condition 'left < right' terminates before inspecting the final candidate element, failing on single elements."
    ),

    # 5. Best Time to Buy and Sell Stock - Temporal ordering violation
    EvalProblem(
        id="lc_121",
        leetcode_id=121,
        function_signature="int maxProfit(vector<int>& prices)",
        title="Best Time to Buy and Sell Stock",
        description="You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock. Return maximum profit.",
        constraints="1 <= prices.length <= 10^5, 0 <= prices[i] <= 10^4.",
        primary_pattern="Sliding Window / One-Pass Greedy",
        subpattern="Track Minimum Prefix",
        target_complexity="O(N) time, O(1) space",
        test_cases=[
            TestCase(id="st_1", input_data="6\n7 1 5 3 6 4\n", expected_output="5\n"),
            TestCase(id="st_2", input_data="5\n7 6 4 3 1\n", expected_output="0\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int n;
    if (!(cin >> n)) return 0;
    vector<int> prices(n);
    for (int i = 0; i < n; ++i) cin >> prices[i];
    cout << maxProfit(prices) << endl;
    return 0;
}
""",
        canonical_solution="""int maxProfit(vector<int>& prices) {
    int min_price = 1e9;
    int max_profit = 0;
    for (int p : prices) {
        if (p < min_price) min_price = p;
        else if (p - min_price > max_profit) max_profit = p - min_price;
    }
    return max_profit;
}""",
        buggy_submission="""int maxProfit(vector<int>& prices) {
    // BUG: Global max minus global min ignores temporal constraint (buy day < sell day)
    int min_p = *min_element(prices.begin(), prices.end());
    int max_p = *max_element(prices.begin(), prices.end());
    return max(0, max_p - min_p);
}""",
        intended_mistake_category=MistakeCategory.WRONG_ARCHETYPE,
        mistake_description="Subtracting global minimum from global maximum without enforcing that buy day must precede sell day."
    ),

    # 6. Maximum Depth of Binary Tree - Tree / DFS
    EvalProblem(
        id="lc_104",
        leetcode_id=104,
        function_signature="int maxDepth(TreeNode* root)",
        title="Maximum Depth of Binary Tree",
        description="Given the root of a binary tree, return its maximum depth. (A binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node).",
        constraints="0 <= number of nodes <= 10^4, -100 <= Node.val <= 100",
        primary_pattern="Tree",
        subpattern="Depth-First Search (Bottom-Up Return Value)",
        target_complexity="O(N) time, O(H) space",
        test_cases=[
            TestCase(id="md_1", input_data="3 9 20 null null 15 7\n", expected_output="3\n"),
            TestCase(id="md_2", input_data="1 null 2\n", expected_output="2\n"),
            TestCase(id="md_3", input_data="null\n", expected_output="0\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <queue>
#include <algorithm>
using namespace std;

struct TreeNode {
    int val;
    TreeNode *left;
    TreeNode *right;
    TreeNode(int x) : val(x), left(NULL), right(NULL) {}
};

// STUDENT_CODE_PLACEHOLDER

TreeNode* buildTree(const string& line) {
    if (line.empty() || line == "null") return NULL;
    stringstream ss(line);
    string valStr;
    if (!(ss >> valStr) || valStr == "null") return NULL;
    TreeNode* root = new TreeNode(stoi(valStr));
    queue<TreeNode*> q;
    q.push(root);
    while (!q.empty() && ss >> valStr) {
        TreeNode* curr = q.front();
        q.pop();
        if (valStr != "null") {
            curr->left = new TreeNode(stoi(valStr));
            q.push(curr->left);
        }
        if (ss >> valStr && valStr != "null") {
            curr->right = new TreeNode(stoi(valStr));
            q.push(curr->right);
        }
    }
    return root;
}

int main() {
    string line;
    if (getline(cin, line)) {
        TreeNode* root = buildTree(line);
        cout << maxDepth(root) << endl;
    }
    return 0;
}
""",
        canonical_solution="""int maxDepth(TreeNode* root) {
    if (!root) return 0;
    vector<pair<TreeNode*,int>> pending;
    pending.push_back({root,1});
    int depth = 0;
    while (!pending.empty()) {
        auto entry = pending.back(); pending.pop_back();
        depth = max(depth,entry.second);
        if (entry.first->left) pending.push_back({entry.first->left,entry.second+1});
        if (entry.first->right) pending.push_back({entry.first->right,entry.second+1});
    }
    return depth;
}""",
        buggy_submission="""int maxDepth(TreeNode* root) {
    if (!root) return 0;
    // BUG: Missing '+ 1' for current node's contribution to depth
    return max(maxDepth(root->left), maxDepth(root->right));
}""",
        intended_mistake_category=MistakeCategory.INVARIANT_VIOLATION,
        mistake_description="Returning max(left, right) without adding 1 for the current node, producing 0 for any tree."
    ),

    # 7. Number of Islands - Graph / Grid DFS
    EvalProblem(
        id="lc_200",
        leetcode_id=200,
        function_signature="int numIslands(vector<vector<char>>& grid)",
        title="Number of Islands",
        description="Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.",
        constraints="1 <= m, n <= 300, grid[i][j] is '0' or '1'.",
        primary_pattern="Graph",
        subpattern="Grid Traversal (Connected Components via DFS/BFS)",
        target_complexity="O(M * N) time, O(M * N) space",
        test_cases=[
            TestCase(id="ni_1", input_data="4 5\n1 1 1 1 0\n1 1 0 1 0\n1 1 0 0 0\n0 0 0 0 0\n", expected_output="1\n"),
            TestCase(id="ni_2", input_data="4 5\n1 1 0 0 0\n1 1 0 0 0\n0 0 1 0 0\n0 0 0 1 1\n", expected_output="3\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int m, n;
    if (!(cin >> m >> n)) return 0;
    vector<vector<char>> grid(m, vector<char>(n));
    for (int i = 0; i < m; ++i) {
        for (int j = 0; j < n; ++j) {
            cin >> grid[i][j];
        }
    }
    cout << numIslands(grid) << endl;
    return 0;
}
""",
        canonical_solution="""int numIslands(vector<vector<char>>& grid) {
    const int rows = grid.size(), cols = grid[0].size();
    int count = 0;
    vector<pair<int,int>> pending;
    const int dr[] = {1,-1,0,0}, dc[] = {0,0,1,-1};
    for (int r = 0; r < rows; ++r) for (int c = 0; c < cols; ++c) {
        if (grid[r][c] != '1') continue;
        ++count;
        grid[r][c] = '0';
        pending.push_back({r,c});
        while (!pending.empty()) {
            auto cell = pending.back(); pending.pop_back();
            for (int k = 0; k < 4; ++k) {
                int nr = cell.first + dr[k], nc = cell.second + dc[k];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == '1') {
                    grid[nr][nc] = '0'; // mark when scheduled: each cell enters once
                    pending.push_back({nr,nc});
                }
            }
        }
    }
    return count;
}""",
        buggy_submission="""int numIslands(vector<vector<char>>& grid) {
    // BUG: Simply counts '1's instead of sinking connected components
    int count = 0;
    for (int i = 0; i < grid.size(); ++i) {
        for (int j = 0; j < grid[0].size(); ++j) {
            if (grid[i][j] == '1') count++;
        }
    }
    return count;
}""",
        intended_mistake_category=MistakeCategory.WRONG_ARCHETYPE,
        mistake_description="Counting every individual land cell instead of exploring and grouping connected components."
    ),

    # 8. Climbing Stairs - 1D DP
    EvalProblem(
        id="lc_70",
        leetcode_id=70,
        function_signature="int climbStairs(int n)",
        title="Climbing Stairs",
        description="You are climbing a staircase. It takes n steps to reach the top. Each time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        constraints="1 <= n <= 45",
        primary_pattern="Dynamic Programming",
        subpattern="1D Linear Recurrence (Fibonacci State)",
        target_complexity="O(N) time, O(1) space",
        test_cases=[
            TestCase(id="cs_1", input_data="2\n", expected_output="2\n"),
            TestCase(id="cs_2", input_data="3\n", expected_output="3\n"),
            TestCase(id="cs_3", input_data="4\n", expected_output="5\n")
        ],
        harness_template="""#include <iostream>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int n;
    if (cin >> n) {
        cout << climbStairs(n) << endl;
    }
    return 0;
}
""",
        canonical_solution="""int climbStairs(int n) {
    if (n <= 2) return n;
    int prev2 = 1, prev1 = 2;
    for (int i = 3; i <= n; ++i) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}""",
        buggy_submission="""int climbStairs(int n) {
    // BUG: Initializing base cases incorrectly (dp[2]=1 instead of 2)
    if (n == 1) return 1;
    if (n == 2) return 1; // Wrong base case: for 2 steps there are 2 ways (1+1 or 2)
    int prev2 = 1, prev1 = 1;
    for (int i = 3; i <= n; ++i) {
        int curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    return prev1;
}""",
        intended_mistake_category=MistakeCategory.BOUNDARY_OFF_BY_ONE,
        mistake_description="Incorrect base case definition: returning 1 for n=2 instead of 2 ways (1+1 and 2)."
    ),

    # 9. Longest Substring Without Repeating Characters - Sliding Window
    EvalProblem(
        id="lc_3",
        leetcode_id=3,
        function_signature="int lengthOfLongestSubstring(const string& s)",
        title="Longest Substring Without Repeating Characters",
        description="Given a string s, find the length of the longest substring without repeating characters.",
        constraints="0 <= s.length <= 5 * 10^4",
        primary_pattern="Sliding Window",
        subpattern="Dynamic/Variable Window with Hash Map / Direct Lookup",
        target_complexity="O(N) time, O(Sigma) space",
        test_cases=[
            TestCase(id="ls_1", input_data="abcabcbb\n", expected_output="3\n"),
            TestCase(id="ls_2", input_data="bbbbb\n", expected_output="1\n"),
            TestCase(id="ls_3", input_data="pwwkew\n", expected_output="3\n"),
            TestCase(id="ls_4", input_data="dvdf\n", expected_output="3\n")
        ],
        harness_template="""#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    string s;
    if (getline(cin, s)) {
        cout << lengthOfLongestSubstring(s) << endl;
    }
    return 0;
}
""",
        canonical_solution="""int lengthOfLongestSubstring(const string& s) {
    vector<int> lastPos(256, -1);
    int maxLen = 0, left = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        if (lastPos[(unsigned char)s[right]] >= left) {
            left = lastPos[(unsigned char)s[right]] + 1;
        }
        lastPos[(unsigned char)s[right]] = right;
        maxLen = max(maxLen, right - left + 1);
    }
    return maxLen;
}""",
        buggy_submission="""int lengthOfLongestSubstring(const string& s) {
    // BUG: Resets left pointer to right instead of lastPos + 1, missing overlapping valid windows
    vector<int> lastPos(256, -1);
    int maxLen = 0, left = 0;
    for (int right = 0; right < (int)s.size(); ++right) {
        if (lastPos[(unsigned char)s[right]] != -1) {
            left = right; // Over-eager contraction
        }
        lastPos[(unsigned char)s[right]] = right;
        maxLen = max(maxLen, right - left + 1);
    }
    return maxLen;
}""",
        intended_mistake_category=MistakeCategory.STATE_TRANSITION,
        mistake_description="Over-contracting the left pointer to right upon duplicate, discarding valid intermediate characters."
    ),

    # 10. Next Greater Element I - Monotonic Stack
    EvalProblem(
        id="lc_496",
        leetcode_id=496,
        function_signature="vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2)",
        title="Next Greater Element I",
        description="The next greater element of some element x in an array is the first greater element that is to the right of x in the same array. Find next greater for nums1 in nums2.",
        constraints="1 <= nums1.length <= nums2.length <= 1000",
        primary_pattern="Monotonic Stack",
        subpattern="Next Greater Element (Decreasing Stack)",
        target_complexity="O(N + M) time, O(M) space",
        test_cases=[
            TestCase(id="nge_1", input_data="3\n4 1 2\n4\n1 3 4 2\n", expected_output="-1 3 -1\n"),
            TestCase(id="nge_2", input_data="2\n2 4\n4\n1 2 3 4\n", expected_output="3 -1\n")
        ],
        harness_template="""#include <iostream>
#include <vector>
#include <stack>
#include <unordered_map>
using namespace std;

// STUDENT_CODE_PLACEHOLDER

int main() {
    int n1, n2;
    if (!(cin >> n1)) return 0;
    vector<int> nums1(n1);
    for (int i = 0; i < n1; ++i) cin >> nums1[i];
    if (!(cin >> n2)) return 0;
    vector<int> nums2(n2);
    for (int i = 0; i < n2; ++i) cin >> nums2[i];
    vector<int> ans = nextGreaterElement(nums1, nums2);
    for (int i = 0; i < (int)ans.size(); ++i) {
        cout << ans[i] << (i + 1 == (int)ans.size() ? "" : " ");
    }
    cout << endl;
    return 0;
}
""",
        canonical_solution="""vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2) {
    unordered_map<int, int> nextMap;
    stack<int> st;
    for (int num : nums2) {
        while (!st.empty() && st.top() < num) {
            nextMap[st.top()] = num;
            st.pop();
        }
        st.push(num);
    }
    vector<int> res;
    for (int num : nums1) {
        res.push_back(nextMap.count(num) ? nextMap[num] : -1);
    }
    return res;
}""",
        buggy_submission="""vector<int> nextGreaterElement(vector<int>& nums1, vector<int>& nums2) {
    // BUG: Stack condition flipped (st.top() > num) forming an increasing stack instead of decreasing
    unordered_map<int, int> nextMap;
    stack<int> st;
    for (int num : nums2) {
        while (!st.empty() && st.top() > num) { // Wrong inequality!
            nextMap[st.top()] = num;
            st.pop();
        }
        st.push(num);
    }
    vector<int> res;
    for (int num : nums1) {
        res.push_back(nextMap.count(num) ? nextMap[num] : -1);
    }
    return res;
}""",
        intended_mistake_category=MistakeCategory.INVARIANT_VIOLATION,
        mistake_description="Inverted stack condition (st.top() > num) finding next smaller element instead of next greater."
    )
]


# Fixed boundary and limit cases, with analytically known expected answers.
# These exercise constraints; they do not establish correctness for every input.
def _array_input(values):
    return str(len(values)) + "\n" + " ".join(map(str, values)) + "\n"


_BOUNDARIES = {
    167: [TestCase(id='ts_negative_pair', input_data='2\n-3 -1\n-4\n', expected_output='1 2'),
          TestCase(id='ts_max', input_data=_array_input([0]*29998+[1,2])+'3\n', expected_output='29999 30000')],
    125: [TestCase(id='vp_single', input_data='a\n', expected_output='true'),
          TestCase(id='vp_max', input_data='a'*200000+'\n', expected_output='true')],
    53: [TestCase(id='ms_single_negative', input_data='1\n-10000\n', expected_output='-10000'),
         TestCase(id='ms_max', input_data=_array_input([10000]*100000), expected_output='1000000000')],
    704: [TestCase(id='bs_single_absent', input_data='1\n5\n4\n', expected_output='-1'),
          TestCase(id='bs_max', input_data=_array_input(range(10000))+'9999\n', expected_output='9999')],
    121: [TestCase(id='stock_single', input_data='1\n5\n', expected_output='0'),
          TestCase(id='stock_max', input_data=_array_input([0]*99999+[10000]), expected_output='10000')],
    104: [TestCase(id='tree_single', input_data='1\n', expected_output='1'),
          TestCase(id='tree_max_skew', input_data='1 '+'null 1 '*9999+'\n', expected_output='10000')],
    200: [TestCase(id='island_water', input_data='1 1\n0\n', expected_output='0'),
          TestCase(id='island_single', input_data='1 1\n1\n', expected_output='1'),
          TestCase(id='island_max', input_data='300 300\n'+('1 '*300+'\n')*300, expected_output='1'),
          TestCase(id='island_diagonal', input_data='2 2\n1 0\n0 1\n', expected_output='2')],
    70: [TestCase(id='stairs_one', input_data='1\n', expected_output='1'),
         TestCase(id='stairs_max', input_data='45\n', expected_output='1836311903')],
    3: [TestCase(id='substring_empty', input_data='\n', expected_output='0'),
        TestCase(id='substring_max', input_data='a'*50000+'\n', expected_output='1')],
    496: [TestCase(id='nge_single', input_data='1\n1\n1\n1\n', expected_output='-1'),
          TestCase(id='nge_max', input_data=_array_input(range(1000))+_array_input(range(1000)),
                   expected_output=' '.join(map(str,list(range(1,1000))+[-1])))],
}
for _problem in EVALUATION_DATASET:
    _problem.test_cases.extend(_BOUNDARIES[_problem.leetcode_id])
