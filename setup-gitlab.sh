#!/bin/bash

# GitLab Repository Setup Script
# This script initializes the repository and pushes to GitLab

set -e

echo "=================================================="
echo "GitLab Repository Setup"
echo "=================================================="
echo

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    exit 1
fi

# Get GitLab repository URL
read -p "Enter your GitLab repository URL (e.g., https://gitlab.com/username/agentic-auth-prototype.git): " GITLAB_URL

if [ -z "$GITLAB_URL" ]; then
    echo "❌ Error: GitLab URL is required"
    exit 1
fi

echo
echo "Setting up Git repository..."

# Initialize git if not already
if [ ! -d ".git" ]; then
    git init
    echo "✓ Git repository initialized"
else
    echo "✓ Git repository already exists"
fi

# Add all files
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "⚠ No changes to commit"
else
    # Create initial commit
    git commit -m "Initial commit: Agentic AI Authentication Prototype

- OAuth 2.0 and RFC 8693 Token Exchange implementation
- RFC 9449 DPoP with ECDSA P-256
- JTI-based replay prevention
- Comprehensive measurements and analysis
- Docker Compose orchestration
- Full documentation and examples"
    echo "✓ Initial commit created"
fi

# Add remote
if git remote | grep -q "origin"; then
    echo "⚠ Remote 'origin' already exists, removing..."
    git remote remove origin
fi

git remote add origin "$GITLAB_URL"
echo "✓ Added remote: $GITLAB_URL"

# Set default branch to main
git branch -M main
echo "✓ Set default branch to 'main'"

echo
echo "=================================================="
echo "Ready to push to GitLab"
echo "=================================================="
echo
echo "Run the following command to push:"
echo
echo "    git push -u origin main"
echo
echo "After pushing, you can:"
echo "  1. Visit your GitLab repository"
echo "  2. Add project description"
echo "  3. Configure CI/CD variables if needed"
echo "  4. Enable merge request approvals"
echo "  5. Set up branch protection rules"
echo
echo "Repository setup complete! ✓"
