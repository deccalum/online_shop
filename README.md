# Online Shop Simulation & Optimization System

A system for simulating and optimizing store operations, (as of now) tries to find the best product mix for a limited space (warehouse capacity) and budget, using a price-elastic demand model.

## Quick Start

### 1. Generate Product Candidates
```bash
cd python
python3 productcreator.py --filter-mode=aggressive
```
Options: `full` (~1.5M), `medium` (~100k), `aggressive` (~10k)

Output: `data/output/product_candidates.csv`

### 2. Run Optimization
```bash
cd python

# Option 1: Batch (fast, high memory)
python3 batch_optimizer.py ../data/output/product_candidates.csv

# Option 2: Filtered (safe, low memory)  
python3 filtered_optimizer.py --filter-mode=aggressive
```

### 3. View Results
Outputs go to `data/output/`:
- `final_catalog.csv`
- `filtered_catalog.csv`
- `optimization_results.csv`

## Configuration

All parameters are in `config/config.json`:

### Demand Model
```json
"demand_model": {
  "tiers": [
    {
      "tier_name": "ultra_cheap",
      "min_price": 0.0,
      "max_price": 5.0,
      "base_demand_monthly": 300,
      "max_demand_monthly": 1000,
      "demand_multiplier": 1.3
    },
    ...
  ]
}
```

### Key Parameters
- **Markup Tiers**: Price markup by cost range
- **Seasonal Factors**: Monthly demand variations
- **Shipping**: Costs, weight/volume limits, customs duty
- **Optimization**: Budget, warehouse capacity, planning horizon

See `docs/CONFIGURATION_GUIDE.md` for complete reference.

## System Components

### Python Optimization
- **productcreator.py**: Generates valid product combinations (cartesian product with filtering)
- **batch_optimizer.py**: Fast batch evaluation (1000+ variables, high memory)
- **filtered_optimizer.py**: Safe filtered evaluation (automatic subset selection)
- **spcplan.py**: Core optimizer using Google OR-Tools SCIP solver

## Workflow

1. **Generate candidates**: productcreator.py creates parameter combinations
2. **Optimize**: batch_optimizer.py or filtered_optimizer.py selects best products
3. **Export**: Results to CSV for analysis
4. **Simulate**: Feed results to Java simulator for discrete event simulation
5. **Analyze**: Review performance metrics

## Architecture Principles

**Configuration-Driven**: All business logic in JSON config
**Realistic Demand**: Price-elasticity with tier-specific caps 
**Per-Product**: Each price tier has independent demand model

## Documentation

- **[Architecture & Fixes](docs/ARCHITECTURE_FIXES.md)** - Design decisions & improvements
- **[Configuration Guide](docs/CONFIGURATION_GUIDE.md)** - All parameters explained
- **[Evaluation Guide](docs/EVALUATION_GUIDE.md)** - Understanding results
- **[Verification Report](docs/VERIFICATION_REPORT.md)** - Testing & validation
- **[Solver Docs](docs/solver.md)** - Mathematical model details

## File Organization Benefits

| Aspect | Benefit |
|--------|---------|
| **docs/** | All documentation in one place |
| **config/** | Single source of truth for all parameters |
| **python/** | Clean separation of optimization scripts |
| **java/** | Self-contained  |
| **data/output/** | All generated files in one place |
| **data/input/** | Room for future input data |


## Documentation Index

- Config tuning → See `docs/CONFIGURATION_GUIDE.md`
- Results interpretation → See `docs/EVALUATION_GUIDE.md`  
- Architecture details → See `docs/ARCHITECTURE_FIXES.md`
- Testing & validation → See `docs/VERIFICATION_REPORT.md`
- Solver math → See `docs/solver.md`
