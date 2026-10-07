# Installation

The skill is a directory named **`echarts-json`** containing `SKILL.md` and its
supporting resources. It follows the [Agent Skills specification](https://agentskills.io/specification).
In this repository, that complete folder is **[skills/echarts-json/](../skills/echarts-json)**.
Install only this folder; tests, reports, CI, and development tools stay in the repository.
There is no model-specific executable, MCP server, or API credential requirement.

## Skills CLI

The [skills CLI](https://github.com/vercel-labs/skills) can discover this repository's
`skills/echarts-json/SKILL.md` and install that folder. Run from your application/project root:

```bash
npx skills add Exilitys/echartsSkill --skill echarts-json --copy
```

Select the desired agents. To select targets without an interactive agent picker:

```bash
npx skills add Exilitys/echartsSkill --skill echarts-json \
  --agent codex claude-code cursor opencode gemini-cli github-copilot windsurf \
  --copy --yes
```

These are installer target IDs, not model names. Choose only the agents you want
to use. The CLI can place several targets in a shared `.agents/skills` location.
`--copy` avoids requiring symlink support. The CLI requires Node.js and Git;
the skill itself does not.

To inspect discovery before installing:

```bash
npx skills add Exilitys/echartsSkill --list
```

For user-wide installation, the CLI supports `--global`. It selects the target
agent's configured user directory; compare that location with your installed
agent version's discovery rules. The manual table below gives documented default
paths and makes the destination explicit.

## Manual Git and copy installation

Clone the repository into a checkout, then copy its `skills/echarts-json` folder
to one of these destinations. Paths are relative to the application/project
unless they begin with `~`.

| Agent | Project destination | User-wide destination | Official guide |
| --- | --- | --- | --- |
| Codex | `.agents/skills/echarts-json` | `~/.agents/skills/echarts-json` | [Codex skills](https://developers.openai.com/codex/skills/) |
| Claude Code | `.claude/skills/echarts-json` | `~/.claude/skills/echarts-json` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Cursor | `.cursor/skills/echarts-json` | `~/.cursor/skills/echarts-json` | [Cursor skills](https://cursor.com/docs/skills) |
| OpenCode | `.opencode/skills/echarts-json` | `~/.config/opencode/skills/echarts-json` | [OpenCode skills](https://opencode.ai/docs/skills/) |
| Gemini CLI | `.gemini/skills/echarts-json` | `~/.gemini/skills/echarts-json` | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |
| GitHub Copilot | `.github/skills/echarts-json` | `~/.copilot/skills/echarts-json` | [Copilot skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills) |
| Windsurf / Devin Desktop | `.devin/skills/echarts-json` (current) or `.windsurf/skills/echarts-json` (legacy) | `~/.config/devin/skills/echarts-json` or `~/.codeium/windsurf/skills/echarts-json` | [Cascade skills](https://docs.devin.ai/desktop/cascade/skills) |

For example, a new project-local Claude Code install is:

```bash
git clone https://github.com/Exilitys/echartsSkill.git echartsSkill
mkdir -p .claude/skills
cp -R echartsSkill/skills/echarts-json .claude/skills/
```

Codex, Cursor, OpenCode, and Gemini CLI document compatible `.agents/skills`
locations. Use the native path above when you want a separate copy for one tool.
Respect configured custom directories and `XDG_CONFIG_HOME` when they apply.
The skills CLI's `windsurf` target uses the compatible legacy `.windsurf/skills`
path; newer Devin Desktop installations also read it and `.agents/skills`.
User-wide skills may stay local to a machine; remote or cloud agents generally
need the skill in their own environment or project checkout.

On Windows, these project-relative paths work with Git and PowerShell. For a
user-wide path, use the corresponding folder under your actual user directory
or let the skills CLI select it. Copy installation does not require symlinks.
For example, use `New-Item -ItemType Directory -Force .claude/skills` and
`Copy-Item -Recurse echartsSkill/skills/echarts-json .claude/skills/` in PowerShell.

## ZIP installation and packaging

Download **Code → Download ZIP** on GitHub, extract the repository, and copy its
`skills/echarts-json` folder into the desired skill directory.
Do not create an extra nested `echarts-json/echarts-json` layer.

To create a portable archive with a correctly named top-level folder:

```bash
python scripts/package_skill.py --output dist/echarts-json.zip
```

Extract the resulting `echarts-json` folder into the skill directory. If an agent
UI supports uploading skill archives, use its documented upload flow; filesystem
installation instructions do not imply that every chat interface accepts ZIPs.
The generated archive contains only the skill resources and license; repository
tests, reports, documentation, and packaging/development files are excluded.

## Confirm the installation

1. Check that `<skill-directory>/echarts-json/SKILL.md` exists and that
   `references/`, `examples/`, and `scripts/` are beside it.
2. Restart the agent or reload skills using its supported command if discovery
   has already run. Gemini CLI provides `/skills reload`; Claude Code provides
   `/echarts-json` invocation; Codex can use `$echarts-json` or its skill selector.
3. Ask: “Use the echarts-json skill to create a native Streamlit bar chart from
   categories A, B, C and values 12, 18, 9. Return only strict JSON.”
4. Optionally validate that output using the installed `scripts/validate_option.py`.

The repository verifies skill discovery and file installation through the skills
CLI. It does not execute models inside every target agent; activation settings,
permissions, and remote syncing remain the responsibility of the chosen host.

## Update or remove

For a manual Git-and-copy installation, update the source checkout and copy its
`skills/echarts-json` folder into the installed location again:

```bash
git -C echartsSkill pull --ff-only
```

For a CLI-managed installation:

```bash
npx skills update echarts-json
npx skills remove echarts-json --agent codex
```

Use the CLI's scope and agent flags if you installed globally or to several
agents. For a manual copy/ZIP install, replace or remove only the `echarts-json`
folder you installed. Keep any intentional local modifications before replacing
an existing copy.

## Updating older installations

Versions before 1.2 kept `SKILL.md` at the repository root. If you cloned that
repository directly into an agent's skill directory, a Git update now puts the
entrypoint under `skills/echarts-json`. Reinstall using the CLI, or replace the
old installed directory with just that folder from the updated checkout. Preserve
any intentional local edits before replacing an existing installation.

The CLI installation command and skill name remain unchanged. A new installation
has `SKILL.md` immediately inside the installed `echarts-json` directory, without
the repository's extra `skills/` prefix or development files.
