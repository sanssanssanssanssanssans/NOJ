# Pull Request Guide

This document describes the rules and workflow for contributing to the NOJ project via Pull Requests (PRs).

## 1. Before You Start
- **Search existing issues/PRs** to avoid duplicates.
- **Open an Issue** first if your PR is a new feature or major change.
- **Small fixes** (typos, comments, docs) can be submitted directly as PRs.

## 2. Branching
- Do **not** push directly to `main` or `master`.
- Use the following naming convention:
  - `feature/<short-description>`
  - `bugfix/<short-description>`
  - `docs/<short-description>`
- Example: `feature/contest-ranking`, `bugfix/python-timeout`, `docs/problem-setup`

## 3. Commit Rules
- Follow conventional commit style if possible:
  - `feat: add ranking system`
  - `fix: correct JSON signature migration`
  - `docs: update A-B problem setup`
- Keep commits small and focused.
- Squash trivial commits before PR submission.

## 4. PR Description
Each PR must include:
1. **Summary**: What the PR does.
2. **Related Issue**: Link to issue number if applicable.
3. **Changes**:
   - Added
   - Changed
   - Removed
   - Fixed
4. **Testing**: How you verified it works (unit tests, manual runs, screenshots).
5. **Checklist**:
   - [ ] Code builds without errors
   - [ ] Tests added/updated if necessary
   - [ ] Docs updated if necessary

## 5. Code Style
- Python: follow **PEP8**.
- HTML/CSS/JS: use 2 spaces indentation.
- Consistency with surrounding code is more important than strict rules.

## 6. Review Process
- At least **1 approval** is required before merge.
- CI checks must pass (lint, tests).
- Reviewers may request changes. Please update commits instead of opening a new PR.

## 7. Merging
- **Squash and Merge** is recommended to keep history clean.
- PR title should be descriptive enough to serve as the squash commit message.

## 8. Security & Data
- Do not commit secrets (API keys, passwords).
- Do not upload testcases that reveal real contest problems.
- Sensitive config (e.g., `.env`) must be excluded.

## 9. Documentation
- If your PR changes user-facing behavior, update:
  - `/docs/` guides
  - Related templates in `/templates/`
- Use plain Markdown, no rendering required.

## 10. Communication
- Use English for commits, PR titles, and discussions.
- Be polite and constructive in reviews.

---