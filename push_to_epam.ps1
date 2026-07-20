# PowerShell Script to Push Repository to EPAM GitLab
# Preserves all commit history and pushes to EPAM remote

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Push to EPAM GitLab Repository" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# EPAM GitLab URL
$epamUrl = "https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop.git"

# Step 1: Check current directory
Write-Host "📁 Current Directory:" -ForegroundColor Yellow
Get-Location
Write-Host ""

# Step 2: Check if git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ Error: Not a git repository!" -ForegroundColor Red
    Write-Host "   Run 'git init' first or navigate to your git repository." -ForegroundColor Red
    exit 1
}

# Step 3: Check current remotes
Write-Host "🔍 Current Git Remotes:" -ForegroundColor Yellow
git remote -v
Write-Host ""

# Step 4: Check if 'epam' remote already exists
$existingRemote = git remote | Select-String "epam"
if ($existingRemote) {
    Write-Host "⚠️  Remote 'epam' already exists!" -ForegroundColor Yellow
    $response = Read-Host "Do you want to remove and re-add it? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Write-Host "Removing existing 'epam' remote..." -ForegroundColor Yellow
        git remote remove epam
        Write-Host "✅ Removed" -ForegroundColor Green
    } else {
        Write-Host "Skipping remote addition..." -ForegroundColor Yellow
    }
} else {
    Write-Host "➕ Adding EPAM GitLab as remote..." -ForegroundColor Yellow
    git remote add epam $epamUrl
    Write-Host "✅ Remote 'epam' added successfully!" -ForegroundColor Green
}
Write-Host ""

# Step 5: Verify remotes
Write-Host "🔍 Updated Git Remotes:" -ForegroundColor Yellow
git remote -v
Write-Host ""

# Step 6: Check current branch
Write-Host "🌿 Current Branch:" -ForegroundColor Yellow
$currentBranch = git branch --show-current
Write-Host "   $currentBranch" -ForegroundColor Cyan
Write-Host ""

# Step 7: Check git status
Write-Host "📊 Git Status:" -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 8: Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "⚠️  WARNING: You have uncommitted changes!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Uncommitted files:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $response = Read-Host "Do you want to commit them now? (y/n)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        git add .
        $commitMsg = Read-Host "Enter commit message"
        if ([string]::IsNullOrWhiteSpace($commitMsg)) {
            $commitMsg = "Prepare for EPAM GitLab migration"
        }
        git commit -m $commitMsg
        Write-Host "✅ Changes committed!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Proceeding without committing changes..." -ForegroundColor Yellow
    }
    Write-Host ""
}

# Step 9: Confirm push
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  Ready to Push" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Target Repository:" -ForegroundColor Yellow
Write-Host "   $epamUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Branch to push:" -ForegroundColor Yellow
Write-Host "   $currentBranch" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will push all commits and history to EPAM GitLab." -ForegroundColor White
Write-Host ""

$response = Read-Host "Do you want to proceed? (y/n)"
if ($response -ne 'y' -and $response -ne 'Y') {
    Write-Host "❌ Push cancelled by user." -ForegroundColor Red
    exit 0
}

# Step 10: Push to EPAM
Write-Host ""
Write-Host "🚀 Pushing to EPAM GitLab..." -ForegroundColor Green
Write-Host "   You may be prompted for credentials..." -ForegroundColor Yellow
Write-Host ""

try {
    git push epam $currentBranch

    Write-Host ""
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host "  ✅ SUCCESS!" -ForegroundColor Green
    Write-Host "=====================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your code has been pushed to EPAM GitLab!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📍 Repository URL:" -ForegroundColor Yellow
    Write-Host "   https://git.garage.epam.com/data-scientist-in-the-loop/data-scientist-in-the-loop" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Visit the URL above to verify your code" -ForegroundColor White
    Write-Host "   2. Check that all files and commits are present" -ForegroundColor White
    Write-Host "   3. Update README.md if needed" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "=====================================================================" -ForegroundColor Red
    Write-Host "  ❌ PUSH FAILED!" -ForegroundColor Red
    Write-Host "=====================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common Issues:" -ForegroundColor Yellow
    Write-Host "   1. Authentication failed - Check credentials" -ForegroundColor White
    Write-Host "   2. Permission denied - Check repository access" -ForegroundColor White
    Write-Host "   3. Repository not found - Verify URL is correct" -ForegroundColor White
    Write-Host ""
    Write-Host "Solutions:" -ForegroundColor Yellow
    Write-Host "   • Use Personal Access Token instead of password" -ForegroundColor White
    Write-Host "   • Create token at: https://git.garage.epam.com/-/profile/personal_access_tokens" -ForegroundColor White
    Write-Host "   • Ensure you have write access to the repository" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 See docs/GIT_MIGRATION_GUIDE.md for detailed troubleshooting" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Step 11: Optional - Push all branches
Write-Host "Additional Options:" -ForegroundColor Yellow
Write-Host ""
$response = Read-Host "Do you want to push all branches? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Pushing all branches..." -ForegroundColor Yellow
    git push epam --all
    Write-Host "✅ All branches pushed!" -ForegroundColor Green
}
Write-Host ""

$response = Read-Host "Do you want to push all tags? (y/n)"
if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host "Pushing all tags..." -ForegroundColor Yellow
    git push epam --tags
    Write-Host "✅ All tags pushed!" -ForegroundColor Green
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "  🎉 All Done!" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""
