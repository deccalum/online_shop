# Product Parameter Optimization - Usage Guide

## Overview

This system generates and optimizes product parameters using integer programming. Two approaches are available depending on your hardware capabilities.

---

## Quick Start

### Option 1: Batch Optimization (Fast, High-Memory)
**Best for:** Systems with 8GB+ RAM, need fastest results  
**Time:** ~5-30 minutes for 1.5M candidates  
**Memory:** ~2-10GB RAM

```bash
# Generate full candidate set (1.5M products)
python productcreator.py --filter-mode full

# Run batch optimization
python batch_optimizer.py product_candidates.json --top-n 100
```

### Option 2: Filtered Optimization (Safe, Low-Memory)
**Best for:** Any machine, guaranteed to work  
**Time:** ~2-5 minutes for 10k candidates  
**Memory:** <1GB RAM

```bash
# All-in-one: generate filtered candidates + optimize
python filtered_optimizer.py --filter-mode aggressive --top-n 50
```

---

## Detailed Usage

### 1. Product Candidate Generation (`productcreator.py`)

Generate all feasible product parameter combinations with configurable filtering.

**Command:**
```bash
python productcreator.py [options]
```

**Options:**
- `--filter-mode {full|medium|aggressive}` - Filtering preset (default: full)
  - `full`: ~1.5M candidates (price: $1-$10k, weight: 0.1-100kg, size: 100-50k cm³)
  - `medium`: ~100k candidates (price: $5-$5k, coarser steps)
  - `aggressive`: ~10k candidates (price: $10-$1k, coarsest steps)
- `--output FILENAME` - Output JSON file (default: product_candidates.json)

**Examples:**
```bash
# Generate full set for batch optimization
python productcreator.py --filter-mode full --output full_candidates.json

# Generate reduced set for quick testing
python productcreator.py --filter-mode aggressive --output test_candidates.json
```

**Output:** JSON file with ProductCandidate objects containing:
- `wholesale_price`: Cost to store
- `retail_price`: Price to customer (auto-calculated with tiered markup)
- `weight_g`: Weight in grams
- `size_cm3`: Volume in cubic centimeters
- `shipping_cost_multiplier`: Shipping cost factor (1.0, 2.5, or 5.0)
- `base_demand`: Estimated monthly demand

---

### 2a. Batch Optimizer (`batch_optimizer.py`) - Option 1

Runs optimizer ONCE with all candidates. The solver selects the optimal subset.

**Command:**
```bash
python batch_optimizer.py CANDIDATES_FILE [options]
```

**Arguments:**
- `CANDIDATES_FILE` - Path to product_candidates.json

**Options:**
- `--output FILENAME` - Catalog output file (default: final_catalog.json)
- `--results-output FILENAME` - Full results (default: optimization_results.json)
- `--top-n N` - Limit to top N products (default: all selected)
- `--budget AMOUNT` - Monthly budget (default: 12000)
- `--warehouse-capacity M3` - Warehouse capacity in m³ (default: 40)
- `--planning-months N` - Planning horizon (default: 3)

**Examples:**
```bash
# Basic usage with 1.5M candidates
python batch_optimizer.py product_candidates.json

# Custom budget and warehouse, export top 50 products
python batch_optimizer.py product_candidates.json \
    --budget 20000 \
    --warehouse-capacity 60 \
    --top-n 50 \
    --output top50_catalog.json

# Quick test with 6-month planning
python batch_optimizer.py product_candidates.json \
    --planning-months 6
```

**Memory Requirements:**
- 100k candidates: ~1-2GB RAM
- 500k candidates: ~4-6GB RAM
- 1.5M candidates: ~8-12GB RAM

**What happens if memory fails?**
- MemoryError is caught and user is prompted to use Option 2
- No automatic fallback (keeps memory management explicit)

---

### 2b. Filtered Optimizer (`filtered_optimizer.py`) - Option 2

All-in-one script: generates filtered candidates + optimizes. Safe for any machine.

**Command:**
```bash
python filtered_optimizer.py [options]
```

**Options:**
- `--filter-mode {medium|aggressive}` - Filter preset (default: aggressive)
- `--top-n N` - Top N products to export (default: 50)
- `--output FILENAME` - Catalog file (default: filtered_catalog.json)
- `--results-output FILENAME` - Full results (default: filtered_optimization_results.json)
- `--budget AMOUNT` - Monthly budget (default: 12000)
- `--warehouse-capacity M3` - Warehouse capacity (default: 40)
- `--planning-months N` - Planning horizon (default: 3)
- `--skip-generation` - Use existing filtered_candidates.json

**Examples:**
```bash
# Quickest run: aggressive filter + top 50 products
python filtered_optimizer.py

# Medium filter for more variety
python filtered_optimizer.py --filter-mode medium --top-n 100

# Reuse existing filtered candidates (skip generation step)
python filtered_optimizer.py --skip-generation --top-n 30

# Custom parameters
python filtered_optimizer.py \
    --filter-mode medium \
    --budget 25000 \
    --warehouse-capacity 80 \
    --planning-months 6 \
    --top-n 200
```

---

## Output Files

### Catalog JSON (`final_catalog.json` / `filtered_catalog.json`)
Contains selected products ranked by profitability:
```json
{
  "optimization_status": "OPTIMAL",
  "total_profit": 45000.0,
  "products_count": 50,
  "products": [
    {
      "id": "P000123",
      "name": "Product_123",
      "total_quantity_ordered": 150,
      "total_cost": 12000.0,
      "total_revenue": 18000.0,
      "total_margin": 6000.0
    },
    ...
  ]
}
```

### Full Results JSON (`optimization_results.json`)
Complete optimizer output with:
- `status`: OPTIMAL, FEASIBLE, or INFEASIBLE
- `objective_value`: Total net profit
- `purchase_orders`: Month-by-month order quantities per product
- `monthly_breakdown`: Revenue, costs, shipping, profit per month
- `product_totals`: Aggregate stats per product across all months

---

## Decision Guide: Which Option to Use?

| Scenario | Recommended Approach |
|----------|---------------------|
| First time / testing | **Option 2** (filtered_optimizer.py --filter-mode aggressive) |
| Limited RAM (<8GB) | **Option 2** (filtered_optimizer.py) |
| Maximum variety, best results | **Option 1** (batch_optimizer.py with full candidates) |
| Production deployment | **Option 1** if RAM available, else **Option 2 medium** |
| Quick iteration | **Option 2 aggressive** |
| Research / benchmarking | **Both** - compare results |

---

## Performance Benchmarks

### Option 1 - Batch Optimization
| Candidates | Time | RAM | Products Selected (typical) |
|------------|------|-----|----------------------------|
| 100k | ~2 min | 2GB | 80-120 |
| 500k | ~8 min | 6GB | 150-200 |
| 1.5M | ~25 min | 10GB | 200-300 |

### Option 2 - Filtered Optimization
| Filter Mode | Candidates | Time | RAM | Products Selected |
|-------------|-----------|------|-----|-------------------|
| Aggressive | ~10k | ~1 min | 0.5GB | 40-80 |
| Medium | ~100k | ~3 min | 1.5GB | 80-120 |

*Benchmarks on Apple M1, 16GB RAM*

---

## Troubleshooting

### "Out of memory" Error
**Solution:** Use filtered_optimizer.py with --filter-mode aggressive

### Solver takes too long (>30 min)
**Solutions:**
- Use --filter-mode medium or aggressive to reduce candidates
- Reduce --planning-months (e.g., from 6 to 3)
- Reduce --warehouse-capacity to limit solution space

### No products selected / INFEASIBLE status
**Causes:**
- Budget too low for any product
- Warehouse capacity too small
- Shipping constraints too tight

**Solutions:**
- Increase --budget
- Increase --warehouse-capacity
- Check shipping configuration in optimizer files

### Want more variety in results
**Solutions:**
- Use Option 1 with full candidates
- Use --filter-mode medium instead of aggressive
- Increase --top-n to export more products

---

## Integration with Java Simulator

### Export for Java Consumption
Both optimizers export JSON that can be loaded by Java:

```java
// Java pseudocode
ObjectMapper mapper = new ObjectMapper();
CatalogResults catalog = mapper.readValue(
    new File("final_catalog.json"),
    CatalogResults.class
);

for (ProductResult product : catalog.getProducts()) {
    store.addProduct(new Product(
        product.getId(),
        product.getName(),
        product.getTotalCost() / product.getTotalQuantityOrdered(),  // unit cost
        // ... other fields
    ));
}
```

### Monthly Purchase Orders
Use `optimization_results.json` → `purchase_orders` section for monthly restock logic.

---

## Advanced Configuration

### Custom Shipping Costs
Edit shipping configuration in optimizer files:

```python
shipping = ShippingOption(
    name="Custom Shipping",
    cost_per_kg=2.0,           # Adjust per-kg cost
    cost_per_m3=50.0,          # Adjust per-volume cost
    max_weight_kg=1000.0,      # Adjust weight limit
    max_volume_m3=20.0,        # Adjust volume limit
    crosses_border=False,      # Domestic vs international
    customs_duty_rate=0.0,     # Set to 0 for domestic
    days_transit=1
)
```

### Custom Seasonal Factors
Edit in optimizer files or add to config JSON:

```python
seasonal_factors = SeasonalFactors({
    1: 0.7,   # January: 70% of baseline
    2: 0.6,   # February: 60%
    # ... customize all 12 months
    12: 1.8   # December: 180% (holiday peak)
})
```

---

## Next Steps

1. **Test with aggressive filter:**
   ```bash
   python filtered_optimizer.py --top-n 20
   ```

2. **If satisfied, scale up to medium:**
   ```bash
   python filtered_optimizer.py --filter-mode medium --top-n 50
   ```

3. **For production, try batch if RAM allows:**
   ```bash
   python productcreator.py --filter-mode full
   python batch_optimizer.py product_candidates.json --top-n 100
   ```

4. **Integrate results into Java simulator** using exported JSON catalog
