#!/bin/bash

# Online Shop Optimization System - Usage Guide
# This script helps run the optimization workflow

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON_DIR="$SCRIPT_DIR/python"
DATA_DIR="$SCRIPT_DIR/data/output"
JAVA_DIR="$SCRIPT_DIR/java"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

case "$1" in
    generate-aggressive)
        print_header "Generating Aggressive Candidate Set (~10k)"
        cd "$PYTHON_DIR"
        python3 productcreator.py --filter-mode=aggressive
        print_success "Candidates saved to: $DATA_DIR/product_candidates.json"
        ;;
    
    generate-medium)
        print_header "Generating Medium Candidate Set (~100k)"
        cd "$PYTHON_DIR"
        python3 productcreator.py --filter-mode=medium
        print_success "Candidates saved to: $DATA_DIR/product_candidates.json"
        ;;
    
    generate-full)
        print_header "Generating Full Candidate Set (~1.5M)"
        cd "$PYTHON_DIR"
        python3 productcreator.py --filter-mode=full
        print_success "Candidates saved to: $DATA_DIR/product_candidates.json"
        ;;
    
    optimize-batch)
        print_header "Running Batch Optimizer (Fast, High Memory)"
        if [ ! -f "$DATA_DIR/product_candidates.json" ]; then
            echo "Error: product_candidates.json not found!"
            echo "Run './run.sh generate-aggressive' first"
            exit 1
        fi
        cd "$PYTHON_DIR"
        python3 batch_optimizer.py "$DATA_DIR/product_candidates.json"
        print_success "Results saved to: $DATA_DIR/optimization_results.json"
        ;;
    
    optimize-filtered)
        print_header "Running Filtered Optimizer (Safe, Low Memory)"
        cd "$PYTHON_DIR"
        python3 filtered_optimizer.py --filter-mode=aggressive
        print_success "Results saved to: $DATA_DIR/filtered_catalog.json"
        ;;
    
    results)
        print_header "Generated Results"
        echo "Files in $DATA_DIR:"
        ls -lh "$DATA_DIR"/ 2>/dev/null || echo "No results yet. Run an optimizer first."
        ;;
    
    java-build)
        print_header "Building Java Simulator"
        cd "$JAVA_DIR"
        mvn clean package
        print_success "Java simulator built"
        ;;
    
    java-run)
        print_header "Running Java Simulator"
        cd "$JAVA_DIR"
        java -cp target/classes se.lexicon.Main
        ;;
    
    *)
        cat << 'EOF'
Online Shop Optimization System

Usage: ./run.sh [command]

GENERATE CANDIDATES:
  generate-aggressive     Generate ~10k candidates (fast, safe)
  generate-medium        Generate ~100k candidates (medium)
  generate-full          Generate ~1.5M candidates (slow, high RAM)

RUN OPTIMIZATION:
  optimize-batch         Batch optimizer (fast, high memory)
  optimize-filtered      Filtered optimizer (safe, low memory)

VIEW RESULTS:
  results                List generated output files

JAVA SIMULATOR:
  java-build            Build Java simulator with Maven
  java-run              Run Java simulator

EXAMPLE WORKFLOW:
  ./run.sh generate-aggressive
  ./run.sh optimize-batch
  ./run.sh results
  ./run.sh java-build
  ./run.sh java-run

For more details, see:
  - README.md                           (Overview)
  - docs/CONFIGURATION_GUIDE.md         (Config parameters)
  - docs/ARCHITECTURE_FIXES.md          (Architecture)
  - docs/EVALUATION_GUIDE.md            (Results interpretation)
EOF
        ;;
esac
