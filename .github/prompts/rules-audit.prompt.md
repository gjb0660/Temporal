---
description: "Use when: auditing repository agent customization files for path correctness, frontmatter validity, applyTo precision, and conflicting instruction sources."
---

Audit all repository customization files and return:
1. Invalid paths and expected target paths.
2. Frontmatter issues (missing description/applyTo/name conflicts).
3. Content overlap or conflicts between workspace instructions.
4. Concrete patch plan with minimal edits.
5. Validation checklist after fix.
