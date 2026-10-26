# Prodict documentation

| Document | For |
|---|---|
| [Tutorial](tutorial.md) | A first walk through: dict with attributes, typed models, nesting, defaults, back to JSON. |
| [Typed models](guides/typed-models.md) | Exactly which annotations convert values, which do not, and which names are reserved. |
| [Serialization](guides/serialization.md) | JSON, every `to_dict()` option, copying and pickling. |
| [Development](guides/development.md) | Setting up a checkout, running tests, linting and building. |
| [Releasing](guides/releasing.md) | How a version reaches PyPI, and what to do when an upload fails. |
| [Examples](../examples/) | Runnable programs, from the basics to a complete JSON API client. |

Every `>>>` block in the tutorial and the guides is executed by the test suite
(`pytest --doctest-glob='*.md'`), and CI runs every example, so what you read here is
what the library does.
