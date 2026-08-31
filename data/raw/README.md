# Raw data policy

Files under `data/raw/legacy/` are immutable copies of the retained undergraduate project
spreadsheets. The pipeline reads but never modifies them. The original Word, PDF, PowerPoint,
and Python files are not copied because they include personal identifiers and a hard-coded
Taobao session cookie. Their reusable analytical logic is documented in
`docs/legacy_code_audit.md` and reimplemented in `src/` without credentials.

External source snapshots are also immutable. Public repository preparation excludes raw HTML,
third-party workbooks, the published crawler, and the local human-annotation worksheet by default.
Their provenance and hashes remain documented. This protects legacy personal information and
avoids applying the project's MIT license to third-party content.

The full pipeline therefore runs from the authorized local project directory. A public clone is a
code-and-results portfolio unless the source files are restored to the paths documented in each
`PROVENANCE.md` file.
