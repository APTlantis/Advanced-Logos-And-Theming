-- Illustrative analysis; table names are example contracts.
WITH observed AS (
    SELECT
        palette_id,
        color_id,
        SUM(pixel_count) AS population
    FROM color_observations
    WHERE alpha > 0
      AND observed_at >= DATE '2026-01-01'
    GROUP BY palette_id, color_id
), ranked AS (
    SELECT
        palette_id,
        color_id,
        population,
        ROW_NUMBER() OVER (
            PARTITION BY palette_id
            ORDER BY population DESC, color_id
        ) AS color_rank
    FROM observed
)
SELECT
    p.name,
    r.color_id,
    r.population,
    CASE WHEN r.color_rank <= 32 THEN 'candidate' ELSE 'reserve' END AS status
FROM ranked AS r
INNER JOIN palettes AS p ON p.id = r.palette_id
WHERE p.illustrative = TRUE
ORDER BY p.name, r.color_rank;
