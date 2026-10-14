"""Reviewed starter lessons, deliberately concise and independent of model output.

Templates illustrate one subpattern, not a universal solution. Complexity variables
are local to each lesson. Linked practice remains optional and uses stable IDs.
"""
from pydantic import BaseModel, ConfigDict, Field
from backend.curriculum.registry import get_registry

class Subpattern(BaseModel):
    name: str
    distinction: str

class WalkthroughStep(BaseModel):
    note: str
    values: list[str]
    active: list[int] = Field(default_factory=list)
    links: list[tuple[int, int]] = Field(default_factory=list)

class Lesson(BaseModel):
    model_config = ConfigDict(extra='forbid')
    id: str
    title: str
    patterns: list[str]
    introduction: str
    intuition: str
    stl: list[str]
    template: str
    complexity: str
    subpatterns: list[Subpattern]
    recognition_questions: list[str]
    misconceptions: list[str]
    walkthrough: list[WalkthroughStep] = Field(min_length=2)
    related_questions: list[int]
    diagram: str = 'array'
    review_status: str = 'starter_content_reviewed'

def step(note, values, active=(), links=()):
    return WalkthroughStep(note=note,values=[str(x) for x in values],active=list(active),links=list(links))

def lesson(id, title, patterns, introduction, intuition, stl, template, complexity,
           subpatterns, recognition, mistakes, steps, related, diagram='array'):
    return Lesson(id=id,title=title,patterns=patterns,introduction=introduction,intuition=intuition,
        stl=stl,template=template,complexity=complexity,
        subpatterns=[Subpattern(name=n,distinction=d) for n,d in subpatterns],
        recognition_questions=recognition,misconceptions=mistakes,walkthrough=steps,
        related_questions=related,diagram=diagram)

LESSONS = [
lesson('arrays-hashing','Arrays & Hashing',['Arrays & Hashing','Hash Table'],
 'Use indexed storage for ordered data and hashing for repeated membership or frequency queries.',
 'Before visiting a value, ask what earlier information must be remembered. A complement lookup uses only earlier values, so it cannot reuse the same index.',
 ['vector<int> a; a.push_back(7); a.size();','unordered_map<int,int> seen; seen.find(key);','unordered_set<int> used; used.insert(x); used.count(x);'],
 'unordered_map<int,int> seen;\nfor (int i = 0; i < (int)a.size(); ++i) {\n    auto it = seen.find(target - a[i]);\n    if (it != seen.end()) { /* pair: it->second, i */ }\n    seen[a[i]] = i;\n}',
 'N entries: expected O(N) time and O(N) memory for complement lookup. Hash collisions can degrade time to O(N²). Output and bucket allocation also consume memory.',
 [('Membership','Remember whether a value exists.'),('Frequency','Remember how often it occurs.'),('Canonical key','Normalize objects before grouping.')],
 ['Do I repeatedly search previously seen values?','Does order matter, or only membership?'],
 ['Do not look up after inserting when an index cannot be reused.','map is ordered; unordered_map has expected, not guaranteed, constant-time lookup.'],
 [step('Target 9: before 2, the seen map is empty.',[2,7,11], [0]),step('Remember 2 at index 0; visiting 7 finds complement 2.',[2,7,11],[0,1])], [1,217,242,49,238]),
lesson('two-pointers','Two Pointers',['Two Pointers'],
 'Use two positions when ordering or positional relationships let you discard work safely.',
 'For a sorted pair sum, a sum below the target cannot improve by decreasing the right value. Move the left position; prove the eliminated pairs cannot work.',
 ['sort(a.begin(), a.end());','swap(a[left], a[right]);','size_t is unsigned: avoid subtracting from an empty size.'],
 'int left = 0, right = (int)a.size() - 1;\nwhile (left < right) {\n    long long sum = (long long)a[left] + a[right];\n    if (sum == target) { /* record pair */ break; }\n    if (sum < target) ++left; else --right;\n}',
 'Sorted pair search: O(N) time, O(1) auxiliary space. Sorting unsorted input adds O(N log N) and can destroy original indices.',
 [('Opposite ends','Use monotonic sorted values to shrink candidates.'),('Read/write','Compact retained values with a write position.'),('Fast/slow','Compare positions moving at different rates.')],
 ['Can moving a boundary discard many candidates with a proof?','Must original indices be retained?'],
 ['Moving both positions may skip a valid pair.','The sorted-pair rule does not apply to arbitrary unsorted arrays.'],
 [step('Target 9: 2 + 15 = 17, so discard the right endpoint.',[2,7,11,15],[0,3]),step('2 + 11 = 13: move right again.',[2,7,11,15],[0,2]),step('2 + 7 = 9: the pair is found.',[2,7,11,15],[0,1])],[167,125,11,26,283]),
lesson('sliding-window','Sliding Window',['Sliding Window'],
 'Maintain a contiguous range instead of recomputing every candidate substring or subarray.',
 'Grow the right boundary, update state, and shrink the left boundary until the chosen invariant holds. Shrinking by sum requires monotonic behavior such as positive values.',
 ['unordered_map<char,int> count; ++count[c]; --count[c];','string text; text.size();','vector<int> last(256, -1);'],
 'int left = 0, best = 0;\nunordered_map<char,int> count;\nfor (int right = 0; right < (int)s.size(); ++right) {\n    ++count[s[right]];\n    while (count[s[right]] > 1) --count[s[left++]];\n    best = max(best, right - left + 1);\n}',
 'N characters, A distinct keys: expected O(N) time because each boundary advances at most N times; O(A) space. Hashing has worst-case collision costs.',
 [('Fixed width','Remove one old value when adding a new one.'),('Longest valid','Shrink until valid, then maximize width.'),('Minimum satisfying','While satisfied, record and shrink.')],
 ['Is the answer contiguous?','Can removing the left entry restore a broken condition?'],
 ['Negative values break simple positive-sum shrinking.','Update counts when shrinking; do not merely move the boundary.'],
 [step('ab is unique; left=0, right=1.',list('abca'),[0,1]),step('abc is unique; best length is 3.',list('abca'),[0,1,2]),step('Adding a repeats a; remove the old a. bca remains length 3.',list('abca'),[1,2,3])],[3,643,209,424,567]),
lesson('binary-search','Binary Search',['Binary Search'],
 'Use sorted data or a monotonic yes/no predicate to discard half the candidate range.',
 'A lower-bound search keeps the first possible position within a half-open interval [left,right). If the middle value is too small, every position through middle is too small.',
 ['auto it = lower_bound(a.begin(), a.end(), target);','auto end = upper_bound(a.begin(), a.end(), target);','long long prevents overflow in large answer-space arithmetic.'],
 'int left = 0, right = (int)a.size();\nwhile (left < right) {\n    int mid = left + (right - left) / 2;\n    if (a[mid] < target) left = mid + 1;\n    else right = mid;\n}\n// left is the insertion position; check bounds before reading a[left].',
 'N sorted values: O(log N) time, O(1) auxiliary space. Answer-space search costs O(log range × predicate cost); the predicate must be monotonic.',
 [('Exact match','Check the insertion position for equality.'),('First/last boundary','Choose lower or upper bound carefully.'),('Answer space','Search a monotonic feasibility predicate instead of stored values.')],
 ['Is there an ordered boundary between false and true?','Which side keeps the middle candidate?'],
 ['Do not mix inclusive and half-open update rules.','A returned position equal to size must not be indexed.'],
 [step('Find lower bound of 7: [0,5), mid=2 points to 5; discard indices 0..2.',[1,3,5,7,9],[2]),step('Now [3,5), mid=4 points to 9; keep [3,4).',[1,3,5,7,9],[4]),step('Now mid=3 points to 7; right=3. left=right=3 is the answer.',[1,3,5,7,9],[3])],[704,35,34,875,1011]),
lesson('prefix-sum','Prefix Sum',['Prefix Sum'],
 'Turn repeated range aggregation into differences between cumulative states.',
 'Define prefix[0]=0 and prefix[i+1]=prefix[i]+a[i]. Then the sum of [left,right) is prefix[right]-prefix[left].',
 ['vector<long long> prefix(a.size()+1, 0);','unordered_map<long long,int> frequency;','frequency[0] = 1;'],
 'vector<long long> prefix(a.size()+1, 0);\nfor (int i = 0; i < (int)a.size(); ++i)\n    prefix[i+1] = prefix[i] + a[i];\n// sum of [left,right): prefix[right] - prefix[left]',
 'O(N) preprocessing and O(N) storage; O(1) per static range query. Updates require rebuilding or a different data structure.',
 [('Range queries','Subtract two prefix totals.'),('Sum equals K','Count earlier prefixes equal to current minus K.'),('Remainders','Equal remainders identify divisible differences.')],
 ['Can the range answer be written as a difference of prefixes?','Must I count ranges or only detect one?'],
 ['Include the empty prefix.','Use wide sums; a legal element can still yield an overflowing total.'],
 [step('Array 2,-1,3 has prefix 0,2,1,4.',[0,2,1,4],[0,3]),step('Range indices [1,3) sums to prefix[3]-prefix[1]=4-2=2.',[0,2,1,4],[1,3])],[560,724,303,525,1480]),
lesson('strings','Strings',['Strings','String Matching'],
 'Choose between direct traversal, frequency reasoning, character mapping, and substring matching.',
 'A subsequence permits gaps but preserves order. A substring requires contiguity; these need different invariants.',
 ['string s; s.size(); s.substr(start, length);','s.find(pattern); // string::npos means absent','tolower(static_cast<unsigned char>(c));'],
 'int matched = 0;\nfor (char c : text)\n    if (matched < (int)pattern.size() && pattern[matched] == c) ++matched;\nbool isSubsequence = matched == (int)pattern.size();',
 'Subsequence scan: O(text length + pattern length) upper bound, O(1) auxiliary memory. Naive substring search may cost O(N M).',
 [('Subsequence','Allow gaps while preserving order.'),('Substring','Require adjacent positions.'),('Character mapping','A bijection needs checks in both directions.')],
 ['Are gaps allowed?','Are characters bytes, ASCII letters, or Unicode code points?'],
 ['Empty patterns need deliberate handling.','C++ string indexes bytes; do not assume arbitrary Unicode characters occupy one byte.'],
 [step('Find ac as a subsequence of abc: match a.',list('abc'),[0]),step('Skip b; match c. A substring ac is still absent.',list('abc'),[2])],[14,28,205,387,392]),
lesson('stacks-queues','Stacks & Queues',['Stacks & Queues','Monotonic Stack'],
 'Use a stack for last-in-first-out pending work and a queue for first-in-first-out scheduling.',
 'Bracket validation keeps unmatched opening brackets. A closing bracket must match the most recent opening one, not any earlier one.',
 ['stack<char> pending; pending.push(c); pending.top(); pending.pop();','queue<int> q; q.push(x); q.front(); q.pop();','deque<int> d; d.push_back(x); d.pop_front();'],
 'stack<char> pending;\nfor (char c : brackets) {\n    if (c == \'(\') pending.push(c);\n    else {\n        if (pending.empty()) { /* invalid */ break; }\n        pending.pop();\n    }\n}\n// Restricted example for parentheses only: require pending.empty() at end.',
 'N brackets: O(N) time and O(N) worst-case stack memory. A monotonic stack also has O(N) total pushes and pops, despite nested loops.',
 [('Nesting','Match the last pending opening symbol.'),('Monotonic stack','Discard dominated unresolved candidates.'),('Queue','Process work in discovery order.')],
 ['Which unresolved item should be handled next?','Can a newly arrived value permanently invalidate earlier candidates?'],
 ['top/front are undefined on empty containers.','A parentheses-only template is not sufficient for mixed brackets.'],
 [step('Read (: push. Stack bottom → top.', ['('],[0]),step('Read another (: push.', ['(','('],[1]),step('Read ): pop the most recent (.',['('],[0]),step('Read final ): empty stack.',[],[])],[20,155,232,496,739], 'stack'),
lesson('linked-lists','Linked Lists',['Linked List'],
 'Operate on node identity and links rather than indexed positions.',
 'During reversal, retain the next node before replacing the current link. The processed prefix points backward; the remaining suffix still points forward.',
 ['Node* current = head;','Node* next = current->next;','Use nullptr for a missing node; node definitions are problem-specific.'],
 'Node* previous = nullptr;\nNode* current = head;\nwhile (current != nullptr) {\n    Node* next = current->next;\n    current->next = previous;\n    previous = current;\n    current = next;\n}\n// previous is the reversed head; Node is a placeholder for the supplied type.',
 'Reversal: O(N) time, O(1) auxiliary space. Recursive reversal consumes O(N) call-stack memory.',
 [('Reversal','Replace links while retaining the remainder.'),('Fast/slow','Detect cycles or find a midpoint.'),('Dummy head','Unify removal at the head and interior.')],
 ['Can the head change?','Does equality mean equal values or the same node?'],
 ['Overwriting next before saving it loses the suffix.','Do not dereference a null fast pointer.'],
 [step('Start: previous=null, current=1.',[1,2,3],[0],[(0,1),(1,2)]),step('After processing 1 and 2, link 2 → 1; current=3.',[1,2,3],[2],[(1,0)]),step('Final chain 3 → 2 → 1.',[1,2,3],[2],[(2,1),(1,0)])],[206,141,21,19,876],'graph'),
lesson('trees-bst','Trees & BST',['Tree','Binary Search Tree'],
 'Traverse hierarchical data while preserving either structural or ordering invariants.',
 'Postorder computes children before their parent. Tree height combines child heights; BST validity instead carries an allowed range inherited from all ancestors.',
 ['queue<Node*> pending; pending.push(root);','stack<Node*> work; work.push(root);','max(leftHeight, rightHeight);'],
 'int height(Node* node) {\n    if (node == nullptr) return 0;\n    return 1 + max(height(node->left), height(node->right));\n}\n// Node is a placeholder. For deep trees, use an explicit stack.',
 'N nodes, height H: O(N) traversal and O(H) recursion memory. BST lookup is O(H), not always O(log N); a skewed BST has H=N.',
 [('DFS/postorder','Return child results upward.'),('BFS levels','Process the queue size captured before a level starts.'),('BST ranges','Carry bounds from ancestors, not just the parent.')],
 ['Is information needed from descendants or ancestors?','Is the tree guaranteed to be balanced?'],
 ['Checking only immediate children does not establish BST validity.','Deep recursion can overflow the Windows stack.'],
 [step('Height of leaf nodes 2 and 3 is 1.',[1,2,3],[1,2],[(0,1),(0,2)]),step('Root height is 1+max(1,1)=2.',[1,2,3],[0],[(0,1),(0,2)])],[104,102,98,235,230],'graph'),
lesson('graphs','Graph Traversal',['Graph'],
 'Represent relationships using vertices and edges; choose traversal according to reachability, components, or distance requirements.',
 'BFS discovers vertices in increasing edge distance in an unweighted graph. Mark on discovery so multiple predecessors cannot enqueue the same vertex repeatedly.',
 ['vector<vector<int>> adjacent(n);','queue<int> frontier; frontier.push(start);','vector<int> distance(n, -1);'],
 'queue<int> frontier;\nvector<int> distance(n, -1);\ndistance[start] = 0; frontier.push(start);\nwhile (!frontier.empty()) {\n    int u = frontier.front(); frontier.pop();\n    for (int v : adjacent[u]) if (distance[v] == -1) {\n        distance[v] = distance[u] + 1; frontier.push(v);\n    }\n}',
 'Adjacency-list traversal: O(V+E) time, O(V) extra state beyond adjacency storage. A grid has V=R×C. BFS shortest-distance guarantees require unweighted edges.',
 [('Components','Restart traversal from each unvisited vertex.'),('Multi-source BFS','Enqueue all sources with distance zero.'),('Topological order','Process directed prerequisite edges without a cycle.'),('Weighted shortest path','Use Dijkstra only with nonnegative edge weights.')],
 ['Are edges weighted or directed?','Do I need any path, shortest distance, or a component count?'],
 ['Marking only when popped permits duplicate enqueues.','Disconnected graphs require multiple traversal starts.'],
 [step('Source A has distance 0; queue contains A.', ['A','B','C','D'],[0],[(0,1),(0,2),(1,3)]),step('Discover B and C at distance 1.', ['A','B','C','D'],[1,2],[(0,1),(0,2),(1,3)]),step('B discovers D at distance 2.', ['A','B','C','D'],[3],[(0,1),(0,2),(1,3)])],[200,994,207,733,785],'graph'),
lesson('dynamic-programming','Dynamic Programming',['Dynamic Programming','Dynamic Programming / Kadane'],
 'Store results of overlapping subproblems after defining exactly what each state means.',
 'For staircase counting, ways[i] counts sequences reaching step i. Every sequence ends with a one-step or two-step move; those disjoint choices give ways[i-1]+ways[i-2].',
 ['vector<long long> ways(n+1, 0);','fill(dp.begin(), dp.end(), initial);','min(best, candidate); max(best, candidate);'],
 'vector<long long> ways(n+1, 0);\nways[0] = 1;\nfor (int i = 1; i <= n; ++i) {\n    ways[i] = ways[i-1];\n    if (i >= 2) ways[i] += ways[i-2];\n}\n// Check input bounds: counts eventually exceed even long long.',
 'N steps: O(N) time and O(N) table memory, reducible to O(1) with two retained states. Subset-sum O(N S) depends on sum S, not just entry count.',
 [('Linear recurrence','Retain nearby predecessor states.'),('Take/skip','Compare including and excluding a choice.'),('Grid','Combine already computed neighboring states.'),('Knapsack','Loop direction determines whether an item may be reused.')],
 ['What does one state represent?','Which states must already be computed?'],
 ['A recurrence without valid base states gives wrong results.','Counting, maximizing, and minimizing require different identities and transitions.'],
 [step('Base: ways[0]=1, ways[1]=1.',[1,1,'?','?','?'],[0,1]),step('ways[2]=1+1=2.',[1,1,2,'?','?'],[0,1,2]),step('ways[3]=2+1=3; ways[4]=3+2=5.',[1,1,2,3,5],[2,3,4])],[70,198,322,62,416]),
lesson('greedy-intervals','Greedy & Intervals',['Greedy','Greedy / One-Pass','Intervals'],
 'A greedy decision needs a proof that a locally chosen option can belong to an optimal solution.',
 'For maximum compatible intervals, choosing the earliest finishing interval leaves at least as much room as a later-finishing choice. Merging overlaps solves a different task.',
 ['sort(intervals.begin(), intervals.end());','sort(items.begin(), items.end(), [](auto a, auto b) { return a.second < b.second; });','Use long long when subtracting extreme endpoints.'],
 'sort(intervals.begin(), intervals.end());\nvector<pair<int,int>> merged;\nfor (auto interval : intervals) {\n    if (merged.empty() || merged.back().second < interval.first)\n        merged.push_back(interval);\n    else merged.back().second = max(merged.back().second, interval.second);\n}',
 'Merging N intervals: O(N log N) sorting, O(N) output. Endpoint-touch overlap rules depend on the problem; scheduling by end time differs from merge-by-start.',
 [('Merge','Unite overlapping coverage.'),('Schedule','Select mutually compatible intervals.'),('Reachability frontier','Maintain the farthest position reachable so far.')],
 ['Can I exchange an optimal first choice with my greedy one?','Do touching endpoints count as overlapping here?'],
 ['Sorting by start is not the scheduling proof.','Do not assume greedy works just because a local choice looks good.'],
 [step('Sorted intervals: [1,3], [2,4], [6,8].',['1..3','2..4','6..8'],[0,1]),step('Merge the first two into [1,4]; retain [6,8].',['1..4','6..8'],[0,1])],[56,435,57,55,121]),
lesson('heaps','Heaps & Priority Queues',['Heap (Priority Queue)'],
 'Keep the next highest or lowest priority item accessible without fully sorting each update.',
 'To retain the largest K values, keep a min-heap of size at most K. Its top is the smallest retained candidate and can be discarded when a larger value arrives.',
 ['priority_queue<int> maximum;','priority_queue<int, vector<int>, greater<int>> minimum;','heap.push(x); heap.top(); heap.pop();'],
 'priority_queue<int, vector<int>, greater<int>> heap;\nfor (int x : a) {\n    heap.push(x);\n    if ((int)heap.size() > k) heap.pop();\n}\n// For 1 <= k <= a.size(), heap.top() is the kth largest.',
 'N entries, retained K: O(N log(K+1)) time, O(K) memory. priority_queue does not offer arbitrary-key decrease or removal.',
 [('Top K','Retain a bounded candidate set.'),('Streaming','Update priority as values arrive.'),('Best-first','Expand the next minimum-cost pending candidate.')],
 ['Do I need every sorted value, or only the next extreme?','Should the heap top be the answer or the candidate to discard?'],
 ['C++ priority_queue defaults to a max-heap.','Calling top on an empty heap is invalid.'],
 [step('K=2, see 4 and 1: retained min-heap top is 1.',[1,4],[0]),step('See 7, evict 1: retained values 4,7; kth largest is 4.',[4,7],[0])],[215,1046,347,703,973]),
lesson('backtracking','Backtracking',['Backtracking'],
 'Explore a choice tree when the task needs combinations, permutations, or constrained constructions.',
 'Make one choice, recurse on the remaining choices, and undo that choice. The restored state must exactly match the state before entering the branch.',
 ['vector<int> path; path.push_back(x); path.pop_back();','vector<vector<int>> answers; answers.push_back(path);','sort(a.begin(), a.end()); // often needed for duplicate skipping'],
 'void subsets(int start, const vector<int>& a, vector<int>& path, vector<vector<int>>& out) {\n    out.push_back(path);\n    for (int i = start; i < (int)a.size(); ++i) {\n        path.push_back(a[i]);\n        subsets(i+1, a, path, out);\n        path.pop_back();\n    }\n}',
 'N distinct entries: O(N 2^N) when copying all subset output; O(N) recursion/path memory excluding output. Enumeration grows rapidly.',
 [('Subsets','Each position may be included or excluded.'),('Permutations','Track which positions are already used.'),('Constrained construction','Prune only when no completion remains possible.')],
 ['Must I return all possibilities?','Can a partial state be rejected before completing it?'],
 ['Forgetting to undo a choice contaminates later branches.','Duplicate values require duplicate-aware rules, not merely the distinct-values template.'],
 [step('Choose 1; remaining choice is 2.', ['[]','[1]','[1,2]'],[1]),step('Undo 2, then undo 1; next root branch is [2].',['[]','[1]','[1,2]','[2]'],[3])],[78,39,22,46,90]),
lesson('tries','Tries',['Trie'],
 'Share prefixes between words when queries need incremental prefix or wildcard matching.',
 'A path represents a prefix. A terminal flag distinguishes a complete stored word from a path that exists only because a longer word was inserted.',
 ['array<int,26> next; next.fill(-1);','vector<Node> nodes(1);','Use indices across vector growth; references may be invalidated.'],
 'struct Node {\n    array<int,26> next; bool terminal = false;\n    Node() { next.fill(-1); }\n};\nvector<Node> nodes(1);\n// Lowercase ASCII only. For each character, follow/create its child index.\n// Mark only the final node terminal. Do not retain references across emplace_back().',
 'Word length L: O(L) insert/exact lookup; O(total stored characters × alphabet size) dense-child storage. Wildcards may branch exponentially.',
 [('Exact word','Path exists and final node is terminal.'),('Prefix','Path exists; no terminal requirement.'),('Wildcard','Branch over available children for a wildcard.')],
 ['Do many queries share prefixes?','What is the alphabet and memory budget?'],
 ['Prefix presence does not imply word presence.','A 26-child array assumes lowercase English letters; validate or choose a different representation.'],
 [step('Insert cat: c → a → t, mark t terminal.',['c','a','t'],[2],[(0,1),(1,2)]),step('Query ca: prefix exists but no complete word is marked.',['c','a','t'],[1],[(0,1),(1,2)])],[208,211],'graph'),
lesson('bits','Bit Manipulation',['Bit Manipulation'],
 'Reason about independent binary positions or algebraic identities when the input guarantees permit it.',
 'XOR cancels identical pairs because x XOR x=0 and x XOR 0=x. Single Number relies on all other values occurring exactly twice.',
 ['unsigned int mask = 1u << bit;','value & mask; value ^ mask;','value &= value - 1; // clears one set bit for nonzero unsigned values'],
 'unsigned int value = input;\nint count = 0;\nwhile (value != 0) {\n    value &= value - 1;\n    ++count;\n}',
 'B-bit word: O(B) worst-case counting and O(1) auxiliary space. XOR aggregation over N values costs O(N). Valid shift counts must be smaller than the word width.',
 [('Cancellation','Use multiplicity guarantees with XOR.'),('Set-bit iteration','Remove one set bit per step.'),('Bit recurrence','Relate counts to a smaller integer.')],
 ['What multiplicities are guaranteed?','Is the integer signed, and how many bits does it have?'],
 ['Pair cancellation fails when the stated multiplicities do not hold.','Shifting by the word width or using an overflowing signed mask is unsafe.'],
 [step('12 is binary 1100; clear its lowest set bit to get 1000.', ['1100','1000'],[0,1]),step('Clear again: 0000; counted two set bits.', ['1000','0000'],[0,1])],[136,191,338,268,190])
]

def get_lessons():
    registry = {p.metadata.leetcode_id: p for p in get_registry()}
    if len({l.id for l in LESSONS}) != len(LESSONS):
        raise ValueError('Duplicate lesson identity')
    for item in LESSONS:
        if not all(n in registry for n in item.related_questions):
            raise ValueError('Lesson references an unknown official question')
        if not all(registry[n].metadata.primary_pattern in item.patterns for n in item.related_questions):
            raise ValueError('Lesson/question topic mismatch')
    return LESSONS
