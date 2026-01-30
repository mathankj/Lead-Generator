# Techjays Full Workflow Automation Script for PowerShell
# Usage: .\fullworkflow.ps1 -FeatureSlug <feature-slug>

param(
    [Parameter(Mandatory=$true)]
    [string]$FeatureSlug
)

$ErrorActionPreference = "Continue"
$LogFile = "workflow_${FeatureSlug}_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

function Write-StepHeader {
    param([string]$StepNum, [string]$StepName)
    Write-Host ""
    Write-Host "[Step $StepNum/9] $StepName..." -ForegroundColor Cyan
    Write-Host "----------------------------------------"
}

function Run-Step {
    param(
        [string]$StepNum,
        [string]$StepName,
        [string]$Command,
        [bool]$Critical = $false
    )

    Write-StepHeader $StepNum $StepName

    try {
        $output = claude -p $Command 2>&1
        $output | Out-File -Append -FilePath $LogFile

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] $StepName complete" -ForegroundColor Green
        } else {
            if ($Critical) {
                Write-Host "[ERROR] $StepName failed, check $LogFile" -ForegroundColor Red
                exit 1
            } else {
                Write-Host "[WARNING] $StepName had issues, check $LogFile" -ForegroundColor Yellow
            }
        }
    } catch {
        if ($Critical) {
            Write-Host "[ERROR] $StepName failed: $_" -ForegroundColor Red
            exit 1
        } else {
            Write-Host "[WARNING] $StepName had issues: $_" -ForegroundColor Yellow
        }
    }
}

Write-Host "============================================" -ForegroundColor Magenta
Write-Host "Techjays Full Workflow Automation" -ForegroundColor Magenta
Write-Host "Feature: $FeatureSlug" -ForegroundColor Magenta
Write-Host "Started: $(Get-Date)" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta

# Step 1: Onboard
Run-Step "1" "Running Onboard" "/onboard"

# Step 2: Feature New (Critical)
Run-Step "2" "Creating Feature: $FeatureSlug" "/feature-new $FeatureSlug" -Critical $true

# Step 3: Planner
Run-Step "3" "Planning Feature" "/planner $FeatureSlug"

# Step 4: Execute
Run-Step "4" "Executing Implementation" "/execute $FeatureSlug"

# Step 5: Tests
Run-Step "5" "Generating Tests" "/tests $FeatureSlug"

# Step 6: Refactor
Run-Step "6" "Refactoring (if needed)" "/refactor $FeatureSlug"

# Step 7: PR (Critical)
Run-Step "7" "Creating Pull Request" "/pr $FeatureSlug" -Critical $true

# Step 8: PR Comments
Run-Step "8" "Handling PR Comments" "/pr-comments $FeatureSlug"

# Step 9: Submit
Run-Step "9" "Finalizing Submission" "/submit $FeatureSlug"

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Workflow Complete!" -ForegroundColor Green
Write-Host "Feature: $FeatureSlug" -ForegroundColor Green
Write-Host "Log: $LogFile" -ForegroundColor Green
Write-Host "Finished: $(Get-Date)" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
