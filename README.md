# cmdweaver

![Python versions supported](https://img.shields.io/badge/python-3.11%20|%203.12%20|%203.13-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**cmdweaver** is a Python library for building custom command-line interfaces and ad-hoc shells.

It provides an engine for command matching, autocompletion, type verification, contextual commands, and help generation. Can be integrated with readline for advanced line editing and history.

## Features

- **Command Definition**: Define commands with keywords and typed parameters
- **Autocompletion**: Built-in completion engine for keywords and parameters
- **Type System**: Validate parameters with built-in types (String, Integer, Options, Regex, etc.)
- **Contexts**: Support for contextual command sets (like sub-menus)
- **Help System**: Automatic help generation for commands

## Installation

```bash
pip install cmdweaver
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

```python
from cmdweaver.interpreter import Interpreter
from cmdweaver.command import Command
from cmdweaver import basic_types

# Create interpreter
interpreter = Interpreter()

# Define command handler
def greet(name, **kwargs):
    print(f"Hello, {name}!")

# Add command: "greet <name>"
interpreter.add_command(
    Command(["greet", basic_types.StringType("name")], greet, help="Greet someone")
)

# Execute command
interpreter.eval("greet World")  # Output: Hello, World!
```

## Defining Commands

Commands are defined with a list of keywords and parameter types:

```python
from cmdweaver.command import Command
from cmdweaver import basic_types

# Simple keyword-only command
Command(["show", "status"], show_status_func)

# Command with string parameter
Command(["set", "name", basic_types.StringType()], set_name_func)

# Command with options parameter
Command(["set", "mode", basic_types.OptionsType(["fast", "slow"])], set_mode_func)

# Command with multiple parameters
Command(
    ["copy", basic_types.StringType("source"), basic_types.StringType("dest")],
    copy_func
)
```

## Parameter Types

| Type | Description | Example |
|------|-------------|---------|
| `StringType()` | Any non-empty string | `"hello"`, `"123"` |
| `IntegerType(min, max)` | Integer with optional bounds | `42`, `-5` |
| `BoolType()` | Boolean (`true`/`false`) | `true`, `false` |
| `OptionsType(options)` | One of predefined options | `"opt1"`, `"opt2"` |
| `DynamicOptionsType(func)` | Options from a function | Dynamic list |
| `RegexType(pattern)` | String matching regex | Pattern match |
| `OrType(type1, type2, ...)` | Any of the given types | Union type |

## Autocompletion

Get completions for partial input:

```python
interpreter.complete("gr")       # Returns: {"greet "}
interpreter.complete("greet ")   # Returns completions for the name parameter
```

## Contexts

Commands can be scoped to specific contexts:

```python
# Command only available in "config" context
Command(["set", "value"], set_func, context_name="config")

# Command always available regardless of context
Command(["exit"], exit_func, always=True)

# Enter/exit contexts
interpreter.push_context("config")
interpreter.pop_context()
```

## Help System

Get help for commands:

```python
# Help for commands matching partial input
interpreter.help("set")  # Returns dict of matching commands with their help text

# Help for all commands
interpreter.all_commands_help()
```

## Argument Validation Errors

When an input lines up with a registered command's keyword shape but a typed
slot rejects the value (e.g. `OptionsType(["prod", "staging"])` receives
`banana`), the interpreter raises `InvalidArgumentError` with per-slot
diagnostics — instead of the generic `NoMatchingCommandFoundError`. This lets
callers surface precise feedback like *"argument `env` is `banana`. Valid
values: `prod`, `staging`."*

```python
from cmdweaver.exceptions import InvalidArgumentError

try:
    interpreter.eval("aws key reset banana")
except InvalidArgumentError as error:
    print(error.command)                  # aws key reset <env>
    for arg in error.argument_errors:
        print(arg.index, arg.name, arg.value, arg.valid_options)
        # 3 env banana ['prod', 'staging']
```

`InvalidArgumentError.argument_errors` is a list of `ArgumentError` records:

| Field | Description |
|-------|-------------|
| `index` | Position of the failing token (0-based). |
| `name` | Slot name (from `BaseType(name=...)`); `None` if the slot was unnamed. |
| `value` | Raw token the caller supplied. |
| `slot_str` | Human-readable slot representation (e.g. `<env>`, `<prod\|staging>`). |
| `valid_options` | List of accepted values for `OptionsType` / `DynamicOptionsType`; `None` for other types. |

The interpreter dispatch order is unchanged for valid inputs:

1. **Strict matches first** — if exactly one command matches keywords *and* validates every typed slot, it executes (today's happy path).
2. **Structural matches next** — keywords match and length is right, but at least one typed slot fails. Exactly one structural match raises `InvalidArgumentError`; multiple structural matches raise `AmbiguousCommandError`.
3. **No match** — `NoMatchingCommandFoundError`, as before.

You can also call the new `Command.structural_match(tokens, context)` and
`Command.validate_arguments(tokens, context)` directly if you want to drive
your own dispatch.

## About this Fork

This project is a fork of [aleasoluciones/boscli](https://github.com/aleasoluciones/boscli). While we acknowledge and appreciate the original work, this fork follows its own direction with different goals and development priorities.

## Development

### Setup

```bash
pip install -r requirements-dev.txt
pip install -e .
```

### Testing

```bash
make test          # Run all tests
make test-coverage # Run tests with coverage report
make validate      # Run tests + style + typing checks
```

### Code Quality

```bash
make check-typing  # Type checking with mypy
make check-style   # Linting with ruff
make reformat      # Auto-format code
```

## Contributing

If you'd like to contribute, fork this repository and send a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.
