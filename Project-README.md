# Logos-And-Theming

CTS project group for image-derived dark themes and related logo tooling. The package and utilities share this directory; SESM embedding remains a separate sibling project.

Detailed overview: [Black-Gold slide deck](docs/presentations/Logos-And-Theming-Overview.pptx). Planned deep dives, ownership and authoring sequence: [documentation suite plan](docs/documentation-suite/PLAN.md).

Implementation and setup: README.md. Intent: Project-Proposal.md. Contracts: docs/COMMAND-CONTRACT.md. Verification: docs/VALIDATION.md and migration/acceptance.json. Recovery: migration/README.md and hash-verified archives.

Default dark surfaces now preserve an image hue instead of automatically using the darkest canonical color. Background and near-black selection policies, explicit opt-ins and the separately preserved comparison run are documented in README.md and migration/dark-surface-regression.json.

The PowerPoint metadata repair is documented in docs/POWERPOINT.md and migration/powerpoint-metadata-repair.json, including native opening without repair, recoverable originals and a utility for correcting older copies.

Current targets are Windows Terminal, SiYuan, Typora and PowerPoint colors with an editable sample deck. Existing Notepad++/JetBrains and other outputs are historical, not new exporters. Local structural and contrast evidence does not establish application installation, visual acceptance, distribution or release readiness. PowerPoint setup and the sample deck acceptance boundary are in docs/POWERPOINT.md.
