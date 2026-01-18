# Repository Organization Guide

## Overview

The repository is organized into logical, self-contained folders for easy maintenance and clear separation of concerns.

```
online_shop/
├── README.md                       # Start here
├── VERSION.md                      # Version info
├── run.sh                          # Quick start script (see below)
│
├── config/                         # ⚙️  CONFIGURATION
│   └── config.json                 # Central config (all parameters here)
│
├── python/                         # 🐍 OPTIMIZATION ENGINE
│   ├── productcreator.py          # Generate product candidates
│   ├── batch_optimizer.py         # Option 1: Batch optimization
│   ├── filtered_optimizer.py      # Option 2: Filtered optimization
│   └── spcplan.py                 # Core solver (OR-Tools)
│
├── java/                          # ☕ SIMULATOR
│   ├── pom.xml                    # Maven build config
│   ├── src/main/java/se/lexicon/  # Java source
│   └── target/                    # Compiled output
│
├── data/                          # 📊 DATA & RESULTS
│   ├── output/                    # Generated outputs
│   │   ├── product_candidates.json
│   │   ├── filtered_candidates.json
│   │   ├── optimization_results.json
│   │   ├── final_catalog.json
│   │   ├── filtered_catalog.json
│   │   └── filtered_catalog.csv
│   └── input/                     # Input data (future use)
│
└── docs/                          # 📚 DOCUMENTATION
    ├── ARCHITECTURE_FIXES.md      # Design improvements
    ├── CONFIGURATION_GUIDE.md     # Parameter reference
    ├── EVALUATION_GUIDE.md        # Results interpretation
    ├── PRODUCT_OPTIMIZATION_GUIDE.md
    ├── VERIFICATION_REPORT.md     # Testing details
    └── solver.md                  # Mathematical model
```

---

## Quick Start with `run.sh`

```bash
# Generate candidates
./run.sh generate-aggressive      # ~10k candidates (fast)
./run.sh generate-medium          # ~100k candidates
./run.sh generate-full            # ~1.5M candidates (slow)

# Run optimization
./run.sh optimize-batch           # Fast batch optimizer
./run.sh optimize-filtered        # Safe filtered optimizer

# View results
./run.sh results                  # List generated files

# Java simulator
./run.sh java-build               # Compile
./run.sh java-run                 # Run simulation
```

---

## Folder Details

### `config/` - Configuration (Source of Truth)

**Purpose**: Single location for ALL tuneable parameters

**Contains**: `config.json` with:
- Demand model (tiers, max demand, elasticity)
- Markup multipliers
- Seasonal factors
- Shipping parameters
- Optimization constraints

**Access**: All Python scripts load from here automatically
```python
config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
```

**Why here**: 
- Centralized configuration
- No hardcoded values in code
- Easy to adjust parameters
- Version control friendly

---

### `python/` - Optimization Engine

**Purpose**: Product optimization using Google OR-Tools

**Key Files**:

1. **productcreator.py**
   - Generates product candidates via cartesian product
   - Applies realistic filtering (density, value constraints)
   - Outputs: JSON with wholesale/retail/demand

2. **batch_optimizer.py** (Option 1)
   - Fast: ~1000 variables, 0.5-5min optimization
   - Requires: 8GB+ RAM
   - Outputs: JSON + CSV catalogs

3. **filtered_optimizer.py** (Option 2)
   - Safe: Auto-filters candidates to ~2k-100k
   - Requires: <1GB RAM
   - Outputs: Same as batch_optimizer

4. **spcplan.py**
   - Core optimization engine
   - Uses Google OR-Tools SCIP solver
   - Imports: Product, Config, Optimizer classes

**Why here**: 
- Clean separation from Java
- All related Python scripts together
- Easy to run from any location

---

### `java/` - Discrete Event Simulator

**Purpose**: Simulate store operations with optimized inventory

**Structure**:
```
java/
├── pom.xml                    # Maven config
├── src/main/java/se/lexicon/
│   ├── Main.java             # Entry point
│   ├── SimulationController.java
│   ├── TimeSimulator.java
│   ├── Warehouse.java
│   ├── Store.java
│   ├── Product.java
│   ├── OrderGenerator.java
│   └── ... (14 total)
└── target/
    ├── classes/              # Compiled .class files
    └── test-classes/         # Test output
```

**Build**:
```bash
cd java
mvn clean package
```

**Run**:
```bash
java -cp target/classes se.lexicon.Main
```

**Why separate folder**: 
- Maven needs clean src structure
- Java builds to target/
- Self-contained project

---

### `data/` - Generated Outputs

**Purpose**: Store all generated files separate from source

**Structure**:
- `output/`: Where all results go
- `input/`: For future external data

**Contents**:
- `product_candidates.json` - Generated by productcreator
- `optimization_results.json` - Solver details
- `final_catalog.json` - Selected products
- `filtered_catalog.csv` - For spreadsheets
- `filtered_candidates.json` - Subset for filtering

**Why here**: 
- Keeps working directory clean
- Easy to backup/archive results
- `.gitignore` can exclude /data
- Results never mix with source

---

### `docs/` - Documentation

**Purpose**: Detailed guides and references

**Key Documents**:

1. **ARCHITECTURE_FIXES.md**
   - How we fixed path/config issues
   - Design principles
   - Before/after comparison

2. **CONFIGURATION_GUIDE.md**
   - Every parameter explained
   - Tuning scenarios
   - Common adjustments

3. **EVALUATION_GUIDE.md**
   - How to interpret results
   - Metrics explained
   - Performance analysis

4. **VERIFICATION_REPORT.md**
   - Testing results
   - Validation checklist
   - Known issues

5. **solver.md**
   - Mathematical model
   - Objective function
   - Constraints

**Why separate folder**: 
- Documentation easily accessible
- Easy to convert to PDF/website
- Not cluttering root directory

---

## Usage Patterns

### Pattern 1: Quick Optimization
```bash
cd python
python3 productcreator.py --filter-mode=aggressive
python3 batch_optimizer.py ../data/output/product_candidates.json
# Results in data/output/
```

### Pattern 2: Using Run Script
```bash
./run.sh generate-aggressive
./run.sh optimize-batch
./run.sh results
```

### Pattern 3: Manual Control
```bash
cd python
python3 productcreator.py --filter-mode=medium --output=../data/output/my_candidates.json
python3 batch_optimizer.py ../data/output/my_candidates.json --budget=10000
```

### Pattern 4: Java Integration
```bash
# Run optimization
./run.sh optimize-batch

# Feed results to simulator
cd java
mvn clean package
java -cp target/classes se.lexicon.Main
# (Simulator reads from ../data/output/)
```

---

## Configuration Workflow

1. **Edit config**: `config/config.json`
2. **Run scripts**: They auto-load config
3. **Check results**: `data/output/`
4. **Iterate**: No code changes needed!

Example config adjustments:
```json
// More conservative
"demand_multiplier": 0.8

// Holiday rush
"seasonal_factors": {"12": 2.0}

// Limited space
"warehouse_capacity_m3": 20.0
```

---

## File Paths Reference

| Purpose | Path |
|---------|------|
| Config | `config/config.json` |
| Python scripts | `python/*.py` |
| Java source | `java/src/main/java/se/lexicon/` |
| Build output | `java/target/` |
| Results | `data/output/*.json`, `*.csv` |
| Documentation | `docs/` |

---

## Migration Notes

**What moved where:**

| File | From | To | Why |
|------|------|-----|-----|
| config.json | src/main/ | config/ | Central config location |
| *.py | src/main/ | python/ | All optimization code together |
| pom.xml | root | java/ | Maven expects in java root |
| Java sources | src/main/java/ | java/src/main/java/ | Standard Maven layout |
| *.json, *.csv | src/main/ | data/output/ | Separate data from code |
| solver.md | src/main/ | docs/ | With other docs |

**Path updates:**
- `config/config.json` now loaded from `../config/` in Python scripts
- Output defaults changed to `../data/output/`
- No absolute paths remain

---

## Benefits of This Organization

✅ **Clear**: Each folder has one clear purpose  
✅ **Maintainable**: Easy to find and update code  
✅ **Scalable**: Easy to add new components  
✅ **Professional**: Follows standard conventions  
✅ **Portable**: Works on any machine  
✅ **Documented**: Each folder has a purpose  
✅ **Clean**: Source separate from data/output  
✅ **Safe**: No accidental file overwrites  

---

## Next Steps

1. Review README.md for overview
2. Read docs/CONFIGURATION_GUIDE.md
3. Try: `./run.sh generate-aggressive`
4. Try: `./run.sh optimize-batch`
5. View: `./run.sh results`
6. Explore: Individual Python scripts for advanced use
