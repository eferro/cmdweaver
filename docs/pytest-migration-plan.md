# Migration Plan: mamba → pytest

## Summary

This document details the plan to migrate the test suite from **mamba** (BDD framework) to **pytest** (standard Python testing framework).

**Current state:**
- 8 spec files in `spec/` directory
- 122 test examples total
- Uses mamba BDD syntax (`describe`, `context`, `it`, `before.each`)
- Uses hamcrest for assertions
- Uses doublex for mocking/spying

**Target state:**
- Test files in `tests/unit/` directory
- pytest as test runner
- Keep hamcrest for assertions (familiar matchers)
- Keep doublex for mocking (already works well)

---

## 📊 Test Files Inventory

| Current File | Tests | Target File |
|--------------|-------|-------------|
| `spec/command_spec.py` | 1 | `tests/unit/test_command.py` |
| `spec/interpreter_spec.py` | ~40 | `tests/unit/test_interpreter.py` |
| `spec/basic_types_spec.py` | ~50 | `tests/unit/test_basic_types.py` |
| `spec/filters_spec.py` | 6 | `tests/unit/test_filters.py` |
| `spec/autocomplete_spec.py` | ~15 | `tests/unit/test_autocomplete.py` |
| `spec/context_spec.py` | ~20 | `tests/unit/test_context.py` |
| `spec/help_spec.py` | 8 | `tests/unit/test_help.py` |
| `spec/interpreter_filters_spec.py` | ~10 | `tests/unit/test_interpreter_filters.py` |
| **TOTAL** | **122** | |

---

## 🔄 Syntax Translation Guide

### Test Structure

```python
# MAMBA (before)
with describe('Command'):
    with context('when doing X'):
        with it('does Y'):
            # test code

# PYTEST (after)
class TestCommand:
    class TestWhenDoingX:
        def test_does_y(self):
            # test code

# OR simpler flat structure:
def test_command_does_y_when_doing_x():
    # test code
```

### Setup/Teardown

```python
# MAMBA (before)
with describe('Interpreter'):
    with before.each:
        self.interpreter = Interpreter()
        self.spy = Spy()

# PYTEST (after) - using fixtures
@pytest.fixture
def interpreter():
    return Interpreter()

@pytest.fixture
def spy():
    return Spy()

def test_something(interpreter, spy):
    # use interpreter and spy
```

### Assertions (keep hamcrest)

```python
# These remain the same - hamcrest works with pytest
from hamcrest import assert_that, is_, has_length
assert_that(result, is_(expected))
assert_that(items, has_length(3))
```

### Mocking (keep doublex)

```python
# These remain the same - doublex works with pytest
from doublex import Spy, Stub, when, called
spy = Spy()
assert_that(spy.method, called().with_args('arg'))
```

---

## 📁 New Directory Structure

```
cmdweaver/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   └── unit/
│       ├── __init__.py
│       ├── test_command.py
│       ├── test_interpreter.py
│       ├── test_basic_types.py
│       ├── test_filters.py
│       ├── test_autocomplete.py
│       ├── test_context.py
│       ├── test_help.py
│       └── test_interpreter_filters.py
├── spec/                        # Remove after migration
└── ...
```

---

## 📦 Dependency Changes

### requirements-dev.txt

```diff
- mamba
+ pytest
+ pytest-cov
  pyhamcrest
  doublex
  coverage
- coveralls
```

### pyproject.toml additions

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"

[tool.coverage.run]
source = ["cmdweaver"]
omit = ["tests/*"]
```

---

## 🔧 Makefile Updates

```makefile
# Current
test:
	mamba $(SPEC_DIR)

test-coverage:
	coverage run --source=$(PACKAGE_NAME) -m mamba $(SPEC_DIR)

# New
test-unit:
	pytest tests/unit -v

test-coverage:
	pytest tests/unit --cov=$(PACKAGE_NAME) --cov-report=term-missing
```

---

## ✅ Execution Phases

### Phase 1: Setup Infrastructure
- [ ] Create `tests/` directory structure
- [ ] Create `tests/__init__.py` and `tests/unit/__init__.py`
- [ ] Create `tests/conftest.py` with shared fixtures
- [ ] Update `requirements-dev.txt`
- [ ] Update `pyproject.toml` with pytest configuration
- [ ] Update `Makefile` with new test targets

### Phase 2: Migrate Tests (one file at a time)
- [ ] **2.1** `command_spec.py` → `test_command.py` (1 test - warmup)
- [ ] **2.2** `filters_spec.py` → `test_filters.py` (6 tests - simple)
- [ ] **2.3** `autocomplete_spec.py` → `test_autocomplete.py` (~15 tests)
- [ ] **2.4** `help_spec.py` → `test_help.py` (8 tests)
- [ ] **2.5** `interpreter_filters_spec.py` → `test_interpreter_filters.py` (~10 tests)
- [ ] **2.6** `context_spec.py` → `test_context.py` (~20 tests)
- [ ] **2.7** `basic_types_spec.py` → `test_basic_types.py` (~50 tests)
- [ ] **2.8** `interpreter_spec.py` → `test_interpreter.py` (~40 tests - largest)

### Phase 3: Cleanup
- [ ] Verify all 122 tests pass with pytest
- [ ] Remove `spec/` directory
- [ ] Remove `mamba` from dependencies
- [ ] Update documentation (README.md)
- [ ] Final commit

---

## 🔀 Example Migration: command_spec.py

### Before (mamba)

```python
from hamcrest import is_
from doublex import assert_that

from cmdweaver.command import Command

with describe('Command'):
    with it('Allow to assign a command ID'):
        command = Command(['k1', 'k2'], cmd_id='cmd_id1')

        assert_that(command.cmd_id, is_('cmd_id1'))
```

### After (pytest)

```python
from hamcrest import is_
from doublex import assert_that

from cmdweaver.command import Command


class TestCommand:
    def test_allows_assigning_a_command_id(self):
        command = Command(['k1', 'k2'], cmd_id='cmd_id1')

        assert_that(command.cmd_id, is_('cmd_id1'))
```

---

## 🔀 Example Migration: interpreter_spec.py (with fixtures)

### Before (mamba)

```python
with describe('Interpreter'):
    with before.each:
        self.interpreter = interpreter_module.Interpreter()
        self.cmds_implementation = Spy()
        self._add_command(['cmd', 'key'], self.cmds_implementation.cmd, cmd_id='id1')

    def _add_command(self, tokens, func, cmd_id=None):
        self.interpreter.add_command(Command(tokens, func, cmd_id=cmd_id))

    with context('command execution'):
        with describe('when evaluating empty line'):
            with it('returns none'):
                assert_that(self.interpreter.eval(''), none())
```

### After (pytest)

```python
import pytest
from hamcrest import none
from doublex import Spy, assert_that, called

from cmdweaver import interpreter as interpreter_module
from cmdweaver.command import Command


class TestInterpreter:
    @pytest.fixture
    def interpreter(self):
        return interpreter_module.Interpreter()

    @pytest.fixture
    def cmds_implementation(self):
        return Spy()

    @pytest.fixture
    def interpreter_with_commands(self, interpreter, cmds_implementation):
        def add_command(tokens, func, cmd_id=None):
            interpreter.add_command(Command(tokens, func, cmd_id=cmd_id))
        
        add_command(['cmd', 'key'], cmds_implementation.cmd, cmd_id='id1')
        return interpreter, cmds_implementation, add_command

    class TestCommandExecution:
        def test_returns_none_when_evaluating_empty_line(self, interpreter):
            assert_that(interpreter.eval(''), none())
```

---

## ⚠️ Important Notes

1. **Incremental migration**: Migrate one file at a time, run tests after each migration.

2. **Keep both test suites temporarily**: During migration, both mamba and pytest can coexist.

3. **Fixture composition**: Complex setups can use fixture composition to avoid repetition.

4. **Test naming**: Use descriptive function names that describe the behavior being tested.

5. **Helper classes**: Test helper classes (like `PlainCompletionsType` in autocomplete_spec.py) should be moved to `tests/conftest.py` or a dedicated `tests/helpers.py`.

6. **Run count verification**: After migration, verify the test count matches (122 tests).

---

## 📈 Migration Order Rationale

The migration order is based on:
1. **Complexity**: Start with simplest files (fewer tests, simpler setup)
2. **Dependencies**: Files with fewer dependencies first
3. **Learning curve**: Build experience before tackling larger files

| Order | File | Reason |
|-------|------|--------|
| 1 | command_spec | Simplest (1 test, no fixtures) |
| 2 | filters_spec | Simple (6 tests, basic setup) |
| 3 | autocomplete_spec | Medium (includes helper classes) |
| 4 | help_spec | Medium complexity |
| 5 | interpreter_filters_spec | Medium, uses filters |
| 6 | context_spec | More complex setup |
| 7 | basic_types_spec | Large but straightforward |
| 8 | interpreter_spec | Largest, most complex |

---

## 🕐 Estimated Effort

| Phase | Estimated Time |
|-------|---------------|
| Phase 1: Infrastructure | 15-30 min |
| Phase 2.1-2.2: Simple files | 30 min |
| Phase 2.3-2.5: Medium files | 1-2 hours |
| Phase 2.6-2.8: Large files | 2-3 hours |
| Phase 3: Cleanup | 15-30 min |
| **TOTAL** | **4-6 hours** |

---

## 🚀 Ready to Start?

To begin the migration, the recommended approach is:

1. Start with Phase 1 (infrastructure setup)
2. Migrate `command_spec.py` first as a proof of concept
3. Run both test suites in parallel until fully migrated
4. Complete remaining files incrementally

