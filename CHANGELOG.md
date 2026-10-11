# Changelog

## 2026-10-11

### Info output consistency

- `InfoPoint.info()`, `InfoData.info()`, and `IMarkov.info()` return `msg` as a list of individual lines without embedded trailing newline characters.
- The corresponding `__str__()` methods join those lines and append one newline after each line.
- `InfoData.info(full=True)` emits point details as separate lines.
- Nested Markov reports use `info(full=True)` to include their points and descendants.
