# VS Code Debug Configurations

This guide explains how to use VS Code's debug configurations to run different optimization scenarios with the online_shop project.

## Overview

The `.vscode/launch.json` file in the Programming workspace contains pre-configured debug launchers for all Python scripts. These allow you to run optimization scenarios directly from VS Code with proper arguments and working directories.

## Key Benefits

- Run scripts with predefined arguments
- Integrated Terminal output
- Breakpoint debugging support
- Environment isolation with correct working directories
- One-click execution from Debug menu
## Setup

1. Make sure you're in the `/Users/gast/Programming/` workspace
2. Open the Debug panel (Ctrl+Shift+D or Cmd+Shift+D)
3. Select a configuration from the dropdown
4. Click the green play button or press F5

## Available Configurations

### 1. Product Creator Scenarios

These configurations generate product candidates with different filtering levels.

#### Product Creator: Aggressive Filter
- **Filter Mode**: Aggressive (~10k candidates)
- **Output**: `aggressive_candidates.csv`
- **Use Case**: Quick testing, fast iteration
- **Runtime**: ~30 seconds
- **Memory**: Low

```bash
# Equivalent command:
cd /Users/gast/Programming/online_shop/python
python productcreator.py --filter-mode aggressive --output ../data/output/aggressive_candidates.csv
```

#### Product Creator: Medium Filter
- **Filter Mode**: Medium (~100k candidates)
- **Output**: `medium_candidates.csv`
- **Use Case**: Balanced testing
- **Runtime**: ~5 minutes
- **Memory**: Medium

```bash
cd /Users/gast/Programming/online_shop/python
python productcreator.py --filter-mode medium --output ../data/output/medium_candidates.csv
```

#### Product Creator: Full Set
- **Filter Mode**: Full (~1.5M candidates)
- **Output**: `full_candidates.csv`
- **Use Case**: Production evaluation
- **Runtime**: ~30 minutes
- **Memory**: High

```bash
cd /Users/gast/Programming/online_shop/python
python productcreator.py --filter-mode full --output ../data/output/full_candidates.csv
```

### 2. Batch Optimizer Scenarios

High-memory fast evaluation for existing candidate sets.

#### Batch Optimizer: Full Set (1.5M candidates)
- **Input**: `product_candidates.csv`
- **Output**: `final_catalog.csv` + `optimization_results.json`
- **Memory Required**: 8GB+ RAM
- **Runtime**: 30-60 minutes
- **Best For**: Production optimization

```bash
cd /Users/gast/Programming/online_shop/python
python batch_optimizer.py ../data/output/product_candidates.csv \
  --output ../data/output/final_catalog.csv \
  --results-output ../data/output/optimization_results.json \
  --top-n 100 --budget 12000 --warehouse-capacity 40 --planning-months 3
```

**Parameters**:
- `--top-n 100`: Select top 100 most profitable products
- `--budget 12000`: Monthly budget ($12,000)
- `--warehouse-capacity 40`: Warehouse space (40 m³)
- `--planning-months 3`: Plan for 3 months ahead

#### Batch Optimizer: High Budget Scenario
- **Budget**: $25,000/month
- **Products**: Top 200
- **Warehouse**: 80 m³
- **Planning**: 6 months
- **Use Case**: Enterprise/High-volume retailers

```bash
cd /Users/gast/Programming/online_shop/python
python batch_optimizer.py ../data/output/product_candidates.csv \
  --output ../data/output/high_budget_catalog.csv \
  --top-n 200 --budget 25000 --warehouse-capacity 80 --planning-months 6
```

#### Batch Optimizer: Conservative (0.5x demand)
- **Demand Multiplier**: 0.5 (pessimistic forecast)
- **Products**: Top 50
- **Use Case**: Risk-averse planning

```bash
cd /Users/gast/Programming/online_shop/python
python batch_optimizer.py ../data/output/product_candidates.csv \
  --output ../data/output/conservative_batch.csv \
  --top-n 50 --demand-multiplier 0.5
```

### 3. Filtered Optimizer Scenarios

Low-memory safe evaluation (generates and optimizes in one pass).

#### Filtered Optimizer: Aggressive (Quick Test)
- **Filter Mode**: Aggressive (~10k candidates)
- **Products**: Top 20
- **Output**: `filtered_catalog.csv`
- **Runtime**: ~2-3 minutes
- **Use Case**: Development/testing
- **Memory**: Low

```bash
cd /Users/gast/Programming/online_shop/python
python filtered_optimizer.py --filter-mode aggressive --top-n 20 \
  --output ../data/output/filtered_catalog.csv
```

#### Filtered Optimizer: Medium (Balanced)
- **Filter Mode**: Medium (~100k candidates)
- **Products**: Top 50
- **Budget**: $15,000
- **Warehouse**: 50 m³
- **Runtime**: ~15-20 minutes
- **Use Case**: Balanced evaluation

```bash
cd /Users/gast/Programming/online_shop/python
python filtered_optimizer.py --filter-mode medium --top-n 50 \
  --budget 15000 --warehouse-capacity 50 --planning-months 3 \
  --output ../data/output/filtered_catalog.csv
```

#### Filtered Optimizer: Conservative Demand (0.5x)
- **Multiplier**: 0.5x base demand
- **Use Case**: Pessimistic forecasting
- **Output**: `conservative_catalog.csv`

```bash
cd /Users/gast/Programming/online_shop/python
python filtered_optimizer.py --filter-mode aggressive --top-n 20 \
  --demand-multiplier 0.5 --output ../data/output/conservative_catalog.csv
```

#### Filtered Optimizer: Aggressive Demand (1.5x)
- **Multiplier**: 1.5x base demand
- **Use Case**: Optimistic forecasting
- **Output**: `aggressive_catalog.csv`

```bash
cd /Users/gast/Programming/online_shop/python
python filtered_optimizer.py --filter-mode aggressive --top-n 20 \
  --demand-multiplier 1.5 --output ../data/output/aggressive_catalog.csv
```

## Working Directory Setup

All configurations set `cwd` to `${workspaceFolder}/online_shop/python` to ensure:

1. Relative imports work correctly
2. Config file can be loaded from `../config/config.json`
3. Output files go to `../data/output/`
4. Candidate files can be referenced as `../data/output/filename.csv`

## Output Formats

All scripts now output CSV by default (machine-readable, spreadsheet-compatible).

- **CSV Files**: Product catalogs and candidates (`.csv`)
- **JSON Files**: Full optimization results with detailed metrics (`.json`)

## Common Debugging Tips

### 1. Set Breakpoints
- Click on line numbers in editor
- Red circle appears - breakpoint is set
- Execution pauses when that line is reached

### 2. Inspect Variables
- Hover over variables in editor (when paused)
- Or use Debug Console to evaluate expressions
- Right-click → "Evaluate" in Debug view

### 3. Step Through Code
- **F10**: Step over (execute current line, move to next)
- **F11**: Step into (enter function calls)
- **Shift+F11**: Step out (exit current function)
- **F5**: Continue execution

### 4. Debug Console
- Switch to "Debug Console" tab
- Type Python expressions: `len(candidates)`, `results.keys()`, etc.
- View print() outputs from your scripts

## Troubleshooting

### Configuration Not Found
- Ensure VS Code is open from `/Users/gast/Programming/`
- Not from `online_shop/` or `online_shop/python/` subdirectory
- Workspace settings apply to the top-level folder only

### Wrong Working Directory Errors
- Check the `cwd` setting in launch.json
- Must be `${workspaceFolder}/online_shop/python`
- This ensures relative paths work correctly

### Import Errors
- Verify `.venv` Python environment is selected
- Check Python path in VS Code: Cmd+Shift+P → "Python: Select Interpreter"
- Choose the venv environment

### File Not Found Errors
- Debug configurations use relative paths like `../data/output/`
- These are relative to the `cwd` setting
- Verify files exist in that location before running

## Performance Comparison

| Scenario | Filter | Time | Memory | Products |
|----------|--------|------|--------|----------|
| Aggressive (PC) | 10k | 30s | Low | 10,000 |
| Medium (PC) | 100k | 5m | Med | 100,000 |
| Full (PC) | 1.5M | 30m | High | 1,500,000 |
| Batch (1.5M) | N/A | 30-60m | 8GB+ | Varies |
| Filtered (Agg) | 10k | 2-3m | Low | 20 |
| Filtered (Med) | 100k | 15-20m | Med | 50 |

## Quick Workflow

### For Development
1. Run "Product Creator: Aggressive Filter"
2. When done, run "Filtered Optimizer: Aggressive (Quick Test)"
3. Check results in `data/output/filtered_catalog.csv`

### For Testing Budget Scenarios
1. Run "Filtered Optimizer: Medium (Balanced)"
2. Modify `--budget` and `--warehouse-capacity` in launch.json
3. Run again and compare outputs

### For Production
1. Run "Product Creator: Full Set" (overnight)
2. Next day, run "Batch Optimizer: Full Set (1.5M candidates)"
3. Export final catalog from `data/output/final_catalog.csv`

## Editing Configurations

To modify a configuration (e.g., change budget):

1. Open `.vscode/launch.json`
2. Find the configuration by name
3. Edit the `args` array
4. Save the file
5. Select configuration again from Debug menu

Example - changing budget in "Batch Optimizer: Full Set":
```json
"args": [
    "../data/output/product_candidates.csv",
    "--output", "../data/output/final_catalog.csv",
    "--results-output", "../data/output/optimization_results.json",
    "--top-n", "100",
    "--budget", "20000",        // Changed from 12000
    "--warehouse-capacity", "40",
    "--planning-months", "3"
]
```

## Additional Resources

- [Configuration Guide](CONFIGURATION_GUIDE.md) - Parameter reference
- [Evaluation Guide](EVALUATION_GUIDE.md) - Interpret results
- [Repository Structure](REPOSITORY_STRUCTURE.md) - File organization
