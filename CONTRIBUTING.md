# Project scope

## In scope
 * support for Legato 100 syringe pump

## Contributions welcome
 * check compatibility with other syringe pumps
 * alternative synchronous controller
 * more interesting examples of usage

# Developer setup
```
poetry shell
poetry install --with dev
```

# Tests
A suite of pytest tests is available in [tests](./tests/).
These can be run in two modes:
 * Online: requires a Legato 100 syringe pump to be connected to the computer
 * Offline: uses mock responses collected during online tests

Further, a small set of tests is available to test the motion control functionality of the pump. These tests will move the plunger if a pump is connected. They are disabled by default and can be run with the `--motion` flag.

```bash
pytest
pytest --offline
pytest --motion
```