# Capsule Schema (v1.1)

The Living Engine proof capsule is a compact JSON document emitted by the SDK and backtest harness.
At minimum, a capsule should expose the following keys:

| Field           | Type   | Description |
| --------------- | ------ | ----------- |
| `schema_version`| str    | Version tag for downstream validation, e.g. `"capsule-1.1.0"`. |
| `created_utc`   | str    | ISO-8601 timestamp produced when the capsule was generated. |
| `data_source`   | str    | Identifier for the originating data feed ("in-memory", "csv", etc.). |
| `data_sha256`   | str    | Hex digest of the raw dataset so you can reproduce the run. |
| `params`        | object | Strategy configuration that produced the run. |
| `verdict`       | str    | Status emitted by the strategy ("OPEN", "P≠NP (claim)", ...). |
| `evidence`      | object | Arbitrary supporting notes or counters collected during execution. |
| `metrics`       | object | Key summary statistics (sharpe, drawdown, trade counts, ...). |

Additional metadata is welcome, but these core fields allow the research pipeline to associate
outputs from the SDK, backtest harness, and live systems.
