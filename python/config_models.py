"""Configuration dataclasses - holds all parameters for optimization and generation"""
from dataclasses import dataclass, field
from typing import Dict
from configparser import ConfigParser
import os


@dataclass
class MarkupTier:
    """Price markup configuration by wholesale cost range"""
    min_cost: float
    max_cost: float
    markup_multiplier: float


@dataclass
class DemandTier:
    """Demand configuration by price range"""
    min_price: float
    max_price: float
    base_demand_monthly: float
    demand_multiplier: float = 1.0
    max_demand_monthly: float = 500


@dataclass
class FilterPreset:
    """Product generation filter parameters"""
    name: str
    description: str
    max_price: float
    max_weight: float
    max_size: float
    price_steps: str
    weight_steps: str
    size_steps: str
    density_min: float
    density_max: float


@dataclass
class ShippingConfig:
    """Shipping parameters"""
    cost_per_kg: float
    cost_per_m3: float
    max_weight_kg: float
    max_volume_m3: float
    crosses_border: bool
    customs_duty_rate: float
    days_transit: int


@dataclass
class OptimizationConfig:
    """Optimization solver parameters"""
    budget_per_month: float
    warehouse_capacity_m3: float
    planning_months: int
    solver_time_limit_seconds: int
    solver_type: str
    demand_multiplier: float


@dataclass
class PathsConfig:
    """File paths configuration"""
    data_output_dir: str
    product_candidates_file: str
    filtered_candidates_file: str
    final_catalog_file: str
    filtered_catalog_file: str
    optimization_results_file: str
    filtered_optimization_results_file: str


@dataclass
class AppConfig:
    """Complete application configuration"""
    markup_tiers: list = field(default_factory=list)
    demand_tiers: list = field(default_factory=list)
    filter_presets: Dict[str, FilterPreset] = field(default_factory=dict)
    shipping: ShippingConfig = None
    optimization: OptimizationConfig = None
    paths: PathsConfig = None

    @classmethod
    def from_cfg_file(cls, cfg_path: str) -> 'AppConfig':
        """Load configuration from config.cfg file"""
        config = ConfigParser()
        config.read(cfg_path)

        # Build markup tiers
        markup_tiers = [
            MarkupTier(0, 50, 1 + config.getfloat('markup_tiers', 'tier_6_markup', fallback=2.0)),
            MarkupTier(50, 100, 1 + config.getfloat('markup_tiers', 'tier_5_markup', fallback=1.5)),
            MarkupTier(100, 500, 1 + config.getfloat('markup_tiers', 'tier_4_markup', fallback=1.25)),
            MarkupTier(500, 1000, 1 + config.getfloat('markup_tiers', 'tier_3_markup', fallback=1.0)),
            MarkupTier(1000, 3000, 1 + config.getfloat('markup_tiers', 'tier_2_markup', fallback=0.75)),
            MarkupTier(3000, 999999, 1 + config.getfloat('markup_tiers', 'tier_1_markup', fallback=0.5)),
        ]

        # Build demand tiers
        demand_tiers = [
            DemandTier(0, config.getfloat('demand_model', 'tier_7_threshold', fallback=50),
                      config.getfloat('demand_model', 'tier_7_demand', fallback=320), 1.0, 500),
            DemandTier(config.getfloat('demand_model', 'tier_7_threshold', fallback=50),
                      config.getfloat('demand_model', 'tier_6_threshold', fallback=100),
                      config.getfloat('demand_model', 'tier_6_demand', fallback=280), 1.0, 400),
            DemandTier(config.getfloat('demand_model', 'tier_6_threshold', fallback=100),
                      config.getfloat('demand_model', 'tier_5_threshold', fallback=500),
                      config.getfloat('demand_model', 'tier_5_demand', fallback=240), 1.0, 300),
            DemandTier(config.getfloat('demand_model', 'tier_5_threshold', fallback=500),
                      config.getfloat('demand_model', 'tier_4_threshold', fallback=1000),
                      config.getfloat('demand_model', 'tier_4_demand', fallback=200), 1.0, 200),
            DemandTier(config.getfloat('demand_model', 'tier_4_threshold', fallback=1000),
                      config.getfloat('demand_model', 'tier_3_threshold', fallback=3000),
                      config.getfloat('demand_model', 'tier_3_demand', fallback=160), 1.0, 100),
            DemandTier(config.getfloat('demand_model', 'tier_3_threshold', fallback=3000),
                      config.getfloat('demand_model', 'tier_2_threshold', fallback=5000),
                      config.getfloat('demand_model', 'tier_2_demand', fallback=120), 1.0, 50),
            DemandTier(config.getfloat('demand_model', 'tier_2_threshold', fallback=5000),
                      999999,
                      config.getfloat('demand_model', 'tier_1_demand', fallback=80), 1.0, 20),
        ]

        # Build filter presets
        filter_presets = {
            'full': FilterPreset('full', 'Full parameter space (~1.5M candidates)',
                                10_000, 100, 50_000, 'fine', 'fine', 'fine', 0.01, 10.0),
            'medium': FilterPreset('medium', 'Reduced parameter space (~100k candidates)',
                                  5_000, 50, 30_000, 'medium', 'medium', 'medium', 0.05, 8.0),
            'aggressive': FilterPreset('aggressive', 'Minimal parameter space (~10k candidates)',
                                      1_000, 20, 20_000, 'coarse', 'coarse', 'coarse', 0.1, 5.0),
        }

        # Build shipping config
        shipping = ShippingConfig(
            cost_per_kg=config.getfloat('shipping', 'cost_per_kg', fallback=3.5),
            cost_per_m3=config.getfloat('shipping', 'cost_per_m3', fallback=80.0),
            max_weight_kg=config.getfloat('shipping', 'max_weight_kg', fallback=800.0),
            max_volume_m3=config.getfloat('shipping', 'max_volume_m3', fallback=15.0),
            crosses_border=config.getboolean('shipping', 'crosses_border', fallback=True),
            customs_duty_rate=config.getfloat('shipping', 'customs_duty_rate', fallback=0.12),
            days_transit=config.getint('shipping', 'days_transit', fallback=3)
        )

        # Build optimization config
        optimization = OptimizationConfig(
            budget_per_month=config.getfloat('optimization', 'budget_per_month', fallback=12000.0),
            warehouse_capacity_m3=config.getfloat('optimization', 'warehouse_capacity_m3', fallback=40.0),
            planning_months=config.getint('optimization', 'planning_months', fallback=1),
            solver_time_limit_seconds=config.getint('optimization', 'solver_time_limit_seconds', fallback=60),
            solver_type=config.get('optimization', 'solver_type', fallback='SCIP'),
            demand_multiplier=config.getfloat('optimization', 'demand_multiplier', fallback=1.0)
        )

        # Build paths config
        paths = PathsConfig(
            data_output_dir=config.get('paths', 'data_output_dir', fallback='../data/output'),
            product_candidates_file=config.get('paths', 'product_candidates_file', fallback='product_candidates.csv'),
            filtered_candidates_file=config.get('paths', 'filtered_candidates_file', fallback='filtered_candidates.csv'),
            final_catalog_file=config.get('paths', 'final_catalog_file', fallback='final_catalog.csv'),
            filtered_catalog_file=config.get('paths', 'filtered_catalog_file', fallback='filtered_catalog.csv'),
            optimization_results_file=config.get('paths', 'optimization_results_file', fallback='optimization_results.txt'),
            filtered_optimization_results_file=config.get('paths', 'filtered_optimization_results_file', fallback='filtered_optimization_results.txt'),
        )

        return cls(
            markup_tiers=markup_tiers,
            demand_tiers=demand_tiers,
            filter_presets=filter_presets,
            shipping=shipping,
            optimization=optimization,
            paths=paths
        )

    def get_full_path(self, filename: str) -> str:
        """Get full path for a file in data_output_dir"""
        return os.path.join(self.paths.data_output_dir, filename)
