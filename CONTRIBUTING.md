# Contributing

Thanks for helping. Bug reports, documentation fixes and pull requests are all welcome.

## Reporting a bug

Open an issue with the
[bug report form](https://github.com/ramazanpolat/prodict/issues/new?template=bug_report.yml).
It asks for the Python version, the prodict version (`pip show prodict`), a minimal snippet
that reproduces the problem, and what you expected instead.

Security problems go through private reporting instead; see [SECURITY.md](SECURITY.md).

## Making a change

1. Fork the repository and create a branch.
2. Set up and run the tests (see [docs/guides/development.md](docs/guides/development.md)):

   ```bash
   uv run pytest
   ```

3. Add or update tests in `test_prodict.py` for behavior changes. If the change affects
   documented behavior, update `docs/` and `examples/` too; their code runs in CI.
4. Add a line under `Unreleased` in [CHANGELOG.md](CHANGELOG.md).
5. Open a pull request. CI runs the tests on Python 3.8 through 3.15.

Releases are cut by the maintainer; see [docs/guides/releasing.md](docs/guides/releasing.md).
