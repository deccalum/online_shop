"""
Multi-Period Inventory Purchase Optimization using Integer Programming
Solver: Google OR-Tools SCIP (handles 1000+ SKUs efficiently)
"""
import numpy as np
import csv
import os
import sys
from configparser import ConfigParser
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
from ortools.linear_solver import pywraplp


# ========== CONFIGURATION CLASSES ==========

@dataclass
class SeasonalFactors:
    """Seasonal demand multipliers by month"""
    factors: Dict[int, float] = field(default_factory=lambda: {
        1: 0.8, 2: 0.7, 3: 0.9, 4: 0.95,
        5: 1.0, 6: 1.0, 7: 1.05, 8: 1.1,
        9: 1.15, 10: 1.3, 11: 1.5, 12: 1.6
    })

    def get(self, month: int) -> float:
        """Get seasonal factor for month (1-12)"""
        return self.factors.get(month, 1.0)

    @classmethod
    def from_dict(cls, data: Dict) -> 'SeasonalFactors':
        return cls(factors=data)


@dataclass
class DemandForecast:
    """Demand forecast parameters"""
    base_demand: float          # baseline monthly demand
    seasonal_factors: SeasonalFactors  # monthly multipliers
    trend_factor: float = 1.02  # e.g., 1.02 = 2% growth per month
    demand_buffer: float = 1.5  # e.g., 1.5 = never order > 150% of forecast

    def forecast_month(self, month: int) -> float:
        """Calculate forecasted demand for a given month"""
        seasonal = self.seasonal_factors.get(month)
        trend = self.trend_factor ** (month - 1)
        return self.base_demand * seasonal * trend


@dataclass
class Product:
    """Product with all cost/dimension attributes"""
    id: str
    name: str
    wholesale_price: float      # cost to store
    retail_price: float         # price to customer
    size_cm3: float             # volume in cubic cm
    weight_g: float             # weight in grams
    category: str
    demand_forecast: DemandForecast
    bulk_discount_threshold: int = 0   # units to trigger discount
    bulk_discount_rate: float = 0.0    # percentage discount

    @property
    def margin(self) -> float:
        """Unit profit before handling/shipping"""
        return self.retail_price - self.wholesale_price


@dataclass
class ShippingOption:
    """Shipping configuration"""
    name: str
    cost_per_kg: float
    cost_per_m3: float
    max_weight_kg: float
    max_volume_m3: float
    crosses_border: bool
    customs_duty_rate: float  # e.g., 0.10 for 10%
    days_transit: int


@dataclass
class OptimizerConfig:
    """Complete optimizer configuration"""
    planning_months: int
    budget_per_month: float
    warehouse_capacity_m3: float
    shipping: ShippingOption
    solver_time_limit_seconds: int = 300
    solver_type: str = 'SCIP'  # 'SCIP', 'CBC', 'GLOP'
    demand_multiplier: float = 1.0  # global demand adjustment
    seasonal_factors: Optional[Dict[int, float]] = None  # override defaults


# ========== OPTIMIZER ==========

class PurchaseOrderOptimizer:
    """Solves multi-period inventory optimization problems"""

    def __init__(self, config: OptimizerConfig):
        self.config = config
        self.solver = None
        self.variables = {}
        self.results = {}

    def optimize(self, products: List[Product]) -> Dict:
        """
        Solve the optimization problem
        
        Returns:
            Dict with keys:
            - 'status': 'OPTIMAL', 'FEASIBLE', or 'INFEASIBLE'
            - 'objective_value': total net profit
            - 'purchase_orders': {month: {product_id: quantity}}
            - 'monthly_breakdown': per-month cost/revenue/profit details
            - 'errors': list of constraint violations (if infeasible)
        """
        
        # Create solver
        self.solver = pywraplp.Solver.CreateSolver(self.config.solver_type)
        if not self.solver:
            return {'status': 'ERROR', 'message': f"Solver {self.config.solver_type} unavailable"}

        try:
            # Build variables
            self._create_variables(products)
            
            # Build objective
            self._create_objective(products)
            
            # Build constraints
            self._create_constraints(products)
            
            # Solve
            status = self.solver.Solve()
            
            # Extract results
            return self._extract_results(products, status)
            
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    def _create_variables(self, products: List[Product]):
        """Create decision variables q[p,t]"""
        self.variables = {}
        
        for product in products:
            self.variables[product.id] = {}
            
            for month in range(1, self.config.planning_months + 1):
                forecast = product.demand_forecast.forecast_month(month)
                forecast_adjusted = forecast * self.config.demand_multiplier
                max_qty = int(forecast_adjusted * product.demand_forecast.demand_buffer)
                
                var = self.solver.IntVar(
                    0, max_qty,
                    f'q_{product.id}_m{month}'
                )
                self.variables[product.id][month] = var

    def _create_objective(self, products: List[Product]):
        """Create objective function: maximize net profit"""
        objective_terms = []
        
        for month in range(1, self.config.planning_months + 1):
            # Gross margin from sales (retail - wholesale)
            for product in products:
                margin_term = product.margin * self.variables[product.id][month]
                objective_terms.append(margin_term)
            
            # Shipping costs (weight-based)
            total_weight_kg = sum(
                (p.weight_g / 1000.0) * self.variables[p.id][month]
                for p in products
            )
            weight_shipping = self.config.shipping.cost_per_kg * total_weight_kg
            objective_terms.append(-weight_shipping)
            
            # Shipping costs (volume-based)
            total_volume_m3 = sum(
                (p.size_cm3 / 1_000_000.0) * self.variables[p.id][month]
                for p in products
            )
            volume_shipping = self.config.shipping.cost_per_m3 * total_volume_m3
            objective_terms.append(-volume_shipping)
            
            # Customs duty (if applicable)
            if self.config.shipping.crosses_border:
                total_wholesale = sum(
                    p.wholesale_price * self.variables[p.id][month]
                    for p in products
                )
                customs = self.config.shipping.customs_duty_rate * total_wholesale
                objective_terms.append(-customs)
        
        self.solver.Maximize(sum(objective_terms))

    def _create_constraints(self, products: List[Product]):
        """Create all constraints"""
        
        # Budget constraint per month
        for month in range(1, self.config.planning_months + 1):
            budget_used = sum(
                p.wholesale_price * self.variables[p.id][month]
                for p in products
            )
            self.solver.Add(
                budget_used <= self.config.budget_per_month,
                f'budget_m{month}'
            )
        
        # Warehouse capacity constraint (total across all months)
        total_volume = sum(
            sum(
                (p.size_cm3 / 1_000_000.0) * self.variables[p.id][month]
                for month in range(1, self.config.planning_months + 1)
            )
            for p in products
        )
        self.solver.Add(
            total_volume <= self.config.warehouse_capacity_m3,
            'warehouse_capacity'
        )
        
        # Shipping weight limit per month
        for month in range(1, self.config.planning_months + 1):
            total_weight = sum(
                (p.weight_g / 1000.0) * self.variables[p.id][month]
                for p in products
            )
            self.solver.Add(
                total_weight <= self.config.shipping.max_weight_kg,
                f'shipping_weight_m{month}'
            )
        
        # Shipping volume limit per month
        for month in range(1, self.config.planning_months + 1):
            total_volume = sum(
                (p.size_cm3 / 1_000_000.0) * self.variables[p.id][month]
                for p in products
            )
            self.solver.Add(
                total_volume <= self.config.shipping.max_volume_m3,
                f'shipping_volume_m{month}'
            )

    def _extract_results(self, products: List[Product], solver_status: int) -> Dict:
        """Extract and format results"""
        
        if solver_status == pywraplp.Solver.OPTIMAL:
            status = 'OPTIMAL'
        elif solver_status == pywraplp.Solver.FEASIBLE:
            status = 'FEASIBLE'
        else:
            status = 'INFEASIBLE'
        
        results = {
            'status': status,
            'objective_value': self.solver.Objective().Value() if status in ['OPTIMAL', 'FEASIBLE'] else 0,
            'purchase_orders': {},
            'monthly_breakdown': {},
            'product_totals': {}
        }
        
        if status in ['OPTIMAL', 'FEASIBLE']:
            # Extract purchase orders
            for month in range(1, self.config.planning_months + 1):
                results['purchase_orders'][month] = {}
                month_cost = 0
                month_revenue = 0
                month_weight = 0
                month_volume = 0
                
                for product in products:
                    qty = int(self.variables[product.id][month].solution_value())
                    
                    if qty > 0:
                        cost = product.wholesale_price * qty
                        revenue = product.retail_price * qty
                        weight = (product.weight_g / 1000.0) * qty
                        volume = (product.size_cm3 / 1_000_000.0) * qty
                        
                        results['purchase_orders'][month][product.id] = {
                            'name': product.name,
                            'quantity': qty,
                            'unit_wholesale': product.wholesale_price,
                            'total_cost': cost,
                            'unit_retail': product.retail_price,
                            'total_revenue': revenue,
                            'margin': revenue - cost,
                            'weight_kg': weight,
                            'volume_m3': volume
                        }
                        
                        month_cost += cost
                        month_revenue += revenue
                        month_weight += weight
                        month_volume += volume
                
                # Calculate shipping for this month
                weight_shipping = self.config.shipping.cost_per_kg * month_weight
                volume_shipping = self.config.shipping.cost_per_m3 * month_volume
                customs = (self.config.shipping.customs_duty_rate * month_cost 
                          if self.config.shipping.crosses_border else 0)
                
                results['monthly_breakdown'][month] = {
                    'product_cost': month_cost,
                    'product_revenue': month_revenue,
                    'gross_margin': month_revenue - month_cost,
                    'weight_shipping': weight_shipping,
                    'volume_shipping': volume_shipping,
                    'customs_duty': customs,
                    'total_costs': month_cost + weight_shipping + volume_shipping + customs,
                    'net_profit': month_revenue - month_cost - weight_shipping - volume_shipping - customs,
                    'weight_kg': month_weight,
                    'volume_m3': month_volume,
                    'items_ordered': len(results['purchase_orders'][month])
                }
            
            # Product totals across all months
            for product in products:
                total_qty = 0
                total_cost = 0
                total_revenue = 0
                
                for month in range(1, self.config.planning_months + 1):
                    if product.id in results['purchase_orders'][month]:
                        order = results['purchase_orders'][month][product.id]
                        total_qty += order['quantity']
                        total_cost += order['total_cost']
                        total_revenue += order['total_revenue']
                
                if total_qty > 0:
                    results['product_totals'][product.id] = {
                        'name': product.name,
                        'total_quantity': total_qty,
                        'total_cost': total_cost,
                        'total_revenue': total_revenue,
                        'total_margin': total_revenue - total_cost
                    }
        
        return results


# ========== UTILITIES ==========

def load_config_from_cfg(filepath: str) -> OptimizerConfig:
    """Load optimizer configuration from .cfg file using ConfigParser"""
    config = ConfigParser()
    config.read(filepath)
    
    # Build ShippingOption
    shipping = ShippingOption(
        name=config.get('shipping', 'name', fallback='standard'),
        cost_per_kg=config.getfloat('shipping', 'cost_per_kg', fallback=2.0),
        cost_per_m3=config.getfloat('shipping', 'cost_per_m3', fallback=50.0),
        handling_fee=config.getfloat('shipping', 'handling_fee', fallback=5.0)
    )
    
    # Build OptimizerConfig
    return OptimizerConfig(
        planning_months=config.getint('optimization', 'planning_months', fallback=12),
        budget_per_month=config.getfloat('optimization', 'budget_per_month', fallback=12000.0),
        warehouse_capacity_m3=config.getfloat('optimization', 'warehouse_capacity_m3', fallback=40.0),
        shipping=shipping,
        solver_time_limit_seconds=config.getint('optimization', 'solver_time_limit_seconds', fallback=300),
        solver_type=config.get('optimization', 'solver_type', fallback='SCIP'),
        demand_multiplier=config.getfloat('optimization', 'demand_multiplier', fallback=1.0),
        seasonal_factors=None
    )


def products_from_csv(filepath: str) -> List[Product]:
    """Load products from CSV file"""
    
    products = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            seasonal = SeasonalFactors()  # Use defaults
            demand = DemandForecast(
                base_demand=float(row.get('base_demand', 100.0)),
                seasonal_factors=seasonal,
                trend_factor=1.02,
                demand_buffer=1.5
            )
            
            product = Product(
                id=f"P{idx:06d}",
                name=row.get('name', f'Product_{idx}'),
                wholesale_price=float(row.get('wholesale_price', 10.0)),
                retail_price=float(row.get('retail_price', 20.0)),
                size_cm3=float(row.get('size_cm3', 100.0)),
                weight_g=float(row.get('weight_g', 500.0)),
                category=row.get('category', 'general'),
                demand_forecast=demand,
                bulk_discount_threshold=0,
                bulk_discount_rate=0.0
            )
            products.append(product)
    
    return products


# ========== MAIN ==========

if __name__ == "__main__":
    print("spcplan.py - Import this module in other scripts to use the optimizer")
    print("\nUsage example:")
    print("  from spcplan import PurchaseOrderOptimizer, OptimizerConfig, Product")
    print("  optimizer = PurchaseOrderOptimizer(config)")
    print("  results = optimizer.optimize(products)")
