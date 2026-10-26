# Import changes: v0.2.0 → v0.3.0

Version 0.3 reorganizes the existing v0.2 implementation into smaller, named subpackages. **Acquisition, parsing and storage semantics are intended to remain unchanged**; paths to many Python modules have changed. The CLI executable name (`balance-measurement`) and normal TOML structure are preserved.

| v0.2 Python import path | v0.3 path |
|---|---|
| `balance_measurement.domain` | `balance_measurement.core.models` |
| `balance_measurement.exceptions` | `balance_measurement.core.exceptions` |
| `balance_measurement.client` | `balance_measurement.scale.client` |
| `balance_measurement.transport` | `balance_measurement.scale.transport` |
| `balance_measurement.protocols` | `balance_measurement.scale.protocols` |
| `balance_measurement.acquisition` | `balance_measurement.acquisition` (public API; implementation in `.session`) |
| `balance_measurement.storage` | `balance_measurement.storage` (unchanged) |
| `balance_measurement.analysis` | `balance_measurement.data.analysis` |
| `balance_measurement.data_processing` | `balance_measurement.data.processing` |
| `balance_measurement.config` | `balance_measurement.config` (public API; implementation in `.settings`) |
| `balance_measurement.timing` | `balance_measurement.times` |
| `balance_measurement.app_logging` | `balance_measurement.logging` |
| `balance_measurement.plotting` | `balance_measurement.visualization` |
| `balance_measurement.reporting` | `balance_measurement.reporting` (public API; implementation in `.reports`) |
| `balance_measurement.cli` | `balance_measurement.interfaces.cli` |
| `balance_measurement.gui` | `balance_measurement.interfaces.gui` |

### Example

Previously:

```python
from balance_measurement.client import ScaleClient
from balance_measurement.protocols import default_registry
from balance_measurement.transport import SerialSettings, SerialTransport
```

Now:

```python
from balance_measurement import ScaleClient, SerialSettings, SerialTransport, default_registry
```

Internal helpers, such as finite decimal parsing, now live under `utils/`. When starting a new script, prefer the public imports used by the README rather than importing implementation files directly.

**Important:** This migration is separate from the original `BalanceLib.py` → rebuilt API migration documented in [MIGRATION.md](MIGRATION.md). There is no automatic source-code rewrite for legacy users.
