"""Natural-language rendering of benchmark graphs (design: docs/renderer-design.md).

Model-free parts only: prompt construction, response validation, the system / eval
view split, leakage checks and review sheets. No API client lives here until the
renderer budget is approved.
"""
