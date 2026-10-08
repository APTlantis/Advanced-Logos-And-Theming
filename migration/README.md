# Migration and recovery

The consolidation replaces Aptlantis Logos, Lang-Theme-Generator, the held palette-transformer, and the Advanced-Logos-And-Theming Documents workspace. Artwork and converters belong to Logos-And-Theming; SESM embedding is a sibling project.

`archives/*.zip` preserve every file from each old location, including Git history and working files. Each adjacent JSON records original absolute root, every relative path, file size and SHA-256, archive SHA-256, and full restoration verification. `inventory.json` compares duplicate scripts and records migration status. Runtime environment files in archives are historical bytes and should be recreated rather than reused after relocation.

Active artwork/catalogs retain original filenames beneath `assets`. LangThemeGenerator assets retain their own subtree to avoid collisions. Original palettes and generated themes remain historical evidence. Public website asset bytes are unchanged. The site workflow receives new source/tool paths only.

Recovery: verify a ZIP against its adjacent JSON `archive_sha256`; extract into a fresh directory; compare every restored file against `files` hashes. Use the manifest's `source` if restoring the original location is intentional and that location is absent. Never extract over an active project. The archive retains the original `.git` so history can be restored with the source tree.

`tools/migrate.py stage` creates/restores archives and copies reviewed content. `retire` requires the acceptance gate, rechecks every old source against its original inventory and every archive hash, and rejects symlinks/junctions or changed source files. Old locations are removed only after those checks and documented destination validation.

The Writerside handbook is a dated snapshot. Its historical source identities, comparison hashes and copied resources are intentionally retained; it must not be silently recaptured as current evidence. The new project records provide current discovery paths.
