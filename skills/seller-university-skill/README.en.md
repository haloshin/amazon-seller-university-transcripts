# Seller University Skill

An Amazon course lookup and study assistant: **356 knowledge modules across 13 topic packs**, released together as **1.0.0-beta.2**. 270 modules link to this project's Chinese course reader; 86 have no public transcript page. Modules cover video and document sources, so the module count differs from the 270 video courses in the reader.

[Download the Skill ZIP](https://github.com/haloshin/seller-university/releases/tag/skill-v1.0.0-beta.2) · [中文](README.md)

Ask for explanations, course references, troubleshooting steps, or an SOP based on information you provide. The Skill asks for missing context and distinguishes archived course material from current rules and its own suggestions. It does not operate seller accounts.

## Install

With Node.js/npm and Git installed, open a terminal in your Agent project and run:

```bash
npx skills add https://github.com/haloshin/seller-university --skill seller-university-skill
```

Select Codex or Claude Code, or append `--agent codex` / `--agent claude-code`. The default scope is the current project; `-g` selects the user directory. This installs the repository's current version. The installer can overwrite an existing Skill: back it up and inspect the destination before confirming. Python 3.10+ is needed for local search; without Python, browse [the topic index](references/INDEX.md).

<details>
<summary>Install the fixed-version ZIP instead</summary>

Extract `seller-university-skill-1.0.0-beta.2.zip`, then run these commands from its `seller-university-skill` folder. Python 3.10+ is required; no third-party Python packages or author-hosted API are required.

```bash
python3 scripts/install.py --agent codex
python3 scripts/install.py --agent codex --apply
```

The first command only previews the destination. Replace `codex` with `claude` for Claude Code, or use `--target <skills-parent-directory>`. Only `--apply` copies files. Existing targets and symlink paths are refused. Back up the old folder explicitly before upgrading; restore that backup to roll back. Start a new Agent session after installation.

Example: “Use seller-university-skill to explain Sessions versus Page views and link to the relevant course.”

</details>

Start a new session in the project and ask:

```text
Use seller-university-skill. Explain Amazon Sessions versus Page views,
and give the relevant course links and sources.
```

## Scope and limitations

Includes the Skill instructions, local search and installer, 356 module notes with source anchors, 13 packs, usage examples and behavioral test prompts. No video files, PDFs, knowledge-card collection or course question bank are included. The v0.9.2 reader ZIP does not include this separately packaged Skill.

The course snapshot is dated July 27, 2026. Fees, eligibility, budgets and policies require current official verification. The search script is offline; it does not update courses or verify current policies. Official links may require login, and unavailable/unverified links are labeled. Not every course playback has been tested.

Temporary-directory installation and search are tested; Agent simulations do not constitute WorkBuddy, Windows or end-user acceptance. See [validation scope](VALIDATION.md).

Maintained by SHIN, independently of Amazon. Program code is MIT-licensed; original editorial content has the project's limited-use permission, and third-party course content is not relicensed. See [LICENSE](LICENSE) and [NOTICE](NOTICE.md).
