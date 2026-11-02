## 2026-11-02

### Removed
- `upload.js` — PAT-based bulk uploader, retired.

  Reason: the script walks the working directory without honouring
  `.gitignore`, so any credential file placed there would be published
  to this public repository. No PAT remains in use; GitHub Desktop
  (OAuth) replaces it.

  Not a retraction: all 23 files it uploaded remain in git history and
  are still referenced by README / claims. Deletion affects only the
  current tree.
  