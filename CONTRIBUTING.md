# Dev setup
```
poetry shell
poetry install
```

# Tests
A suite of pytest tests is available in [tests](./tests/).
These can be run in two modes:
 * Online: requires a Legato 100 syringe pump to be connected to the computer
 * Offline: uses mock responses collected during online tests

Corresponding commands:
```bash
pytest
pytest --offline
```