# Renaming Plan: boscli → cmdweaver

## Summary

This document details the plan to change all references from `boscli` to `cmdweaver` in the project.

**Total changes:** 41 references in 16 files + 1 directory

---

## 📁 Phase 1: Rename Main Directory

| Action | Source | Target |
|--------|--------|--------|
| Rename directory | `boscli/` | `cmdweaver/` |

**Note:** This automatically includes:
- `boscli/__init__.py` → `cmdweaver/__init__.py`
- `boscli/basic_types.py` → `cmdweaver/basic_types.py`
- `boscli/command.py` → `cmdweaver/command.py`
- `boscli/exceptions.py` → `cmdweaver/exceptions.py`
- `boscli/filters.py` → `cmdweaver/filters.py`
- `boscli/interpreter.py` → `cmdweaver/interpreter.py`
- `boscli/parser.py` → `cmdweaver/parser.py`
- `boscli/readlinecli/` → `cmdweaver/readlinecli/`

---

## 📦 Phase 2: Package Configuration Files

### 2.1 pyproject.toml (6 references)

| Line | Original | New |
|------|----------|-----|
| 6 | `name = "boscli"` | `name = "cmdweaver"` |
| 34 | `Homepage = "https://github.com/aleasoluciones/boscli"` | `Homepage = "https://github.com/eferro/cmdweaver"` |
| 35 | `Repository = "https://github.com/aleasoluciones/boscli"` | `Repository = "https://github.com/eferro/cmdweaver"` |
| 36 | `Issues = "https://github.com/aleasoluciones/boscli/issues"` | `Issues = "https://github.com/eferro/cmdweaver/issues"` |
| 37 | `Changelog = "https://github.com/aleasoluciones/boscli/blob/master/CHANGELOG.md"` | `Changelog = "https://github.com/eferro/cmdweaver/blob/master/CHANGELOG.md"` |
| 45 | `packages = ["boscli", "boscli.readlinecli"]` | `packages = ["cmdweaver", "cmdweaver.readlinecli"]` |

### 2.2 setup.py (1 reference)

| Line | Original | New |
|------|----------|-----|
| 19 | `setup(name='boscli',` | `setup(name='cmdweaver',` |

### 2.3 Makefile (1 reference)

| Line | Original | New |
|------|----------|-----|
| 5 | `PACKAGE_NAME = boscli` | `PACKAGE_NAME = cmdweaver` |

---

## 📚 Phase 3: Documentation

### 3.1 README.md (4 references)

| Line | Original | New |
|------|----------|-----|
| 1 | `# Boscli` | `# cmdweaver` |
| 6 | `**Boscli** is the base infrastructure...` | `**cmdweaver** is the base infrastructure...` |
| 12 | `fork of [aleasoluciones/boscli]...` | `fork of [aleasoluciones/boscli]...` (keep historical reference) |
| 28 | `To run the Boscli specs...` | `To run the cmdweaver specs...` |

---

## 🔧 Phase 4: Source Code (internal imports)

### 4.1 cmdweaver/interpreter.py (3 references)

```python
# Original:
from boscli import exceptions
from boscli import parser as parser_module
from boscli import filters

# New:
from cmdweaver import exceptions
from cmdweaver import parser as parser_module
from cmdweaver import filters
```

### 4.2 cmdweaver/command.py (1 reference)

```python
# Original:
from boscli import basic_types

# New:
from cmdweaver import basic_types
```

### 4.3 cmdweaver/readlinecli/readlinecli.py (1 reference)

```python
# Original:
from boscli import exceptions

# New:
from cmdweaver import exceptions
```

---

## 🧪 Phase 5: Tests/Specs (19 references in 8 files)

### 5.1 spec/command_spec.py (1 reference)

```python
# Original:
from boscli.command import Command

# New:
from cmdweaver.command import Command
```

### 5.2 spec/autocomplete_spec.py (3 references)

```python
# Original:
from boscli import interpreter as interpreter_module
from boscli import basic_types
from boscli.command import Command

# New:
from cmdweaver import interpreter as interpreter_module
from cmdweaver import basic_types
from cmdweaver.command import Command
```

### 5.3 spec/filters_spec.py (1 reference)

```python
# Original:
from boscli import filters

# New:
from cmdweaver import filters
```

### 5.4 spec/interpreter_spec.py (4 references)

```python
# Original:
import boscli
from boscli import exceptions, basic_types
from boscli import interpreter as interpreter_module
from boscli.command import Command

# New:
import cmdweaver
from cmdweaver import exceptions, basic_types
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command
```

### 5.5 spec/basic_types_spec.py (1 reference)

```python
# Original:
from boscli import basic_types

# New:
from cmdweaver import basic_types
```

### 5.6 spec/help_spec.py (3 references)

```python
# Original:
from boscli import basic_types
from boscli import interpreter as interpreter_module
from boscli.command import Command

# New:
from cmdweaver import basic_types
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command
```

### 5.7 spec/context_spec.py (3 references)

```python
# Original:
from boscli import exceptions, basic_types
from boscli import interpreter as interpreter_module
from boscli.command import Command

# New:
from cmdweaver import exceptions, basic_types
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command
```

### 5.8 spec/interpreter_filters_spec.py (3 references)

```python
# Original:
from boscli import exceptions
from boscli import interpreter as interpreter_module
from boscli.command import Command

# New:
from cmdweaver import exceptions
from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command
```

---

## 📝 Phase 6: Examples (5 references)

### 6.1 examples/ifaces_config.py

```python
# Original:
import boscli
from boscli import interpreter as interpreter_module
from boscli import basic_types
from boscli.command import Command
from boscli.readlinecli import readlinecli

# New:
import cmdweaver
from cmdweaver import interpreter as interpreter_module
from cmdweaver import basic_types
from cmdweaver.command import Command
from cmdweaver.readlinecli import readlinecli
```

---

## ✅ Execution Checklist

### Recommended execution order:

- [ ] **1.** Rename directory `boscli/` → `cmdweaver/`
- [ ] **2.** Update internal imports in `cmdweaver/`:
  - [ ] `cmdweaver/interpreter.py`
  - [ ] `cmdweaver/command.py`
  - [ ] `cmdweaver/readlinecli/readlinecli.py`
- [ ] **3.** Update configuration files:
  - [ ] `pyproject.toml`
  - [ ] `setup.py`
  - [ ] `Makefile`
- [ ] **4.** Update specs:
  - [ ] `spec/command_spec.py`
  - [ ] `spec/autocomplete_spec.py`
  - [ ] `spec/filters_spec.py`
  - [ ] `spec/interpreter_spec.py`
  - [ ] `spec/basic_types_spec.py`
  - [ ] `spec/help_spec.py`
  - [ ] `spec/context_spec.py`
  - [ ] `spec/interpreter_filters_spec.py`
- [ ] **5.** Update examples:
  - [ ] `examples/ifaces_config.py`
- [ ] **6.** Update documentation:
  - [ ] `README.md`
- [ ] **7.** Run tests: `make test`
- [ ] **8.** Verify everything works: `make build`

---

## ⚠️ Important Notes

1. **GitHub URLs**: Decide if the new repository will be `eferro/cmdweaver` or another path. This plan assumes `eferro/cmdweaver`.

2. **Historical reference**: In README.md line 12, the reference to the original fork `aleasoluciones/boscli` is kept as historical acknowledgment.

3. **Package version**: Consider whether the name change justifies a version bump (currently `0.9.3`).

4. **PyPI**: If the package is published on PyPI as `boscli`, a new package `cmdweaver` will need to be published.

5. **External dependencies**: Verify if there are external projects that depend on `boscli` and need to be updated.

---

## 📊 Summary by File Type

| Category | Files | References |
|----------|-------|------------|
| Directory | 1 | - |
| Configuration | 3 | 8 |
| Documentation | 1 | 4 |
| Source code | 3 | 5 |
| Tests/Specs | 8 | 19 |
| Examples | 1 | 5 |
| **TOTAL** | **17** | **41** |
