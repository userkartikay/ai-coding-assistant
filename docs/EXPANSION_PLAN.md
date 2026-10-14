# Curriculum and learning increment

User-authorized scope: expand the catalogue to 120–150 entries, add reviewed starter
lessons and optional grounded code review, and consistently show official LeetCode
numbers. This increment precedes the deferred persistence milestone.

1. Verify number/title/slug/difficulty against LeetCode's public catalogue; preserve
   an exact snapshot of the original 53 records and all existing internal IDs.
2. Add curated catalogue-only entries, original summaries, and explicit unavailable
   constraints/signatures. Add identity, preservation, search and sorting tests.
3. Build reusable lesson data, representative walkthroughs and visual step controls;
   connect official-number practice links without changing independent-mode defaults.
4. Add optional structured approach/alternative review and grounded lesson questions
   using the existing bounded Ollama client and shared single-model request lock.
   No execution or generated-code compilation. Hint Only keeps the existing tier gate.
5. Integrate navigation, verify automated and live model behavior separately, update
   roadmap/decisions, and stop for hands-on testing.

New questions remain catalogue-only: metadata verification is not harness verification.
No database migration or draft-key rename is necessary; existing `lc_<number>` keys
and SQLite LeetCode fields already provide the requested canonical identity.
