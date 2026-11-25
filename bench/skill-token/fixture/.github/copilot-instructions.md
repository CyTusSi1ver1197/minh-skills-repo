# Project rules
- Follow PEP 8 and use type hints on all public functions.
- Tests use the stdlib `unittest` module, in `tests/`.
- Do not add new dependencies (stdlib only).
- `python -m unittest discover -s tests -t .` must pass before work is done.
- Keep functions in `src/orders.py` small and documented.
