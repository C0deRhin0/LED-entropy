# Contributing to LED-Entropy

Thank you for your interest in contributing to this hardware entropy project! This document outlines the guidelines for contributions.

## Project Scope

LED-Entropy is a hardware-software hybrid project. Contributions may involve:

- **Hardware**: Arduino sketches, circuit designs, sensor integration
- **Software**: Python entropy extraction, OpenCV pipelines, camera capture
- **Documentation**: Wiring guides, tutorials, setup walkthroughs
- **Testing**: Entropy quality analysis, benchmark data, validation scripts

## Getting Started

1. **Review the README** to understand the full system architecture
2. **Read the roadmap** in `plan/roadmap.md` to see planned features
3. **Check existing Issues** for tasks that need attention
4. **Set up the hardware** (or use the provided test video files) to run validation

## Development Workflow

### 1. Fork and Clone

```bash
git clone https://github.com/C0deRhin0/LED-Entropy.git
cd LED-Entropy/codebase
```

### 2. Create a Branch

```bash
git checkout -b feat/your-feature-name
# or
git checkout -b fix/your-bug-fix
# or
git checkout -b docs/your-doc-update
```

### 3. Make Changes

- **Arduino code**: Follow the coding conventions in `plan/coding_convention.md`
- **Python code**: Keep functions focused, use descriptive names, add docstrings
- **Documentation**: Write for a beginner audience — assume the reader has basic electronics knowledge but not expert-level experience

### 4. Test Your Changes

- **Arduino**: Upload to an Uno and verify LED behavior with Serial Monitor
- **Python**: Run against test data: `python entropy_core.py --frames ./test_frames/`
- **Entropy quality**: Check output with `ent` or the chi-square test

### 5. Commit Guidelines

This project uses conventional commit prefixes:

| Prefix | When to Use |
|--------|-------------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix or correction |
| `docs:` | Documentation changes only |
| `chore:` | Tooling, config, or infrastructure |
| `test:` | Adding or updating tests |
| `refactor:` | Code restructuring without behavior change |

**Commit messages should be concise** (aim for 50-72 characters in the summary line).

```bash
git add <changed-files>
git commit -m "feat: add entropy extraction from multiple LSBs"
```

### 6. Push and Open a PR

```bash
git push origin feat/your-feature-name
# Then open a Pull Request on GitHub
```

## Pull Request Checklist

Before submitting, ensure:

- [ ] Arduino sketches compile without warnings in Arduino IDE
- [ ] Python scripts pass: `python -m py_compile <file>`
- [ ] New features include documentation updates
- [ ] No debug prints or commented-out code left in
- [ ] Hardware contributions include wiring instructions
- [ ] Entropy analysis includes test data or validation approach
- [ ] Commit messages follow the conventional format

## Hardware Contribution Notes

If you're contributing circuit modifications or sensor additions:

1. Include a **Mermaid diagram** or Fritzing breadboard layout
2. List exact **component specifications** (values, tolerances, ratings)
3. Document **verification steps** — how to confirm the circuit works
4. If adding a new entropy source, provide **before/after quality metrics**

## Code Style

### Arduino (C++)

- Use `const int` or `#define` for pin declarations
- Never use `delay()` in main loop — use `millis()`-based timing
- Avoid `String` class (causes heap fragmentation on Uno)
- Call `randomSeed()` exactly once in `setup()`

### Python

- Use descriptive function and variable names
- Add docstrings for all public functions
- Keep line length under 100 characters
- Use NumPy vectorized operations over Python loops

## Questions?

Open a [GitHub Issue](https://github.com/C0deRhin0/LED-Entropy/issues) for:
- Bugs in the entropy extraction pipeline
- Hardware compatibility questions
- Suggestions for additional entropy sources
- Documentation improvements

---

*Every contribution, no matter how small, helps make this entropy source better. Thank you!*
