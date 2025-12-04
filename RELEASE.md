# Release Process

This document describes how to create releases for Naytrik.

## Versioning

Naytrik follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backwards-compatible)
- **PATCH** version: Bug fixes (backwards-compatible)

## Creating a Release

### 1. Update Version Numbers

Update the version in the following files:
- `pyproject.toml` → `version = "X.Y.Z"`
- `naytrik/__init__.py` → `__version__ = "X.Y.Z"`

### 2. Update Changelog

Add release notes to `CHANGELOG.md`:
- Move items from `[Unreleased]` to the new version section
- Add the release date
- Update the comparison links at the bottom

### 3. Commit Version Bump

```bash
git add pyproject.toml naytrik/__init__.py CHANGELOG.md
git commit -m "chore: bump version to X.Y.Z"
```

### 4. Create Git Tag

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

### 5. Create GitHub Release

1. Go to [Releases](https://github.com/vikas-rajpoot/naytrik/releases)
2. Click "Draft a new release"
3. Select the tag `vX.Y.Z`
4. Title: `Naytrik vX.Y.Z`
5. Copy release notes from CHANGELOG.md
6. Publish the release

## Recommended Tags

For GitHub Topics, use:
- `browser-automation`
- `ai-automation`
- `playwright`
- `gemini-ai`
- `workflow-automation`
- `record-and-playback`
- `python`
- `web-automation`
- `test-automation`
- `rpa`

## Repository Description

Suggested description for the repository:

> 🚀 AI-Powered Browser Automation - Record workflows once with Gemini AI, replay infinitely without it. Combines intelligent recording with fast, deterministic playback.

## Release Checklist

- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Version numbers are bumped
- [ ] CHANGELOG.md is updated
- [ ] Git tag is created
- [ ] GitHub release is published
- [ ] Package is published to PyPI (if applicable)

## Example Release Notes Template

```markdown
## What's New in vX.Y.Z

### ✨ New Features
- Feature 1 description
- Feature 2 description

### 🐛 Bug Fixes
- Fix 1 description
- Fix 2 description

### 📚 Documentation
- Documentation updates

### 🔧 Maintenance
- Dependency updates
- Code improvements

### ⚠️ Breaking Changes
- Description of any breaking changes

### 📦 Installation

\`\`\`bash
pip install naytrik==X.Y.Z
\`\`\`

### 🙏 Contributors
Thanks to all contributors who made this release possible!
```
