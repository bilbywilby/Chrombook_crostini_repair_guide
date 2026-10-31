# Test Suite Reference

The repository test suite checks project structure and selected repository behavior.

## Run tests

From the repository root, run:

```bash
python3 -m unittest discover -s tests -v
```

If the project dependencies are required, install the pinned packages listed in `requirements.txt` in the intended Python environment before running tests.

## CI

The Python CI workflow tests the supported Python versions configured in the workflow. A local pass is useful, but CI may expose differences between Python versions or environments.

## Before committing

- Run the test suite from the repository root.
- Review `git status` and `git diff`.
- Do not commit generated reports or runtime files unless they are intended project artifacts.
