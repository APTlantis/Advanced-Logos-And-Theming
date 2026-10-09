#!/usr/bin/env bash
# Read-only illustrative source listing; displayed, not run.
set -euo pipefail

readonly EXPECTED_COUNT=32
labels=("Observed colors" "Semantic roles" "Target tokens")
source_dir="${1:-./source}"

describe_file() {
    local file="$1"
    local name="${file##*/}"
    printf 'Source: %s\n' "$name"
    if [[ -f "$file" ]]; then
        wc -c < "$file"
    else
        printf 'Missing source\n' >&2
        return 1
    fi
}

for label in "${labels[@]}"; do
    printf '%s / expected %d colors\n' "$label" "$EXPECTED_COUNT"
done

if [[ -d "$source_dir" ]]; then
    find "$source_dir" -maxdepth 1 -type f -print |
        while IFS= read -r file; do
            describe_file "$file"
        done
else
    printf 'No source directory: %s\n' "$source_dir" >&2
fi
