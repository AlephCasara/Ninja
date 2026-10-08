# Claude Code guidance

Read `AGENTS.md` before making changes.

This repository exposes a project-scoped MCP server in `.mcp.json` named `ninja-tooling`. It currently provides the canonical external-tool catalog and local environment diagnostics. Use those capabilities before assuming a crawler, browser, archive, data, semantic, statistical or backtesting tool is installed.

Do not expand the MCP server into arbitrary shell execution. New tool access should be implemented as typed capability adapters documented in `docs/NINJA_TOOLS.md`.
