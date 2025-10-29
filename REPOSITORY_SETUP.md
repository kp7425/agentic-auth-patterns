# Repository Setup Guide for GitLab

This document guides you through uploading this prototype to GitLab and referencing it in your paper.

## Step 1: Create GitLab Repository

### Option A: Via Web Interface

1. Go to https://gitlab.com
2. Click **"New project"** → **"Create blank project"**
3. Fill in details:
   - **Project name**: `agentic-auth-prototype`
   - **Project URL**: Choose your namespace
   - **Visibility**: Public (recommended for academic work)
   - **Initialize repository**: Uncheck (we have files already)
4. Click **"Create project"**
5. Copy the repository URL (e.g., `https://gitlab.com/username/agentic-auth-prototype.git`)

### Option B: Via GitLab CLI

```bash
# Install glab (GitLab CLI)
brew install glab  # macOS
# or download from https://gitlab.com/gitlab-org/cli

# Authenticate
glab auth login

# Create repository
glab repo create agentic-auth-prototype --public
```

## Step 2: Initialize Local Repository

Navigate to this directory and run the setup script:

```bash
cd /path/to/agentic-auth-prototype
./setup-gitlab.sh
```

The script will:
- Initialize git repository
- Add all files
- Create initial commit
- Add GitLab remote
- Set default branch to `main`

## Step 3: Push to GitLab

```bash
git push -u origin main
```

If you encounter authentication issues:

```bash
# Generate personal access token at:
# https://gitlab.com/-/profile/personal_access_tokens

# Use token as password when prompted
```

## Step 4: Configure Repository

After pushing, configure your GitLab repository:

### 4.1 Project Settings

1. **General** → **Project description**:
   ```
   Empirical validation prototype for authentication in agentic AI systems.
   Demonstrates OAuth 2.0, Token Exchange (RFC 8693), and DPoP (RFC 9449)
   composition with measured performance overhead.
   ```

2. **General** → **Topics**:
   - authentication
   - oauth2
   - token-exchange
   - dpop
   - agentic-ai
   - security
   - keycloak

### 4.2 Repository Badges

Add badges to make your repository look professional:

1. Go to **Settings** → **General** → **Badges**
2. Add these badges:

**License Badge:**
- Name: `License`
- Link: `https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype/-/blob/main/LICENSE`
- Badge image URL: `https://img.shields.io/badge/license-MIT-blue.svg`

**Pipeline Badge:**
- Name: `Pipeline`
- Link: `https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype/-/commits/main`
- Badge image URL: `https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype/badges/main/pipeline.svg`

**DOI Badge (after creating Zenodo release):**
- Name: `DOI`
- Link: `https://doi.org/YOUR_DOI`
- Badge image URL: `https://zenodo.org/badge/DOI/YOUR_DOI.svg`

### 4.3 Enable CI/CD

The repository includes `.gitlab-ci.yml` for automated testing.

1. Go to **CI/CD** → **Pipelines**
2. Pipeline should run automatically on push
3. Verify all stages pass (build, test, analyze)

### 4.4 Branch Protection

Protect the main branch:

1. Go to **Settings** → **Repository** → **Branch Rules**
2. Add rule for `main`:
   - ☑ Developers can push
   - ☑ Developers can merge
   - ☑ Require approval from code owners
   - ☑ Require passing pipeline

## Step 5: Create Zenodo Release (Optional but Recommended)

To get a DOI for citation:

1. Go to https://zenodo.org
2. Link your GitLab account
3. Enable repository: **agentic-auth-prototype**
4. Create a release on GitLab:
   ```bash
   git tag -a v1.0.0 -m "Initial release for paper submission"
   git push origin v1.0.0
   ```
5. Zenodo automatically creates DOI
6. Add DOI badge to repository
7. Update CITATION.cff with DOI

## Step 6: Update Paper References

### In LaTeX Paper

**Methodology Section (after line 234):**

```latex
The complete implementation, including Docker Compose configuration and
experiment scripts, is available at
\url{https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype}.
```

**Bibliography (references.bib):**

```bibtex
@software{bhushan2025prototype,
  author = {Bhushan, Badal and Pappu, Karthik and Mittal, Akashay},
  title = {Agentic AI Authentication Prototype},
  year = {2025},
  publisher = {GitLab},
  url = {https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype},
  doi = {10.5281/zenodo.XXXXXX}  % Add after Zenodo release
}
```

**Cite in text:**

```latex
Our prototype implementation~\cite{bhushan2025prototype} demonstrates...
```

### In Abstract (optional enhancement):

```latex
...with token caching providing 4.6× speedup. The prototype implementation
is publicly available~\cite{bhushan2025prototype}. Our analysis demonstrates...
```

## Step 7: Repository Checklist

Verify everything is ready:

- [ ] Repository is public on GitLab
- [ ] README.md displays correctly
- [ ] All code files are present
- [ ] Docker Compose builds successfully
- [ ] CI/CD pipeline passes
- [ ] License file is included
- [ ] CITATION.cff is accurate
- [ ] Repository URL is in paper
- [ ] DOI obtained (if using Zenodo)
- [ ] Repository URL is short/memorable

## Example Repository URLs

Good examples:
- ✅ `gitlab.com/username/agentic-auth-prototype`
- ✅ `gitlab.com/research-group/agentic-ai-auth`

Avoid:
- ❌ `gitlab.com/username/project-12345`
- ❌ Very long or auto-generated URLs

## Paper Footnote Format

If space is limited, use a footnote:

```latex
Our prototype implementation is publicly available.\footnote{
\url{https://gitlab.com/YOUR_USERNAME/agentic-auth-prototype}}
```

## Maintenance During Review

While your paper is under review:

1. **Don't delete the repository**
2. **Don't make breaking changes**
3. **Fix bugs in separate branches**
4. **Keep main branch stable**
5. **Respond to issues promptly**

## Support

If you encounter issues:

1. Check GitLab documentation: https://docs.gitlab.com
2. Verify git configuration: `git config --list`
3. Check SSH keys: https://gitlab.com/-/profile/keys
4. Test access: `ssh -T git@gitlab.com`

## After Paper Acceptance

Update repository:
- Add paper citation to README
- Tag release: `v1.0.0-published`
- Archive on Zenodo permanently
- Consider publishing on artifact evaluation platforms

---

**Questions?** Contact maintainers (see README.md for emails)
