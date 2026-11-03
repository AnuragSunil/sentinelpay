# Bob Log

Rolling log of every change Bob makes. Newest entry at the TOP.

## Rules for this log

1. Bob adds exactly ONE new entry at the top at the end of every prompt (below this header, above older entries).
2. Entries use EXACTLY this format, max ~12 lines:

   ```
   ## B-<next number> | <YYYY-MM-DD> | <short title>
   - Prompt (1 line): <what the owner asked>
   - Created: <paths or "none">
   - Modified: <paths + 1-line reason each, or "none">
   - Deleted: <paths or "none">
   - Dependencies added: <name + version + why, or "none">
   - Decisions/assumptions: <anything Bob chose that the owner did not specify>
   - Not done / follow-ups: <honest list>
   - How to verify: <commands or steps the owner can run>
   ```

3. Log only what was actually done. If a step failed or was skipped, say so.
4. Keep only the 10 newest entries here. When there are more than 10, move the oldest entries to `docs/bob/archive/<YYYY-MM>.md` (append, do not rewrite).
5. Never delete log history.
6. Never write secrets, keys, tokens, or passwords in this log.

---

## B-001 | 2026-11-03 | Create Bob docs scaffolding
- Prompt (1 line): Create docs/bob/PROJECT_CONTEXT.md, docs/bob/BOB_LOG.md, and docs/bob/archive/ with .gitkeep, and nothing else.
- Created: docs/bob/PROJECT_CONTEXT.md, docs/bob/BOB_LOG.md, docs/bob/archive/.gitkeep
- Modified: none
- Deleted: none
- Dependencies added: none
- Decisions/assumptions: Workspace was empty, so PROJECT_CONTEXT.md and the log did not exist to read at start (rule A). Repo layout lists the intended folders and notes they do not exist yet. "Tech decisions" left as an empty list with a comment. Rules A-K were split between Conventions and Do-not list; rule B's entry format lives in this header.
- Not done / follow-ups: Owner to fill in "Tech decisions". No code, build, or git commands were run. No .gitignore was created (not requested).
- How to verify: `git status` shows only the 3 new files under docs/bob/; open the files and compare with the prompt; `Get-ChildItem -Force docs/bob/archive` shows .gitkeep.
