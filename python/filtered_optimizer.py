"""
Filtered Product Optimizer - Option 2: Low-Memory Safe Evaluation

Generates reduced candidate set using aggressive filtering, then optimizes.
This is the safe/fast alternative when batch_optimizer.py exceeds memory limits.

"""
import csv
import time
import os
import argparse
import subprocess
import sys
from typing import List, Dict

# Import from spcplan.py (same directory)
from spcplan import (
    Product, DemandForecast, SeasonalFactors, ShippingOption,
    OptimizerConfig, PurchaseOrderOptimizer
)

from config_models import AppConfig
from consoleUI import ConsoleUI


# ========== CANDIDATE GENERATION ==========

def generate_filtered_candidates(filter_mode: str, output_file: str, app_config: AppConfig) -> int:
    """
    Call productcreator.py to generate filtered candidates
    
    Returns:
        Number of candidates generated
    """
    ConsoleUI.status(f"Generating candidates with filter mode: {filter_mode}")
    
    cmd = [
        'python3',
        'productcreator.py',
        '--filter-mode', filter_mode,
        '--output', output_file
    ]
    
    # Run productcreator.py (same directory as this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result = subprocess.run(
        cmd,
        cwd=script_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        ConsoleUI.error("ERROR running productcreator.py:")
        ConsoleUI.error(result.stderr)
        sys.exit(1)
    
    # Parse output to get candidate count
    ConsoleUI.detail(result.stdout)
    
    # Load to verify and return count
    count = 0
    with open(output_file, 'r') as f:
        reader = csv.DictReader(f)
        for _ in reader:
            count += 1
    
    return count


# ========== OPTIMIZATION ==========

def load_and_optimize(
    candidates_file: str,
    config: OptimizerConfig,
    seasonal_factors: SeasonalFactors
) -> tuple:
    """
    Load candidates and run optimization
    
    Returns:
        Tuple of (optimization results, candidates_map)
    """
    # Load candidates
    ConsoleUI.status(f"Loading candidates from: {candidates_file}")
    candidates = []
    with open(candidates_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['wholesale_price'] = float(row['wholesale_price'])
            row['retail_price'] = float(row['retail_price'])
            row['weight_g'] = float(row['weight_g'])
            row['size_cm3'] = float(row['size_cm3'])
            row['shipping_cost_multiplier'] = float(row['shipping_cost_multiplier'])
            row['base_demand'] = float(row['base_demand'])
            candidates.append(row)
    
    ConsoleUI.metric("Loaded", len(candidates), "candidates")
    
    # Pre-filter to top 1000 candidates by profit potential (demand × margin)
    # This keeps solver tractable while maintaining quality
    candidates_scored = []
    for idx, c in enumerate(candidates, start=1):
        margin = c['retail_price'] - c['wholesale_price']
        profit_potential = margin * c['base_demand']
        candidates_scored.append((idx, c, profit_potential))
    
    candidates_scored.sort(key=lambda x: x[2], reverse=True)
    top_candidates = candidates_scored[:1000]
    
    ConsoleUI.detail("Selected top 1,000 candidates by profit potential")
    
    # Build candidate map
    candidates_map = {}
    for idx, (orig_idx, c, _) in enumerate(top_candidates, start=1):
        candidates_map[f"P{idx:06d}"] = c
    
    # Use filtered candidates list
    candidates = [c for _, c, _ in top_candidates]
    
    # Convert to Product objects
    ConsoleUI.status(f"Converting {len(candidates):,} candidates to Product objects...")
    products = []
    
    for idx, candidate in enumerate(candidates, start=1):
        if idx % 5000 == 0:
            ConsoleUI.progress(idx, len(candidates), "Converted")
        
        demand_forecast = DemandForecast(
            base_demand=candidate['base_demand'],
            seasonal_factors=seasonal_factors,
            trend_factor=1.02,
            demand_buffer=1.5
        )
        
        product = Product(
            id=f"P{idx:06d}",
            name=f"Product_{idx}",
            wholesale_price=candidate['wholesale_price'],
            retail_price=candidate['retail_price'],
            size_cm3=candidate['size_cm3'],
            weight_g=candidate['weight_g'],
            category="General",
            demand_forecast=demand_forecast,
            bulk_discount_threshold=0,
            bulk_discount_rate=0.0
        )
        
        products.append(product)
    
    ConsoleUI.success(f"Converted {len(products):,} products")
    
    # Run optimizer (demand is now per-product in config)
    ConsoleUI.status(f"Initializing optimizer with {len(products)} products...")
    ConsoleUI.detail(f"Time limit: {config.solver_time_limit_seconds}s")
    ConsoleUI.detail(f"Budget/month: ${config.budget_per_month:,.2f}")
    ConsoleUI.detail(f"Planning months: {config.planning_months}")
    optimizer = PurchaseOrderOptimizer(config)
    
    ConsoleUI.status(f"Starting optimization (this may take up to {config.solver_time_limit_seconds}s)...")
    start = time.time()
    
    try:
        results = optimizer.optimize(products)
    except KeyboardInterrupt:
        ConsoleUI.warning("Optimization interrupted by user")
        sys.exit(1)
    except Exception as e:
        ConsoleUI.error(f"Optimization error: {e}")
        raise
    
    elapsed = time.time() - start
    ConsoleUI.success(f"Optimization complete in {elapsed:.2f}s")
    
    # Add metadata
    results['filtered_metadata'] = {
        'total_candidates': len(candidates),
        'optimization_time_seconds': elapsed
    }
    
    return results, candidates_map


# ========== RESULT EXPORT ==========

def export_catalog(results: Dict, output_file: str, candidates_map: Dict[str, Dict], top_n: int = None):
    """Export selected products to CSV only"""
    
    if results['status'] not in ['OPTIMAL', 'FEASIBLE']:
        ConsoleUI.warning(f"Optimization status is {results['status']}")
        return
    
    # Get product totals
    product_totals = results.get('product_totals', {})
    
    # Sort by margin
    sorted_products = sorted(
        product_totals.items(),
        key=lambda x: x[1]['total_margin'],
        reverse=True
    )
    
    # Apply limit
    if top_n:
        sorted_products = sorted_products[:top_n]
    
    # Build catalog
    selected = []
    for product_id, data in sorted_products:
        candidate = candidates_map.get(product_id, {})
        selected.append({
            'id': product_id,
            'name': data['name'],
            'wholesale_price': candidate.get('wholesale_price'),
            'retail_price': candidate.get('retail_price'),
            'weight_g': candidate.get('weight_g'),
            'size_cm3': candidate.get('size_cm3'),
            'shipping_cost_multiplier': candidate.get('shipping_cost_multiplier'),
            'base_demand': candidate.get('base_demand'),
            'total_quantity_ordered': data['total_quantity'],
            'total_cost': data['total_cost'],
            'total_revenue': data['total_revenue'],
            'total_margin': data['total_margin']
        })
    
    # Create output directory if needed
    output_dir = os.path.dirname(os.path.abspath(output_file)) or '.'
    os.makedirs(output_dir, exist_ok=True)
    
    catalog_csv = os.path.abspath(output_file)
    
    # Export CSV only
    with open(catalog_csv, 'w', newline='') as f:
        fieldnames = [
            'product_id', 'name', 'wholesale_price', 'retail_price',
            'weight_g', 'size_cm3', 'shipping_cost_multiplier', 'base_demand',
            'total_quantity_ordered', 'total_cost', 'total_revenue', 'total_margin'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for p in selected:
            writer.writerow({
                'product_id': p['id'],
                'name': p['name'],
                'wholesale_price': p['wholesale_price'],
                'retail_price': p['retail_price'],
                'weight_g': p['weight_g'],
                'size_cm3': p['size_cm3'],
                'shipping_cost_multiplier': p['shipping_cost_multiplier'],
                'base_demand': p['base_demand'],
                'total_quantity_ordered': p['total_quantity_ordered'],
                'total_cost': round(p['total_cost'], 2),
                'total_revenue': round(p['total_revenue'], 2),
                'total_margin': round(p['total_margin'], 2)
            })
    
    ConsoleUI.success(f"Exported catalog to: {catalog_csv}")
    ConsoleUI.detail(f"Total products in catalog: {len(selected)}")
    
    if selected:
        ConsoleUI.section("TOP PRODUCTS BY MARGIN")
        for i, p in enumerate(selected[:5], 1):
            ConsoleUI.detail(f"{i}. {p['id']}: ${p['total_margin']:,.2f} margin ({p['total_quantity_ordered']} units)")


# ========== MAIN ==========


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Filtered product optimization (Option 2: Low-memory safe evaluation)'
    )
    parser.add_argument(
        '--filter-mode',
        choices=['medium', 'aggressive'],
        default='aggressive',
        help='Filter preset: medium (~100k) or aggressive (~10k) - default: aggressive'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=50,
        help='Number of top products to export (default: 50)'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output CSV catalog file (default: from config.cfg)'
    )
    parser.add_argument(
        '--results-output',
        default=None,
        help='Full results file (default: from config.cfg)'
    )
    parser.add_argument(
        '--budget',
        type=float,
        default=None,
        help='Monthly budget (default: from config.cfg)'
    )
    parser.add_argument(
        '--warehouse-capacity',
        type=float,
        default=None,
        help='Warehouse capacity in m³ (default: from config.cfg)'
    )
    parser.add_argument(
        '--planning-months',
        type=int,
        default=None,
        help='Planning months (default: from config.cfg)'
    )
    parser.add_argument(
        '--demand-multiplier',
        type=float,
        default=1.0,
        help='Demand multiplier (default: 1.0)'
    )
    parser.add_argument(
        '--skip-generation',
        action='store_true',
        help='Skip candidate generation, use existing filtered_candidates.csv'
    )
    
    args = parser.parse_args()
    
    # Load application config
    app_config = AppConfig.from_cfg_file('config.cfg')
    
    ConsoleUI.header("FILTERED PRODUCT OPTIMIZER (Option 2)")
    
    # Determine output paths
    candidates_file = os.path.join(
        app_config.paths.data_output_dir,
        app_config.paths.filtered_candidates_file
    )
    catalog_output = args.output or os.path.join(
        app_config.paths.data_output_dir,
        app_config.paths.filtered_catalog_file
    )
    results_output = args.results_output or os.path.join(
        app_config.paths.data_output_dir,
        app_config.paths.filtered_optimization_results_file
    )
    
    # Generate or load candidates
    if not args.skip_generation:
        try:
            candidate_count = generate_filtered_candidates(args.filter_mode, candidates_file, app_config)
            ConsoleUI.metric("Generated", candidate_count, "filtered candidates")
        except Exception as e:
            ConsoleUI.error(f"Failed to generate candidates: {e}")
            sys.exit(1)
    else:
        if os.path.exists(candidates_file):
            ConsoleUI.detail(f"Using existing candidates from: {candidates_file}")
        else:
            ConsoleUI.error(f"{candidates_file} not found!")
            ConsoleUI.detail("Run without --skip-generation to generate candidates first.")
            sys.exit(1)
    
    # Load shipping configuration
    shipping = ShippingOption(
        name=app_config.shipping.name,
        cost_per_kg=app_config.shipping.cost_per_kg,
        cost_per_m3=app_config.shipping.cost_per_m3,
        max_weight_kg=app_config.shipping.max_weight_kg,
        max_volume_m3=app_config.shipping.max_volume_m3,
        crosses_border=app_config.shipping.crosses_border,
        customs_duty_rate=app_config.shipping.customs_duty_rate,
        days_transit=app_config.shipping.days_transit
    )
    
    # Build optimizer config (override with CLI args if provided)
    config = OptimizerConfig(
        planning_months=args.planning_months or app_config.optimization.planning_months,
        budget_per_month=args.budget or app_config.optimization.budget_per_month,
        warehouse_capacity_m3=args.warehouse_capacity or app_config.optimization.warehouse_capacity_m3,
        shipping=shipping,
        solver_time_limit_seconds=app_config.optimization.solver_time_limit_seconds,
        solver_type=app_config.optimization.solver_type,
        demand_multiplier=args.demand_multiplier
    )
    
    seasonal_factors = SeasonalFactors()
    
    # Show configuration
    ConsoleUI.section("CONFIGURATION")
    ConsoleUI.detail(f"Filter mode: {args.filter_mode}")
    ConsoleUI.detail(f"Planning months: {config.planning_months}")
    ConsoleUI.detail(f"Budget per month: ${config.budget_per_month:,.2f}")
    ConsoleUI.detail(f"Warehouse capacity: {config.warehouse_capacity_m3}m³")
    ConsoleUI.detail(f"Top N products: {args.top_n}")
    
    try:
        # Run optimization
        results = load_and_optimize(candidates_file, config, seasonal_factors, app_config)
        
        # Show results
        ConsoleUI.section("OPTIMIZATION RESULTS")
        ConsoleUI.detail(f"Status: {results['status']}")
        ConsoleUI.metric("Objective Value", results['objective_value'], "$")
        ConsoleUI.metric("Products Selected", len(results.get('product_totals', {})))
        
        # Export catalog
        catalog_dir = os.path.dirname(os.path.abspath(catalog_output)) or '.'
        os.makedirs(catalog_dir, exist_ok=True)
        
        selected = export_catalog(results, catalog_output, candidates_file, args.top_n, app_config)
        
        ConsoleUI.success(f"Exported {len(selected)} products to: {catalog_output}")
        
        if selected:
            ConsoleUI.section("TOP PRODUCTS BY MARGIN")
            for i, p in enumerate(selected[:5], 1):
                ConsoleUI.detail(f"{i}. {p['id']}: ${p['total_margin']:,.2f} margin ({p['total_quantity_ordered']} units)")
        ConsoleUI.section("OPTIMIZATION COMPLETE")
        
    except Exception as e:
        ConsoleUI.error(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
