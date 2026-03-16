## Audit (sub)agent prompt

You are simulating an AI agent that just had the ppt-cli skill loaded for a new presentation task. Read the skill instruction files in EXACTLY the order a runtime agent would encounter them, and ONLY those files. Do not read any other files in the repository.

**Reading order (follow this exactly):**

1. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/SKILL.md` — the skill entry point
2. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/protocol.md` — SKILL.md says to read this before starting any task
3. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/design-system.yaml` — protocol.md S2 says to read this for design directions
4. One direction file, e.g. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/3-design-business.yaml` — loaded after direction choice
5. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/image-gen.md` — SKILL.md says to read this when images are needed
6. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/speaker-notes.md` — loaded at build time
7. `/home/andreid/Projects/Devbox/cli-tools/ppt-cli/ppt_cli/skill/build-template.sh` — loaded at build time for composition patterns

Read each file carefully and completely. After reading ALL of them, provide a detailed report covering:

1. **Contradictions** — Do any files contradict each other? Are there instructions in one file that conflict with instructions in another?
2. **Broken references** — Does any file reference another file, section, or concept that doesn't exist or is named differently?
3. **Ambiguities** — Are there instructions that could be interpreted in multiple ways, especially around turn boundaries, when to ask vs. act, or what goes where?
4. **Missing information** — Are there gaps where a runtime agent would need to make assumptions? Especially around the new build script workflow and the plan file structure.
5. **Flow coherence** — Does the overall flow (SKILL.md → user experience steps → plan → build script → QA) make sense end-to-end? Are the handoffs between planning and execution clear?

Be thorough and critical. Flag anything that might cause the agent to do the wrong thing, skip a step, bundle actions that should be sequential, or produce a plan/script that doesn't match intent.
