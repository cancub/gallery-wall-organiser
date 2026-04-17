# gallery-wall-organiser

Automatically arrange photos on a gallery wall for visual balance.

Given a wall, a set of photo sizes, and fixed obstacles to avoid (light switches, vents, etc.), this tool finds the optimal placement of all photos such that:

- The gap between edges of adjacent photos is **uniform**
- Photo area is **balanced across four quadrants** (split at the wall's horizontal center and eye level)
- No photos overlap each other or obstacles
- Gaps around obstacles are as **even as possible**

## How It Works

The optimizer uses **simulated annealing** to search for photo placements that minimize quadrant imbalance and gap variance while satisfying all hard constraints (no overlaps, within wall bounds, uniform spacing).

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
gallery-wall-organiser --wall 2400 1800 \
                       --photos 400 300  500 400  300 300 \
                       --obstacles 100 900 80 120 \
                       --eye-level 1450
```

- `--wall H W` — wall dimensions in mm
- `--photos H1 W1 H2 W2 ...` — photo dimensions (height, width pairs)
- `--obstacles X Y H W ...` — obstacle position and size (x, y, height, width groups)
- `--eye-level` — height of eye level in mm (default: 1450)

## Output

Produces a scaled diagram of the wall showing photo placements, obstacles, and quadrant lines.

![example output](docs/example.png)

## Inputs

| Input | Format | Notes |
|-------|--------|-------|
| Wall | height × width | Single rectangle |
| Photos | list of (height, width) | Orientation fixed as given |
| Obstacles | list of (x, y, height, width) | Position fixed |
| Eye level | single value | Vertical coordinate for quadrant split |

## Algorithm

1. Photos are placed in an initial grid layout
2. Simulated annealing iteratively perturbs placements
3. Cost function penalizes overlap, out-of-bounds, gap variance, and quadrant imbalance
4. Final layout is rendered with matplotlib

## Requirements

- Python 3.10+
- numpy
- scipy
- shapely
- matplotlib

## License

AGPL-3.0 License
