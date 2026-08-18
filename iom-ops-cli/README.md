# IOM Operations Diagnosis CLI

Command-line interface for the IOM Operations Diagnosis Agent.

## Installation

```bash
pip install -e .
```

## Usage

After installation, use the `iom-ops` command:

```bash
# Initialize a new project
iom-ops init --project-name my-project

# Run gate check
iom-ops check --gate G0

# Map pain points to hypotheses
iom-ops map-painpoints --input pains.md --output hypotheses.md

# Check MECE compliance
iom-ops check-mece --tree issue_tree.md

# Select methods based on bottlenecks
iom-ops select-methods --bottleneck-tags OTD_delay --output plan.md

# Render visualization pages
iom-ops render --page-register pages.md --output outputs/pages

# Build review pack
iom-ops build-pack --project-dir . --output outputs/review

# Show project status
iom-ops status
```

## Commands

- `init` - Initialize a new IOM diagnosis project
- `check` - Execute stage gate checks (G0-G5)
- `map-painpoints` - Map pain points to hypotheses
- `check-mece` - Verify MECE compliance of issue trees
- `select-methods` - Auto-recommend method stack based on bottlenecks
- `render` - Generate visualization pages
- `build-pack` - Assemble complete review package
- `status` - Display current project status

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/

# Lint
flake8 src/
```

## License

MIT
