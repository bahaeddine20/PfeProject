# PowerShell cleanup script for GitLab CI
# This script helps clean up virtual environments and temporary files

param(
    [switch]$Force
)

Write-Host "Starting cleanup process..." -ForegroundColor Green

# Function to safely remove directory
function Remove-DirectorySafely {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        Write-Host "Removing $Description: $Path" -ForegroundColor Yellow
        try {
            # First, try to remove read-only attributes
            Get-ChildItem -Path $Path -Recurse -Force | ForEach-Object {
                if ($_.Attributes -match "ReadOnly") {
                    $_.Attributes = $_.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly)
                }
            }
            
            # Remove the directory
            Remove-Item -Path $Path -Recurse -Force -ErrorAction Stop
            Write-Host "Successfully removed $Description" -ForegroundColor Green
        }
        catch {
            Write-Host "Warning: Could not remove $Description: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "$Description not found: $Path" -ForegroundColor Gray
    }
}

# Function to safely remove file
function Remove-FileSafely {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        Write-Host "Removing $Description: $Path" -ForegroundColor Yellow
        try {
            # Remove read-only attribute if present
            $file = Get-Item -Path $Path -Force
            if ($file.Attributes -match "ReadOnly") {
                $file.Attributes = $file.Attributes -band (-bnot [System.IO.FileAttributes]::ReadOnly)
            }
            
            Remove-Item -Path $Path -Force -ErrorAction Stop
            Write-Host "Successfully removed $Description" -ForegroundColor Green
        }
        catch {
            Write-Host "Warning: Could not remove $Description: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "$Description not found: $Path" -ForegroundColor Gray
    }
}

# Clean up virtual environments
Remove-DirectorySafely -Path "venv" -Description "Root virtual environment"
Remove-DirectorySafely -Path "ServeurFlaskHost/venv" -Description "Flask server virtual environment"
Remove-DirectorySafely -Path "env" -Description "Alternative virtual environment"
Remove-DirectorySafely -Path ".venv" -Description "Hidden virtual environment"

# Clean up Python cache
Remove-DirectorySafely -Path "__pycache__" -Description "Python cache directory"
Get-ChildItem -Path "." -Recurse -Directory -Name "__pycache__" | ForEach-Object {
    Remove-DirectorySafely -Path $_ -Description "Python cache subdirectory"
}

# Clean up log files
Remove-FileSafely -Path "flask.log" -Description "Flask log file"
Remove-FileSafely -Path "flask_error.log" -Description "Flask error log file"
Remove-FileSafely -Path "flask_pid.txt" -Description "Flask PID file"
Remove-FileSafely -Path "ServeurFlaskHost/flask.log" -Description "Flask server log file"
Remove-FileSafely -Path "ServeurFlaskHost/flask_error.log" -Description "Flask server error log file"
Remove-FileSafely -Path "ServeurFlaskHost/flask_pid.txt" -Description "Flask server PID file"

# Clean up Robot Framework files
Remove-FileSafely -Path "log.html" -Description "Robot Framework log"
Remove-FileSafely -Path "output.xml" -Description "Robot Framework output"
Remove-FileSafely -Path "report.html" -Description "Robot Framework report"

# Clean up temporary files
Get-ChildItem -Path "." -Recurse -File -Include "*.tmp", "*.temp", "*.log" | ForEach-Object {
    Remove-FileSafely -Path $_.FullName -Description "Temporary file"
}

# Force cleanup if requested
if ($Force) {
    Write-Host "Performing forced cleanup..." -ForegroundColor Red
    
    # Kill any remaining Python processes
    try {
        Get-Process -Name "python" -ErrorAction SilentlyContinue | Stop-Process -Force
        Write-Host "Killed remaining Python processes" -ForegroundColor Green
    }
    catch {
        Write-Host "No Python processes to kill" -ForegroundColor Gray
    }
    
    # Additional aggressive cleanup
    Get-ChildItem -Path "." -Recurse -Directory -Name "venv*" | ForEach-Object {
        Remove-DirectorySafely -Path $_ -Description "Virtual environment (forced)"
    }
}

Write-Host "Cleanup process completed!" -ForegroundColor Green 