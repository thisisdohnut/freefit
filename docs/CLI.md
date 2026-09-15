# CLI Specification

## Commands

```bash
freefit                       # open interactive TUI
freefit status                # system/provider summary
freefit models                # endpoint board
freefit providers             # provider board
freefit detail <endpoint>    # endpoint detail
freefit compare <a> <b>      # compare endpoints
freefit bench                 # run default benchmark
freefit bench --all           # benchmark all eligible endpoints
freefit probe <endpoint>      # one live speed probe
freefit health                # current health states
freefit routes                # routing matrix
freefit discover              # refresh provider catalogs
freefit quota                 # quota/free-state report
freefit observatory           # historical/live signals
freefit export --json        # machine-readable registry + scores
freefit doctor                # diagnostics
```

## Global options

```text
--config <path>
--db <path>
--provider <id>
--model <id>
--free-only
--healthy-only
--json
--no-color
--verbose
```

## Output contract

Human output optimizes scanning. JSON output is a stable machine contract and should not rely on terminal formatting.

## Exit codes

```text
0 success
1 general failure
2 invalid arguments
3 configuration error
4 provider unavailable
5 benchmark failure
6 no eligible endpoint
```

## Agent integration

Agents should prefer:

```bash
freefit routes --json
freefit detail <endpoint> --json
freefit status --json
```

The router must be usable without parsing colored text.
