# Releasing

Releases are published by CI. Merging to `master` publishes to PyPI exactly when the
`version` in `pyproject.toml` is not on PyPI yet.

## Steps

1. Bump `version` in `pyproject.toml` (for example `0.8.22` to `0.8.23`).
2. Move the `Unreleased` entries in `CHANGELOG.md` under a heading for the new version
   and date.
3. Open a pull request. CI runs the test matrix and builds the distribution.
4. Merge to `master`. The `deploy` job then:
   - builds the sdist and wheel and runs `twine check`;
   - asks PyPI whether the version exists, and stops here if it does;
   - uploads to TestPyPI, then to PyPI.
5. Once the version is on PyPI, tag the release commit, push the tag and create a
   GitHub release from the changelog section (recommended; CI does not need either):

   ```bash
   git tag -a v0.8.23 -m "prodict 0.8.23" && git push origin v0.8.23
   gh release create v0.8.23 --title "prodict 0.8.23" --notes-file notes.md
   ```

A push to `master` that does not change the version publishes nothing, so documentation
and CI changes can be merged at any time.

## Credentials

The upload steps read two repository secrets, `TESTPYPI_TOKEN` and `PYPI_TOKEN`, through
`TWINE_PASSWORD`. Tokens are never written to a file or printed. To rotate one, create the
new token on PyPI, replace the secret in the repository settings, confirm the next release
uploads, then revoke the old token.

## When an upload fails

- **Before anything reached PyPI** (for example a bad token): fix the cause and re-run the
  failed `deploy` job. TestPyPI tolerates files it already has.
- **After part of a release reached PyPI** (for example the wheel uploaded and the sdist
  did not): CI will not finish it, because the version now exists on PyPI and `deploy`
  skips the upload. Upload the missing file by hand from the release commit:

  ```bash
  git checkout <release commit>
  uv build
  uvx twine upload --skip-existing dist/*
  ```

  PyPI never accepts the same file name twice, so a release with a wrong file is fixed
  with a new version, not by replacing files.
