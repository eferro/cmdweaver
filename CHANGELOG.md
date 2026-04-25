# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.0] - 2026-04-25

### Added
- `Command.structural_match(tokens, context)` — keyword positions must match literally; typed slots are treated as always matching. Useful to find the command shape before validating individual arguments.
- `Command.validate_arguments(tokens, context) -> list[ArgumentError]` — per-slot validation that returns the list of failing slots (empty if all valid). Each `ArgumentError` carries `index`, `name`, `value`, `slot_str`, and `valid_options` (populated for `OptionsType` / `DynamicOptionsType`).
- `exceptions.ArgumentError` (frozen dataclass) and `exceptions.InvalidArgumentError` exception. Raised by the interpreter when exactly one structurally-matching command exists but at least one typed slot fails.

### Changed
- `Interpreter._matching_command` now falls through to structural matching when no strict match exists. Inputs that already executed correctly behave identically; previously-rejected inputs with a valid keyword prefix and an invalid typed slot now raise `InvalidArgumentError` instead of `NoMatchingCommandFoundError`, exposing per-slot diagnostics so callers can build precise error messages.

### Migration notes
- Callers that catch `NoMatchingCommandFoundError` to surface "unknown command" feedback should also catch `InvalidArgumentError` to render the new precise feedback. Genuine unknown-command inputs (no keyword prefix match) still raise `NoMatchingCommandFoundError`.
