# CLAUDE.md - Parent Repository Guidelines

## ⚠️ IMPORTANT: This is a Parent Repository

**ALL development work should be done in the `zipbusiness-api` submodule.**

### Repository Structure
```
zipbusiness/                    # Parent repository (YOU ARE HERE)
├── zipbusiness-api/           # Submodule - ALL WORK GOES HERE
├── ENGINEERING_HANDOFF*.md    # Documentation only
├── scripts/                   # Migration/setup scripts only
└── CLAUDE.md                  # This file
```

## 🚨 Critical Rules

1. **NEVER implement API functionality in this parent repository**
2. **ALWAYS work in the zipbusiness-api submodule**
3. **This repository is for documentation and coordination only**

## 📁 Where to Work

### For ANY Restaurant/API Related Work:
```bash
cd zipbusiness-api/
# Read CLAUDE.md in that directory for guidelines
cat CLAUDE.md
```

### What Belongs in Parent Repo:
- ✅ Engineering documentation
- ✅ Migration scripts
- ✅ Setup/deployment scripts
- ✅ Integration tests that span multiple services
- ❌ **NOT** API code
- ❌ **NOT** Business logic
- ❌ **NOT** Database models

## 🔄 Working with Submodules

### Initial Setup
```bash
git submodule update --init --recursive
```

### Making Changes
```bash
# 1. Enter the submodule
cd zipbusiness-api/

# 2. Make your changes
# ... edit files ...

# 3. Commit in submodule
git add .
git commit -m "Your changes"
git push origin main

# 4. Update parent repo reference
cd ..
git add zipbusiness-api
git commit -m "Update zipbusiness-api submodule"
git push origin main
```

### Pulling Latest Changes
```bash
git pull
git submodule update --recursive
```

## 🎯 Single Source of Truth

**The `zipbusiness-api` IS the single source of truth for:**
- All restaurant data
- All API endpoints
- All business logic
- All data models
- All services
- All caching
- All monitoring

**DO NOT create parallel implementations anywhere else.**

## 📋 Quick Navigation

- **API Development**: `cd zipbusiness-api/`
- **API Guidelines**: `cat zipbusiness-api/CLAUDE.md`
- **API Documentation**: `cat zipbusiness-api/README.md`
- **Engineering Docs**: `cat ENGINEERING_HANDOFF*.md`

---

**Remember: If you're writing code, you should be in `zipbusiness-api/`**

*Last Updated: 2025-01-09*
*Version: 1.0*