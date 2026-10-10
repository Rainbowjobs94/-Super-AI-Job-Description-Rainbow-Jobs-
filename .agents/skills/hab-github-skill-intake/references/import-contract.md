# Import contract

Inspect layout before concluding the source is invalid. A GitHub repo is not
required to be authored as a skill in order to supply useful documentation.
Keep original, normalized and proposed representations separate.

Example valid wrapper:

    ---
    name: reviewed-project-guidance
    description: Apply reviewed guidance from an identified project. Use for its specific integration after reading the host instructions.
    ---
    # Reviewed project guidance
    Source: identified repo and commit; files read: README and relevant docs.
    Status: proposed wrapper, not installed.
    Steps: inspect capabilities; reuse observed entry points; verify changes.
    Limits: no installer execution, provider activation or release authority.

Required manifest fields: source URL/revision; source path; SHA256 of actual
packaged bytes; read status; extraction bounds; rights; excluded sensitive
paths; wrapper name/version; host target; activation status; tested checks.

Fail closed on traversal, symlinks, secret-bearing paths, ambiguous overwrites
and unapproved executable behavior. Missing metadata calls for repair guidance,
not silent deletion or generic rejection.
