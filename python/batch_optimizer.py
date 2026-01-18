"""
Batch Product Optimizer - Option 1: High-Memory Fast Evaluation

Loads all product candidates and runs optimizer once with the full set.
The solver automatically selects the optimal subset that maximizes profit.

"""
import csv
import time
import os
import argparse
import sys
from typing import List, Dict

# Import from spcplan.py (same directory)
from spcplan import (
    Product, DemandForecast, SeasonalFactors, ShippingOption,
    OptimizerConfig, PurchaseOrderOptimizer
)

from config_models import AppConfig
from consoleUI import ConsoleUI


# ========== CANDIDATE LOADING ==========

def load_candidates(filepath: str, app_config: AppConfig) -> List[Dict]:
    """Load product candidates from CSV file"""
    ConsoleUI.status(f"Loading candidates from: {filepath}")
    start = time.time()
    
    import csv
    data = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            row['wholesale_price'] = float(row['wholesale_price'])
            row['retail_price'] = float(row['retail_price'])
            row['weight_g'] = float(row['weight_g'])
            row['size_cm3'] = float(row['size_cm3'])
            row['shipping_cost_multiplier'] = float(row['shipping_cost_multiplier'])
            row['base_demand'] = float(row['base_demand'])
            data.append(row)
    
    elapsed = time.time() - start
    ConsoleUI.metric("Loaded", len(data), f"candidates in {elapsed:.2f}s")
    
    return data


def candidate_to_product(candidate: Dict, product_id: int, seasonal_factors: SeasonalFactors) -> Product:
    """Convert ProductCandidate dict to Product object"""
    
    # Create demand forecast
    demand_forecast = DemandForecast(
        base_demand=candidate['base_demand'],
        seasonal_factors=seasonal_factors,
        trend_factor=1.02,
        demand_buffer=1.5
    )
    
    # Build product
    product = Product(
        id=f"P{product_id:06d}",
        name=f"Product_{product_id}",
        wholesale_price=candidate['wholesale_price'],
        retail_price=candidate['retail_price'],
        size_cm3=candidate['size_cm3'],
        weight_g=candidate['weight_g'],
        category="General",  # Can be inferred post-optimization
        demand_forecast=demand_forecast,
        bulk_discount_threshold=0,
        bulk_discount_rate=0.0
    )
    
    return product


# ========== BATCH OPTIMIZATION ==========

def optimize_batch(
    candidates: List[Dict],
    config: OptimizerConfig,
    seasonal_factors: SeasonalFactors,
    verbose: bool = True
) -> Dict:
    """
    Run optimizer on full candidate set
    
    Returns:
        Optimization results with purchase orders and profit breakdown
    """
    
    ConsoleUI.status(f"Converting {len(candidates):,} candidates to Product objects...")
    start = time.time()
    
    products = [
        candidate_to_product(c, idx, seasonal_factors) 
        for idx, c in enumerate(candidates, start=1)
    ]
    
    elapsed = time.time() - start
    ConsoleUI.detail(f"Conversion complete in {elapsed:.2f}s")
    ConsoleUI.detail(f"Memory estimate: ~{len(products) * 0.002:.1f}MB for product objects")
    
    ConsoleUI.status("Initializing optimizer...")
    optimizer = PurchaseOrderOptimizer(config)
    
    ConsoleUI.status("Running optimization (this may take 5-30 minutes for large sets)...")
    opt_start = time.time()
    
    results = optimizer.optimize(products)
    
    opt_elapsed = time.time() - opt_start
    ConsoleUI.metric("Optimization complete", opt_elapsed/60, "min")
    
    # Add timing metadata
    results['batch_metadata'] = {
        'total_candidates': len(candidates),
        'conversion_time_seconds': elapsed,
        'optimization_time_seconds': opt_elapsed,
        'total_time_seconds': elapsed + opt_elapsed
    }
    
    return results


def export_catalog_to_csv(results: Dict, filepath: str, candidates_map: Dict[str, Dict], top_n: int = None, app_config: AppConfig = None) -> List[Dict]:
    """
    Export selected products to CSV with full parameters
    
    Returns:
        List of selected products for further use
    """
    
    if results['status'] not in ['OPTIMAL', 'FEASIBLE']:
        return []
    
    product_totals = results.get('product_totals', {})
    sorted_products = sorted(
        product_totals.items(),
        key=lambda x: x[1]['total_margin'],
        reverse=True
    )
    
    if top_n:
        sorted_products = sorted_products[:top_n]
    
    selected = []
    # Write CSV with all product parameters
    with open(filepath, 'w', newline='') as f:
        fieldnames = [
            'product_id', 'name', 'wholesale_price', 'retail_price',
            'weight_g', 'size_cm3', 'shipping_cost_multiplier', 'base_demand',
            'total_quantity_ordered', 'total_cost', 'total_revenue', 'total_margin'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for product_id, data in sorted_products:
            candidate = candidates_map.get(product_id, {})
            row = {
                'product_id': product_id,
                'name': data['name'],
                'wholesale_price': candidate.get('wholesale_price', 'N/A'),
                'retail_price': candidate.get('retail_price', 'N/A'),
                'weight_g': candidate.get('weight_g', 'N/A'),
                'size_cm3': candidate.get('size_cm3', 'N/A'),
                'shipping_cost_multiplier': candidate.get('shipping_cost_multiplier', 'N/A'),
                'base_demand': candidate.get('base_demand', 'N/A'),
                'total_quantity_ordered': data['total_quantity'],
                'total_cost': round(data['total_cost'], 2),
                'total_revenue': round(data['total_revenue'], 2),
                'total_margin': round(data['total_margin'], 2)
            }
            writer.writerow(row)
            selected.append(row)
    
    return selected


# ========== RESULT FILTERING ==========

def extract_selected_products(results: Dict, top_n: int = None) -> List[Dict]:
    """
    Extract products that were actually selected by the optimizer
    
    Args:
        results: Optimization results dict
        top_n: Optional limit on number of products to export
    
    Returns:
        List of selected products with their order quantities
    """
    
    if results['status'] not in ['OPTIMAL', 'FEASIBLE']:
        ConsoleUI.warning(f"Optimization status is {results['status']}")
        return []
    
    # Aggregate quantities across all months for each product
    product_totals = results.get('product_totals', {})
    
    # Sort by total margin (descending)
    sorted_products = sorted(
        product_totals.items(),
        key=lambda x: x[1]['total_margin'],
        reverse=True
    )
    
    # Apply top_n limit if specified
    if top_n:
        sorted_products = sorted_products[:top_n]
    
    # Convert to list of dicts
    selected = []
    for product_id, data in sorted_products:
        selected.append({
            'id': product_id,
            'name': data['name'],
            'total_quantity_ordered': data['total_quantity'],
            'total_cost': data['total_cost'],
            'total_revenue': data['total_revenue'],
            'total_margin': data['total_margin']
        })
    
    return selected


# ========== MAIN ==========

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Batch product optimization (Option 1: High-memory fast evaluation)'
    )
    parser.add_argument(
        'candidates_file',
        help='Path to product candidates CSV file'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output CSV file for selected products (default: from config.cfg)'
    )
    parser.add_argument(
        '--results-output',
        default=None,
        help='Output file for full optimization results (default: from config.cfg)'
    )
    parser.add_argument(
        '--top-n',
        type=int,
        default=None,
        help='Limit output to top N most profitable products'
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
        help='Number of months to plan (default: from config.cfg)'
    )
    parser.add_argument(
        '--demand-multiplier',
        type=float,
        default=1.0,
        help='Demand multiplier for forecasting (default: 1.0)'
    )
    
    args = parser.parse_args()
    
    # Load application config
    app_config = AppConfig.from_cfg_file('config.cfg')
    
    # Validate candidate file exists
    if not os.path.exists(args.candidates_file):
        ConsoleUI.error(f"Candidates file not found: {args.candidates_file}")
        sys.exit(1)
    
    ConsoleUI.header("BATCH PRODUCT OPTIMIZER (Option 1)")
    
    # Load candidates
    candidates = load_candidates(args.candidates_file, app_config)
    
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
    
    # Build mapping of product_id -> candidate for later export
    candidates_map = {}
    for idx, c in enumerate(candidates, start=1):
        candidates_map[f"P{idx:06d}"] = c
    
    # Show configuration
    ConsoleUI.section("CONFIGURATION")
    ConsoleUI.detail(f"Planning months: {config.planning_months}")
    ConsoleUI.detail(f"Budget per month: ${config.budget_per_month:,.2f}")
    ConsoleUI.detail(f"Warehouse capacity: {config.warehouse_capacity_m3}m³")
    ConsoleUI.detail(f"Solver time limit: {config.solver_time_limit_seconds}s")
    
    # Determine output path
    catalog_output = args.output or os.path.join(
        app_config.paths.data_output_dir,
        app_config.paths.product_catalog_file
    )
    
    try:
        # Convert candidates to products and run optimization
        products = convert_candidates_to_products(candidates, seasonal_factors, app_config)
        results = optimize_batch(products, seasonal_factors, config, app_config)
        
        # Show results
        ConsoleUI.section("OPTIMIZATION RESULTS")
        ConsoleUI.detail(f"Status: {results['status']}")
        ConsoleUI.metric("Objective Value", results['objective_value'], "$")
        ConsoleUI.metric("Products Selected", len(results.get('product_totals', {})))
        
        # Export catalog
        catalog_dir = os.path.dirname(os.path.abspath(catalog_output)) or '.'
        os.makedirs(catalog_dir, exist_ok=True)
        
        catalog_csv = os.path.abspath(catalog_output)
        selected = export_catalog_to_csv(results, catalog_csv, candidates_map, args.top_n, app_config)
        
        ConsoleUI.success(f"Exported {len(selected)} products to: {catalog_csv}")
        
        if selected:
            ConsoleUI.section("TOP PRODUCTS BY MARGIN")
            for i, p in enumerate(selected[:5], 1):
                ConsoleUI.detail(f"{i}. {p['id']}: ${p['total_margin']:,.2f} margin ({p['total_quantity_ordered']} units)")
        
    except MemoryError as e:
        ConsoleUI.error("Out of memory!")
        ConsoleUI.detail(f"{len(candidates):,} candidates exceeded available RAM")
        ConsoleUI.detail("Suggestions:")
        ConsoleUI.detail("  1. Use productcreator.py with --filter-mode=medium or --filter-mode=aggressive")
        ConsoleUI.detail("  2. Run filtered_optimizer.py instead (Option 2)")
        ConsoleUI.detail("  3. Increase system RAM or use chunked evaluation")
        sys.exit(1)
        
    except Exception as e:
        ConsoleUI.error(f"Optimization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
