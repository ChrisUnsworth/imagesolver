# Image Puzzle Solver

A web application that uses Claude's vision AI to detect and analyse puzzle images, then solves them using Google OR-Tools optimisation models. Upload an image of a supported puzzle and get an instant solution.

## Supported Puzzles

| Puzzle | Detection | Analysis | Solver |
|---|---|---|---|
| **Sudoku** | Claude vision | Claude vision | OR-Tools MIP (SCIP) |
| **LinkedIn Queens** | Claude vision | Claude vision | OR-Tools CP-SAT |

More puzzle types can be added by following the conventions in the [project structure](#project-structure) below.

## How It Works

```
Upload image
     │
     ▼
┌─────────────────────┐
│  Puzzle Detector    │  Claude vision classifies the puzzle type
└─────────────────────┘
     │
     ├── sudoku ──▶  Sudoku Analyser  ──▶  Sudoku Solver  ──▶  9×9 solution grid
     │               (Claude vision)       (OR-Tools MIP)
     │
     └── queens ──▶  Queens Analyser  ──▶  Queens Solver  ──▶  N×N solution grid
                     (Claude vision)       (OR-Tools CP-SAT)
```

### Sudoku

The analyser reads the 9×9 grid from the image and returns which cells are filled and their values. The solver uses a **Mixed Integer Programming (MIP)** formulation with 729 binary variables (`x[i,j,d] = 1` if cell `(i,j)` contains digit `d`) and four sets of constraints (one digit per cell, row, column, and 3×3 box).

### LinkedIn Queens

The analyser reads the N×N coloured-region grid from the image and assigns integer region IDs. The solver uses a **CP-SAT** constraint programming model with one boolean variable per cell and four constraint families:
1. Exactly one queen per row
2. Exactly one queen per column
3. Exactly one queen per coloured region
4. No two queens adjacent (including diagonally)

## Project Structure

```
imagesolver/
├── app.py                        # Flask web application & routing
├── detectors/
│   └── puzzle_detector.py        # Classifies uploaded image by puzzle type
├── analyzers/
│   ├── sudoku_analyzer.py        # Reads sudoku grid from image via Claude
│   └── queens_analyzer.py        # Reads Queens colour regions from image via Claude
├── solvers/
│   ├── sudoku_solver.py          # Solves sudoku via OR-Tools MIP
│   └── queens_solver.py          # Solves Queens via OR-Tools CP-SAT
├── templates/
│   └── index.html                # Single-page UI
├── uploads/                      # Saved uploaded images (Docker volume)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- An [Anthropic API key](https://console.anthropic.com/)

## Getting Started

**1. Clone the repository**

```bash
git clone <repo-url>
cd imagesolver
```

**2. Add your Anthropic API key**

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

**3. Build and run**

```bash
docker compose up --build
```

**4. Open the app**

Navigate to [http://localhost:5000](http://localhost:5000), upload a puzzle image, and click **Analyse & Solve**.

## Adding a New Puzzle Type

1. **Register the type** — add an entry to `KNOWN_TYPES` in [detectors/puzzle_detector.py](detectors/puzzle_detector.py) and update the prompt.
2. **Create an analyser** — add `analyzers/<puzzle>_analyzer.py` with an `analyze_<puzzle>(image_path)` function that returns a structured dict.
3. **Create a solver** — add `solvers/<puzzle>_solver.py` with a `solve_<puzzle>(data)` function that returns the solution.
4. **Wire up the route** — add a branch in `app.py` for the new puzzle type.
5. **Display the result** — add a section in `templates/index.html`.

## Tech Stack

| Component | Technology |
|---|---|
| Web framework | [Flask](https://flask.palletsprojects.com/) |
| Vision AI | [Claude claude-sonnet-4-6](https://www.anthropic.com/) via Anthropic Python SDK |
| Optimisation | [Google OR-Tools](https://developers.google.com/optimization) (MIP + CP-SAT) |
| Container | Docker + Docker Compose |
