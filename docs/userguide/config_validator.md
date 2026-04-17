# A2Bridge JSON Configuration Validator

A standalone Python script that validates A2Bridge device configuration files
against the official schema for both **Master** and **Slave** device roles.

---

## Requirements

| Requirement | Details |
|---|---|
| Python | 3.9 or newer |
| Third-party library | `jsonschema >= 4.0` |

Install the dependency before first use:

```bash
pip install "jsonschema>=4.0"
```

No other packages, no project installation needed — the script runs as a
single downloaded file.

---

## Availability

The script is part of the [A2Bridge SDK repository](https://github.com/int2code/a2bridge) at path:

```
tools/json_config_validator/config_validator.py
```

No project installation is needed — download or clone the repo and run the script directly.

---

## Usage

```
python config_validator.py JSON_FILE [--mode {master,slave,auto}]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `JSON_FILE` | Yes | Path to the A2Bridge `.json` configuration file to validate. |
| `--mode`, `-m` | No | Schema to validate against: `master`, `slave`, or `auto` (default). When `auto` the role is read from the `A2BRole` field inside the file. When `master` or `slave` is given the script also asserts that `A2BRole` matches. |

### Examples

Auto-detect device role from the file:

```bash
python config_validator.py config.json
```

Force a specific schema:

```bash
python config_validator.py master.json --mode master
python config_validator.py slave.json  --mode slave
```

Show built-in help:

```bash
python config_validator.py --help
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Config is valid |
| `1` | Validation failed — errors are printed to **stderr** |
| `2` | Bad command-line arguments |
---

## What is validated

Validation runs in three sequential layers. A later layer is skipped if an
earlier one fails.

### 1. JSON Standard Compliance

- The file exists and is readable.
- The file is encoded in UTF-8.
- The content is syntactically valid JSON.
- The top-level value is a JSON object (`{...}`).

When a syntax error is found the output includes the offending line and a
caret pointing at the column:

```
[FAIL] Config is invalid (? mode):
  - Invalid JSON syntax at line 14, col 5: Expecting ',' delimiter
      "SupplyVoltage": 5000
      ^
```

### 2. Schema Validation

Checks that every required field is present and holds a valid value.

**Fields required in every config (Master and Slave)**

| Field | Type | Notes |
|---|---|---|
| `Version` | `string` | Pattern `\d+\.\d+` — e.g. `"1.32"` |
| `Name` | `string` |  |
| `ResetOnNew` | `"True"` \| `"False"` | String, not boolean |
| `LogLevel` | `string` | `debug` `info` `warning` `error` `critical` |
| `A2BRole` | `"Master"` \| `"Slave"` | Drives schema selection |
| `AudioResolution` | `integer` | `16`, `24`, or `32` |
| `UsbInputChannels` | `integer` | ≥ 1 |
| `UsbOutputChannels` | `integer` | ≥ 1 |
| `RunInProtobufMode` | `"True"` \| `"False"` | String, not boolean |
| `SupplyVoltage` | `integer` | ≥ 0, in mV |
| `AudioRouteMatrixDownstream` | `array of arrays` | Each inner value ≥ 1 |
| `AudioRouteMatrixUpstream` | `array of arrays` | Each inner value ≥ 1 |

**Additional field required when `A2BRole` is `"Master"`**

`A2BMasterConfig` — object with:

| Field | Type | Notes |
|---|---|---|
| `SlavesOnBus` | `integer` | ≥ 1 |
| `DnSlots` | `integer` | ≥ 0 |
| `UpSlots` | `integer` | ≥ 0 |
| `AutoDiscovery` | `"True"` \| `"False"` | |
| `SlaveConfiguration` | `array` | At least 1 entry; see below |

Each entry in `SlaveConfiguration`:

| Field | Type | Allowed values |
|---|---|---|
| `Node` | `integer` | ≥ 0 |
| `DnSlots` | `integer` | ≥ 0 |
| `LocalDnSlots` | `integer` | ≥ 0 |
| `UpSlots` | `integer` | ≥ 0 |
| `LocalUpSlots` | `integer` | ≥ 0 |
| `PowerConfig` | `string` | `"High"` or `"Low"` |
| `CableLength` | `integer` | ≥ 0 (metres) |
| `ConfigureTDM` | `"True"` \| `"False"` | |
| `TdmTxLines` | `integer` | ≥ 0 |
| `TdmRxLines` | `integer` | ≥ 0 |
| `TDMMode` | `string` | `TDM2` `TDM4` `TDM8` `TDM12` `TDM16` `TDM20` `TDM24` `TDM32` |
| `TDMOptions` | `array of strings` | Any subset of `EARLY` `ALT` `INV` `RXBCLKINV` `TXBCLKINV` `TDMSS` `INTERLEAVE` |

**Additional field required when `A2BRole` is `"Slave"`**

`A2BSlaveConfig` — object with:

| Field | Type | Notes |
|---|---|---|
| `TdmRxChannels` | `integer` | ≥ 0 |
| `TdmTxChannels` | `integer` | ≥ 0 |

### 3. Cross-Field Consistency

Checks relationships between fields that JSON Schema cannot express:

- `AudioRouteMatrixDownstream` rows count must not be higher than `UsbInputChannels`.
- `AudioRouteMatrixUpstream` rows count must not be higher than `UsbOutputChannels`.
- *(Master only)* `A2BMasterConfig.SlavesOnBus` must equal the number of
  entries in `A2BMasterConfig.SlaveConfiguration`.
- *(Slave only)* `AudioRouteMatrixUpstream` row count must not exceed
  `A2BSlaveConfig.TdmRxChannels` — each row is one A2B channel the slave
  receives, so all rows must fit within the declared receive capacity.
- *(Slave only)* The highest A2B channel index referenced in any cell of
  `AudioRouteMatrixDownstream` must not exceed `A2BSlaveConfig.TdmTxChannels`
  — the slave can only transmit as many A2B channels as `TdmTxChannels`
  allows.

---

## Output Examples

**Valid config**

```
[OK] Config is valid (master mode)
```

**Invalid config**

```
[FAIL] Config is invalid (master mode):
  - at 'AudioResolution': 20 is not one of [16, 24, 32]
  - at 'A2BMasterConfig -> SlaveConfiguration -> 0 -> PowerConfig': 'Medium' is not one of ['High', 'Low']
```

**Mode mismatch**

```
[FAIL] Config is invalid (slave mode):
  - 'A2BRole' in file is 'Master' but validation mode is 'slave' – mismatch.
```


