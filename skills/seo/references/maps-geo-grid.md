<!-- Updated: 2026-09-25 -->
# Geo-Grid Rank Tracking Algorithm

## Concept

Geo-grid rank tracking simulates Google Maps searches from multiple GPS
coordinates around a business to show how rankings vary across a geographic
area. The output is a heatmap revealing where the business ranks well (green)
and where competitors dominate (red).

---

## Grid Generation (Haversine-Based)

### Algorithm

1. Take center coordinates (business location): `center_lat`, `center_lng`
2. Define grid size (e.g., 7x7 = 49 points) and radius in km
3. Calculate spacing: `step = (2 * radius_km) / (grid_size - 1)`
4. Generate grid points using offset formula:

```
For each row i (0 to grid_size-1) and column j (0 to grid_size-1):
  dy = (i - center_index) * step_km
  dx = (j - center_index) * step_km
  new_lat = center_lat + (dy / 111.32)
  new_lng = center_lng + (dx / (111.32 * cos(center_lat * pi/180)))
```

Where `center_index = (grid_size - 1) / 2` and `111.32 km = 1 degree latitude`
(equirectangular approximation; accurate enough at grid scale).

Grid points go to DataForSEO as coordinates. Never reverse-geocode grid points through the
public Nominatim server: its usage policy forbids "reverse queries in a grid".

### Grid Sizes and Use Cases

Sizes and radii are heuristics [H]; costs are Maps SERP live prices [V] (2026-09-25).

| Grid | Points | Typical Radius [H] | Best For [H] | Est. Cost (Live) |
|------|--------|---------------|----------|-----------------|
| 3x3 | 9 | 2 km | Quick snapshot, low budget | $0.018/keyword |
| 5x5 | 25 | 3 km | Standard urban audit | $0.050/keyword |
| **7x7** | **49** | **5 km** | **Default (editorial choice)** | **$0.098/keyword** |
| 9x9 | 81 | 8 km | Suburban/wide service area | $0.162/keyword |
| 13x13 | 169 | 15 km | Rural or large metro | $0.338/keyword |

**Radius guidelines (heuristic):** Urban dense = 2-5 km, suburban = 5-10 km, rural = 10-25 km.

---

## DataForSEO Integration

Use the Google Maps SERP API with `location_coordinate` parameter:

```json
{
  "keyword": "dentist",
  "location_coordinate": "30.2672,-97.7431,15z",
  "language_code": "en",
  "device": "mobile",
  "depth": 20
}
```

For each grid point, send one task with the point's lat/lng. Find the target business
(match `cid` or `place_id`) among `maps_search` items and use its `rank_group`; skip
`maps_paid_item` ads.

**Batching:** a **live** call carries only one task, so a live 7x7 grid is 49 calls (limit
2,000 calls/min). To batch, use the standard queue: `/v3/serp/google/maps/task_post` accepts
up to 100 tasks per POST (all 49 in one request), then collect results with `task_get`.
Standard is cheaper ($0.0006 vs $0.002) but can take up to 45 minutes.

---

## Share of Local Voice (SoLV)

SoLV® is Local Falcon's registered trademark. Local Falcon defines it as how often a
business ranks in the top three positions across a scan [V Local Falcon KB32, updated
2025-11-20]. Other tools may define it differently.

### Calculation

```
SoLV = (points_in_top_3 / total_grid_points) * 100
```

### Interpretation (heuristic bands [H])

Neither Google nor Local Falcon publishes SoLV bands. These are editorial cut-offs: label them
"heuristic" in output and cap any finding based on them at Medium. Compare against competitors
in the same scan (Local Falcon's own advice), not against a fixed scale.

| SoLV | Interpretation |
|------|---------------|
| 80-100% | Dominant in the scanned area |
| 60-79% | Strong: visible in most of the area |
| 40-59% | Moderate: significant gaps |
| 20-39% | Weak: competitors lead most points |
| 0-19% | Very weak: rarely in the top 3 |

### Extended Metrics

- **Average Rank**: Mean position across all grid points (lower = better)
- **Visibility Score** [H]: Weighted average where top 3 = 3pts, 4-10 = 1pt, 11+ = 0pts
- **Worst Quadrant**: Identify which compass direction has weakest rankings

---

## ASCII Heatmap Rendering

For terminal/Markdown output, render a grid using rank-position symbols:

### Format

```
Geo-Grid: "dentist" (7x7, 5km radius, center: 30.267, -97.743)

     W -------- E
  N  1  1  2  3  5  8  -
  |  1  1  1  2  3  6  9
  |  2  1  [1] 1  2  4  7
  |  3  2  1  1  1  3  5
  |  5  3  2  1  2  4  8
  |  8  5  3  2  3  6  -
  S  -  8  5  4  5  9  -

Legend: [1]=center, 1-3=top 3 (strong), 4-10=visible, -=not ranked
SoLV: 59% (29/49 grid points in top 3)
Avg Rank: 3.6 (45 ranked points) | Weakest: south row (avg rank 6.2, 2 points unranked)
```

(Invented example data; the summary lines are computed from this grid.)

### Color Mapping (for enhanced output)

| Position | Symbol | Meaning |
|----------|--------|---------|
| 1 | `1` | #1 ranking (best) |
| 2-3 | `2`, `3` | Top 3 (strong local presence) |
| 4-10 | `4`-`9` | Visible but not dominant |
| 11-20 | `+` | Buried in results |
| Not found | `-` | Not ranking at this point |

---

## Multi-Keyword Grid

For comprehensive analysis, scan 2-3 keywords on the same grid:

1. Primary service keyword (e.g., "dentist")
2. Brand + location (e.g., "Smith Dental Austin")
3. Long-tail intent (e.g., "emergency dentist near me")

**Cost for 3-keyword 7x7 scan:** 147 tasks = ~$0.29 (live) or ~$0.088 (standard queue, up to 45 min)

---

## Cost Warning Template

Before running a geo-grid scan, display:

```
Geo-Grid Scan Estimate:
  Grid: 7x7 (49 points)
  Keywords: 3
  API calls: 147
  Estimated cost: $0.09 (standard) - $0.29 (live)
  Proceed? [DataForSEO credits will be consumed]
```
