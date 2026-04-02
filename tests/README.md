# Tests

This directory is scaffolded for future unit and integration tests.

## Strategy

Tests are deferred until the `swag/` module design stabilizes. Once it does,
the priority areas for coverage are:

- `swag/config.py` — `swag_config` loading, machine detection, merging, validation,
  derived path computation, and `to_env_dict()` output.
- `swag/grid.py`, `swag/topo.py`, `swag/maps.py`, `swag/domain.py` — path-helper
  functions (pure Python, no HPC dependencies) and command-string construction.
- `swag/util.py` — `run_cmd()` error handling.

## Running Tests

```shell
python -m pytest tests/
```

## Notes

- Workflow stages that call HPC tools (MBDA, homme_tool, ncremap, etc.) require
  a real compute node and are not suitable for unit tests. Test those functions'
  command-string logic in isolation by mocking `run_cmd()`.
- Integration tests for full pipeline stages can be run on an interactive node
  using a small test grid (e.g. ne4).
</content>
</invoke>