"""Console UI module - all print/logging statements centralized here"""
import sys


class ConsoleUI:
    """Centralized console output - can be swapped for logging, GUI, web API, etc."""
    
    VERBOSE = True
    
    @staticmethod
    def header(title: str, width: int = 80):
        """Print section header"""
        if not ConsoleUI.VERBOSE:
            return
        print("=" * width)
        print(title)
        print("=" * width)
    
    @staticmethod
    def section(title: str):
        """Print subsection"""
        if not ConsoleUI.VERBOSE:
            return
        print(f"\n{title}")
    
    @staticmethod
    def status(message: str):
        """Print status message"""
        if not ConsoleUI.VERBOSE:
            return
        print(message)
    
    @staticmethod
    def detail(message: str, indent: int = 1):
        """Print detail with indentation"""
        if not ConsoleUI.VERBOSE:
            return
        prefix = "  " * indent
        print(f"{prefix}{message}")
    
    @staticmethod
    def success(message: str):
        """Print success message"""
        if not ConsoleUI.VERBOSE:
            return
        print(f"{message}")
    
    @staticmethod
    def error(message: str):
        """Print error message to stderr"""
        print(f"ERROR: {message}", file=sys.stderr)
    
    @staticmethod
    def warning(message: str):
        """Print warning message"""
        if not ConsoleUI.VERBOSE:
            return
        print(f"WARNING: {message}")
    
    @staticmethod
    def metric(label: str, value, unit: str = ""):
        """Print metric with label and value"""
        if not ConsoleUI.VERBOSE:
            return
        if isinstance(value, (int, float)):
            if isinstance(value, float) and value > 100:
                formatted = f"{value:,.2f}"
            elif isinstance(value, int):
                formatted = f"{value:,}"
            else:
                formatted = f"{value:.2f}"
        else:
            formatted = str(value)
        
        unit_str = f" {unit}" if unit else ""
        print(f"  {label}: {formatted}{unit_str}")
    
    @staticmethod
    def progress(current: int, total: int, label: str = ""):
        """Print progress"""
        if not ConsoleUI.VERBOSE:
            return
        pct = (current / total * 100) if total > 0 else 0
        label_str = f" {label}" if label else ""
        print(f"Processed {current:,}/{total:,}... ({pct:.0f}%){label_str}")
    
    @staticmethod
    def table_header(headers: list):
        """Print table header"""
        if not ConsoleUI.VERBOSE:
            return
        print("  " + " | ".join(f"{h:20}" for h in headers))
        print("  " + "-" * (len(headers) * 23))
    
    @staticmethod
    def table_row(values: list):
        """Print table row"""
        if not ConsoleUI.VERBOSE:
            return
        print("  " + " | ".join(f"{str(v):20}" for v in values))
    
    @staticmethod
    def config_section(title: str, **params):
        """Print configuration section"""
        if not ConsoleUI.VERBOSE:
            return
        print(f"\n{title}:")
        for key, value in params.items():
            if isinstance(value, float):
                if key.endswith('_money') or 'price' in key or 'budget' in key or 'cost' in key:
                    formatted = f"${value:,.2f}"
                else:
                    formatted = f"{value:.2f}"
            elif isinstance(value, int):
                formatted = f"{value:,}"
            else:
                formatted = str(value)
            print(f"  {key}: {formatted}")
    
    @staticmethod
    def set_verbose(verbose: bool):
        """Enable/disable verbose output"""
        ConsoleUI.VERBOSE = verbose

