# Theme review hosting

The review hub is publicly served at [themes.aptlantis.net](https://themes.aptlantis.net/) directly from `D:\CTS\Logos-And-Theming\output`. The source directory remains owned by this project. Origin routing and service lifecycle belong to `A:\webserver`; no output assets are copied into `A:\aptlantis.net\dist`.

## Serving contract

`A:\webserver\docker-compose.yml` mounts the output directory read-only at `/srv/aptlantis-themes` in `caddy-aptlantis`. `A:\webserver\Caddyfile` uses a dedicated `http://themes.aptlantis.net:8100` site block. The dashboard-managed Cloudflare application forwards to `http://localhost:8100` with the public Host header; TLS terminates at Cloudflare. The existing website uses the same listener with its previous site block.

The themes route serves `/` and `/index.html`, plus files beneath these exact directories:

`ada`, `blackgold`, `dnf-Clojure`, `dnf-Julia`, `dnf-QBasic`, `dnf-R`, `dnf-Scratch`, `dnf-Zig`

The matcher is `@publishedThemes`. Other paths return 404. Directory browsing and SPA fallback are disabled for this hostname. Recovery bundles, tests, wheel staging and other output folders remain unreachable even though the parent directory is mounted. Missing files within allowed folders also return 404. Responses use `Cache-Control: no-store, max-age=0` and `Cloudflare-CDN-Cache-Control: no-store`.

The host-specific route and exclusive fallback follow [Caddy host matching](https://caddyserver.com/docs/caddyfile/matchers#host) and [handle routing](https://caddyserver.com/docs/caddyfile/directives/handle). The public pages currently receive Cloudflare analytics injection, and the index receives Rocket Loader transformations. Public HTML therefore need not be byte-identical to the origin; the acceptance record compares the authored HTML after those known transformations. Images and PowerPoint downloads were checked byte-for-byte.

## Updates and verification

The user's 2026-10-09 curated index retains eight themes: Ada, Black Gold, Clojure, Julia, QBasic, R, Scratch and Zig. Each card links to `review.html`, `svg/examples.html` and `data_visualization/examples.html`. All 24 page destinations and eight palette images exist locally; index evidence: `migration/curated-index-links-2026-10-09.json`. The user then authorized updating `A:\webserver\Caddyfile`: its allowlist now matches the eight exact folders above. Caddy validation and reload passed; all 24 pages returned HTTP 200 locally and publicly, five removed/recovery/missing paths returned local 404, and the main site's local homepage returned 200. Everything outside the theme allowlist remains unchanged. Delivery evidence: `migration/curated-theme-hosting-2026-10-09.json`; byte-preserved rollback: `migration/Caddyfile-before-curated-index-2026-10-09.txt`. To roll back routing, restore that file to the Caddyfile path, validate, then reload. Theme assets were not regenerated and removed index entries remain absent. Project identity and discovery roots remain unchanged; parent/index registrations need no update. The earlier 16-theme acceptance below remains historical evidence.

Edits to `output/index.html` and files in an approved folder are visible through the live mount. Adding a new theme requires updating both the manually maintained index and the exact folder allowlist in Caddy. Review the directory contents before exposure, then validate and reload the configuration. Generate new runs into fresh directories; the webserver does not build or regenerate theme outputs.

```powershell
curl.exe -H "Host: themes.aptlantis.net" http://127.0.0.1:8100/
docker exec caddy-aptlantis caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
docker exec caddy-aptlantis caddy reload --config /etc/caddy/Caddyfile --adapter caddyfile
```

The 2026-10-09 application added only the read-only mount and the themes site block. Only Caddy was recreated with `--no-deps --pull never`; its persistent volumes and the independent phpBB stack were preserved. The existing site's local homepage remained byte-identical. All 16 reviews and palette images, a PowerPoint download, denied paths and missing-file behavior passed 43 local HTTP checks.

The existing automatic `Cloudflared` Windows service was stopped. It was started without changing credentials, service configuration or dashboard routes. Both public hostnames initially returned error 1033, documented by [Cloudflare as a missing healthy tunnel connector](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/troubleshoot-tunnels/common-errors/#1033-error). Public delivery passed after the service started. Browser checks confirmed the index, filtering to one matching theme, opening a review, and returning to the collection. The retained local `cloudflared-ingress.yml` is historical and was left unchanged.

Measured checks and hashes: `migration/theme-hosting-acceptance.json`. This evidence establishes the tested delivery paths and browser interactions, not native application theme import or release acceptance.

## Recovery and rollback

Original server files are preserved in `migration/theme-hosting-backups/2026-10-09`: `Caddyfile`, `docker-compose.yml`, server `README.md`, `webserver.manifest.toml`, and the A-drive `A-README.md`. Their original hashes are in the acceptance record.

To remove this origin route and mount, restore the two configuration files to their original A-drive paths after checking the backup hashes and reviewing any later edits. Run `docker compose -f A:\webserver\docker-compose.yml --project-directory A:\webserver config --quiet`, then `docker compose -f A:\webserver\docker-compose.yml --project-directory A:\webserver up -d --no-deps --pull never caddy`. Validate the mounted Caddyfile and verify the original website. Restore documentation selectively if appropriate. Do not delete named volumes or stop the tunnel merely to remove this route; the tunnel also serves the existing website.

The A-drive navigation and server consumer record now point here. No D-drive portfolio registration change is needed: project identity, ownership and filesystem root are unchanged.
