# Kmindz target

Added 2026-10-14. Target ID: `kmindz`; default budget: 40 named tokens; mandatory count: 32. Both `generate` and `import` can select it, and it joins all default targets. No existing/native/public output is overwritten or activated by adding this target.

## Output contract

The operator supplied a `KMINDS.json` example with `kind = kmind.theme-package`, package/theme `schemaVersion = 1`, nested variants/tokens, edges, relations, rounded node shape, rainbow palette, depth rules, and encoded preview thumbnail. Its exact JSON is retained at `apt_theme/templates/kmindz-template.json` and bundled by the existing `templates/*.json` package-data rule. The exporter lives in `apt_theme/kmindz.py` and is dispatched from `targets.py`.

Each target folder contains:
- `KMINDS.json`: package identity, descriptions, dark variant, four depth rules, and 244×96 encoded SVG thumbnail.
- `preview.svg`: the same authored thumbnail, for offline inspection. This is not a native app screenshot or Kmindz layout rendering.
- `format-provenance.json`: supplied-contract template hash and acceptance limits.
- `tokens.json` and `validation.json`: semantic origins, aliases, omissions, actual checks, and pending native acceptance.
- `apt-<theme>-kmindz-palette.toml` and matching `-swatch.png`: common per-target provenance artifacts. Canonical source colors remain a separate unchanged 32-entry palette.

Identity is `<theme-slug>-canonical32`, and the visible name is `<theme name> · Canonical 32`; the BlackGold example's identity/colors are never reused for unrelated inputs. Timestamp fields use 0 as an explicit unspecified reproducibility marker, not the wall-clock time or the sample's creation time. Exporting an identical input/name is deterministic.

## Mapping and policy

The current pipeline is dark-only, so the light variant is intentionally omitted. Geometry, fonts, line widths, depth predicates, rule priority, and route types retain the supplied dark template's values. Primary/secondary roles drive hierarchy colors; fills are hue-preserving dark derivations, and text is checked in normal/selected states. Base paint fields, depth overrides, 12 rainbow entries, background, and thumbnail colors all reference actual mapped target tokens. No colors are copied from the sample preview.

The common 22-token nonterminal base is extended with ten consumed hierarchy tokens. Budgets below 32 fail rather than truncate required fields. Text checks target 4.5:1 and edges 3:1. Selected-state checks cover the actual shared text/fill combinations. Style-rule/rainbow precedence inside Kmindz cannot be established from the sample alone.

## Generate a reviewed local package

```powershell
./Invoke-AptTheme.ps1 import assets/references/Aptlantis-Black-Gold/palette.toml --output pilot/kmindz-new --targets kmindz --strict
```

Use a fresh output path. Review `KMINDS.json`, the hierarchy preview, palette, and findings before importing. The generic review page links the package and preview.

## Acceptance limits

Automated checks cover supplied-contract shape, dynamic identity, dark-only policy, token/color membership, normal/selected text contrast, determinism, canonical preservation, budget rejection, common artifacts, both CLI paths through the pipeline suite, and bundled resource availability.

The supplied example is the available format authority; an independent authoritative application schema was not supplied. Native import, handling of a dark-only variants object and unspecified timestamps, layout, rainbow/rule precedence, rendering, edit/save/reopen, and application-version compatibility remain unverified. Do not label this as installed or application-accepted until those gates are exercised. Existing hosted themes are not regenerated or published in this pass.
