# Purely 💧

**A lightweight elixir for cleaner, safer, and more fluent Python.**

![PyPI - Version](https://img.shields.io/pypi/v/purely)
![PyPi - Python Version](https://img.shields.io/pypi/pyversions/purely)
![Github - Open Issues](https://img.shields.io/github/issues-raw/apiad/purely)
![PyPi - Downloads (Monthly)](https://img.shields.io/pypi/dm/purely)
![Github - Commits](https://img.shields.io/github/commit-activity/m/apiad/purely)

---

**Purely** is a zero-dependency library designed to bring the best parts of functional programming—safety, pipelines, and immutability—into Python without the academic overhead or complex types. It allows you to write code that reads from top to bottom, rather than inside out.

## 📦 Installation

**Purely** leverages modern Python features (generics) and requires **Python 3.12+**.

```bash
pip install purely
```

## ✨ Features

* **Functional Containers**: `Option` for null-safety and `Result` for explicit error handling.
* **Safe Navigation**: Access deeply nested attributes without worrying about `AttributeError`.
* **Fluent Pipelines**: Chain operations and vectorize list transformations with `Chain` and `pipe`.
* **Architectural Decoupling**: Interface-aware Dependency Injection and Multiple Dispatch.
* **Ergonomic Currying**: Partial application with full type-hint support for IDEs.

## 📚 User Guide

The guide lives in [`docs/chapters/`](docs/chapters/). It follows the backend of a small online bookshop: each chapter starts from a job the shop needs done, solves it in plain Python, and then shows the one or two ideas from purely that make it simpler, ending with a checkout that uses all of them. Every code block in it runs against the package when it is built (`make docs`), and the task chapters write the programs in [`docs/examples/`](docs/examples/).

## 🛠 Contribution

We use `uv` for dependency management and a `makefile` for orchestration.

1. **Setup**: Clone the repository and run `make`.
2. **Formatting**: Ensure code adheres to `black` formatting using `make format`.
3. **Testing**: Run the full test suite with `make test-all`.
4. **Docs**: Edit the chapters, never `docs/examples/`, and run `make docs-check` before a release.

## 📝 License

Distributed under the MIT License.