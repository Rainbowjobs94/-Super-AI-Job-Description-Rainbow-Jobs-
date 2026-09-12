#!/bin/bash
# Auto PR Processor - Bash wrapper for convenient execution
# Usage: ./scripts/run_pr_processor.sh [--dry-run] [--token YOUR_TOKEN]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="$SCRIPT_DIR/auto_pr_processor.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Parse arguments
DRY_RUN=false
TOKEN=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --token)
            TOKEN="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

print_header "Auto PR Processor"

# Check prerequisites
print_warning "Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_success "Python 3 found"

if ! command -v git &> /dev/null; then
    print_error "Git is not installed"
    exit 1
fi
print_success "Git found"

# Check token
if [ -z "$TOKEN" ]; then
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GitHub token not provided"
        echo "Usage: $0 --token YOUR_TOKEN"
        echo "Or set GITHUB_TOKEN environment variable"
        exit 1
    fi
    TOKEN="$GITHUB_TOKEN"
fi
print_success "GitHub token configured"

# Install Python dependencies
print_warning "Installing Python dependencies..."
cd "$PROJECT_ROOT"
pip install -q requests pytest pytest-cov flake8 black isort || true
print_success "Dependencies installed"

# Run the processor
print_warning "Starting PR processing..."
echo ""

if [ "$DRY_RUN" = true ]; then
    print_warning "Running in DRY RUN mode - no changes will be made"
    echo ""
    python3 "$PYTHON_SCRIPT" --token "$TOKEN" --dry-run
else
    python3 "$PYTHON_SCRIPT" --token "$TOKEN"
fi

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    print_success "PR processing completed"
    if [ -f "pr_processing_report.json" ]; then
        print_success "Report saved to pr_processing_report.json"
        echo ""
        echo "Report contents:"
        cat pr_processing_report.json | python3 -m json.tool || cat pr_processing_report.json
    fi
else
    print_error "PR processing failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
