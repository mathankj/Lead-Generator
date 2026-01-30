#!/bin/bash
# Techjays Full Workflow Automation Script
# Usage: ./fullworkflow.sh <feature-slug>

set -e

if [ -z "$1" ]; then
    echo "Usage: ./fullworkflow.sh <feature-slug>"
    echo "Example: ./fullworkflow.sh user-authentication"
    exit 1
fi

FEATURE_SLUG="$1"
LOG_FILE="workflow_${FEATURE_SLUG}_$(date +%Y%m%d_%H%M%S).log"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================"
echo "Techjays Full Workflow Automation"
echo "Feature: ${FEATURE_SLUG}"
echo "Started: $(date)"
echo "============================================"
echo ""

run_step() {
    local step_num=$1
    local step_name=$2
    local command=$3

    echo "[Step ${step_num}/9] ${step_name}..."
    echo "----------------------------------------"

    if claude -p "${command}" >> "${LOG_FILE}" 2>&1; then
        echo -e "${GREEN}[OK]${NC} ${step_name} complete"
    else
        echo -e "${YELLOW}[WARNING]${NC} ${step_name} had issues, check ${LOG_FILE}"
    fi
    echo ""
}

run_critical_step() {
    local step_num=$1
    local step_name=$2
    local command=$3

    echo "[Step ${step_num}/9] ${step_name}..."
    echo "----------------------------------------"

    if claude -p "${command}" >> "${LOG_FILE}" 2>&1; then
        echo -e "${GREEN}[OK]${NC} ${step_name} complete"
    else
        echo -e "${RED}[ERROR]${NC} ${step_name} failed, check ${LOG_FILE}"
        exit 1
    fi
    echo ""
}

# Step 1: Onboard
run_step 1 "Running Onboard" "/onboard"

# Step 2: Feature New (Critical)
run_critical_step 2 "Creating Feature: ${FEATURE_SLUG}" "/feature-new ${FEATURE_SLUG}"

# Step 3: Planner
run_step 3 "Planning Feature" "/planner ${FEATURE_SLUG}"

# Step 4: Execute
run_step 4 "Executing Implementation" "/execute ${FEATURE_SLUG}"

# Step 5: Tests
run_step 5 "Generating Tests" "/tests ${FEATURE_SLUG}"

# Step 6: Refactor
run_step 6 "Refactoring (if needed)" "/refactor ${FEATURE_SLUG}"

# Step 7: PR (Critical)
run_critical_step 7 "Creating Pull Request" "/pr ${FEATURE_SLUG}"

# Step 8: PR Comments
run_step 8 "Handling PR Comments" "/pr-comments ${FEATURE_SLUG}"

# Step 9: Submit
run_step 9 "Finalizing Submission" "/submit ${FEATURE_SLUG}"

echo "============================================"
echo -e "${GREEN}Workflow Complete!${NC}"
echo "Feature: ${FEATURE_SLUG}"
echo "Log: ${LOG_FILE}"
echo "Finished: $(date)"
echo "============================================"
