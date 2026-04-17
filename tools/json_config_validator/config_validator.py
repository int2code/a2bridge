"""A2Bridge JSON configuration validator.

Validates A2Bridge device JSON configuration files against the official schema
for both ``Master`` and ``Slave`` device roles.

=============================================================================
STANDALONE USAGE
=============================================================================

Requirements
------------
Python 3.9 or newer and the ``jsonschema`` library::

    pip install "jsonschema>=4.0"

Running the validator
---------------------
Auto-detect the device role from the ``A2BRole`` field inside the file::

    python config_validator.py config.json

Force a specific schema (also asserts that ``A2BRole`` matches)::

    python config_validator.py master.json --mode master
    python config_validator.py slave.json  --mode slave
Exit codes::

    0  – Config is valid
    1  – Validation failed  (errors are printed to stderr)
    2  – Bad CLI arguments
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

try:
    from jsonschema import Draft7Validator, ValidationError
except ImportError as _import_error:  # pragma: no cover
    raise ImportError(
        "The 'jsonschema' package is required for JSON validation. "
        "Install it with:  pip install 'jsonschema>=4.0'"
    ) from _import_error


class ConfigMode(str, Enum):
    """A2B device role / configuration mode."""

    MASTER = "master"
    SLAVE = "slave"
    AUTO = "auto"


@dataclass
class ValidationResult:
    """Result of a :func:`validate_config` call.

    Attributes:
        is_valid:   ``True`` when the config passes every validation check.
        mode:       Detected or requested :class:`ConfigMode` (never ``AUTO``).
        errors:     Human-readable list of error strings.  Empty when valid.
    """

    is_valid: bool
    mode: Optional[ConfigMode]
    errors: list[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover
        if self.is_valid:
            return f"[OK] Config is valid ({self.mode.value} mode)"
        lines = [
            f"[FAIL] Config is invalid ({self.mode.value if self.mode else '?'} mode):"
        ]
        for error in self.errors:
            lines.append(f"  - {error}")
        return "\n".join(lines)


# JSON Schema definitions

_STRING_BOOL = {"type": "string", "enum": ["True", "False"]}

_ROUTE_MATRIX = {
    "type": "array",
    "minItems": 1,
    "items": {
        "type": "array",
        "minItems": 1,
        "items": {"type": "integer", "minimum": 1},
    },
    "description": "Each row is a USB channel; each element is an A2B channel number.",
}

_SLAVE_CONFIGURATION_ITEM: dict = {
    "type": "object",
    "required": [
        "Node",
        "DnSlots",
        "LocalDnSlots",
        "UpSlots",
        "LocalUpSlots",
        "PowerConfig",
        "CableLength",
        "ConfigureTDM",
        "TdmTxLines",
        "TdmRxLines",
        "TDMMode",
        "TDMOptions",
    ],
    "additionalProperties": False,
    "properties": {
        "Node": {
            "type": "integer",
            "minimum": 0,
            "description": "Node number, counting from 0.",
        },
        "DnSlots": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of channels forwarded downward.",
        },
        "LocalDnSlots": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of slots from upstream consumed by this node.",
        },
        "UpSlots": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of slots forwarded upward.",
        },
        "LocalUpSlots": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of slots produced by this node towards master.",
        },
        "PowerConfig": {
            "type": "string",
            "enum": ["High", "Low"],
            "description": "Power configuration for this slave node.",
        },
        "CableLength": {
            "type": "integer",
            "minimum": 0,
            "description": "Length of the cable to the upper node (m).",
        },
        "ConfigureTDM": {
            **_STRING_BOOL,
            "description": "If True, A2Bridge configures slave TDM settings.",
        },
        "TdmTxLines": {
            "type": "integer",
            "minimum": 0,
            "description": "TDM TX lines from A2B transceiver to slave µC.",
        },
        "TdmRxLines": {
            "type": "integer",
            "minimum": 0,
            "description": "TDM RX lines from slave µC to A2B transceiver.",
        },
        "TDMMode": {
            "type": "string",
            "enum": [
                "TDM2",
                "TDM4",
                "TDM8",
                "TDM12",
                "TDM16",
                "TDM20",
                "TDM24",
                "TDM32",
            ],
            "description": "Number of channels per TDM frame.",
        },
        "TDMOptions": {
            "type": "array",
            "uniqueItems": True,
            "items": {
                "type": "string",
                "enum": [
                    "EARLY",
                    "ALT",
                    "INV",
                    "RXBCLKINV",
                    "TXBCLKINV",
                    "TDMSS",
                    "INTERLEAVE",
                ],
            },
            "description": "Additional TDM flags.",
        },
    },
}

_A2B_MASTER_CONFIG: dict = {
    "type": "object",
    "required": [
        "SlavesOnBus",
        "DnSlots",
        "UpSlots",
        "AutoDiscovery",
        "SlaveConfiguration",
    ],
    "additionalProperties": False,
    "properties": {
        "SlavesOnBus": {
            "type": "integer",
            "minimum": 1,
            "description": "Number of slave nodes on the A2B bus.",
        },
        "DnSlots": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of downstream slots going out from master.",
        },
        "UpSlots": {
            "type": "integer",
            "minimum": 0,
            "description": "Number of upstream slots coming in to master.",
        },
        "AutoDiscovery": {
            **_STRING_BOOL,
            "description": "If True, re-triggers discovery every 500 ms until Normal state.",
        },
        "SlaveConfiguration": {
            "type": "array",
            "minItems": 1,
            "items": _SLAVE_CONFIGURATION_ITEM,
            "description": "Per-slave node configuration table.",
        },
    },
}

_A2B_SLAVE_CONFIG: dict = {
    "type": "object",
    "required": ["TdmRxChannels", "TdmTxChannels"],
    "additionalProperties": False,
    "properties": {
        "TdmRxChannels": {
            "type": "integer",
            "minimum": 0,
            "description": "TDM RX channels from A2B transceiver to slave µC.",
        },
        "TdmTxChannels": {
            "type": "integer",
            "minimum": 0,
            "description": "TDM TX channels from slave µC to A2B transceiver.",
        },
    },
}

_COMMON_PROPERTIES: dict = {
    "Version": {
        "type": "string",
        "pattern": r"^\d+\.\d+$",
        "description": "Config format version; must be compatible with firmware (e.g. '1.32').",
    },
    "Name": {
        "type": "string",
        "minLength": 0,
        "description": "Human-readable label for this configuration.",
    },
    "ResetOnNew": {
        **_STRING_BOOL,
        "description": "If True, device resets when a new configuration is uploaded.",
    },
    "LogLevel": {
        "type": "string",
        "enum": ["debug", "info", "warning", "error", "off"],
        "description": "Logging verbosity level.",
    },
    "A2BRole": {
        "type": "string",
        "enum": ["Master", "Slave"],
        "description": "A2B role of this device ('Master' or 'Slave').",
    },
    "AudioResolution": {
        "type": "integer",
        "enum": [16, 24, 32],
        "description": "Audio resolution in bits per sample.",
    },
    "UsbInputChannels": {
        "type": "integer",
        "minimum": 1,
        "description": "Number of audio channels sent from the PC to the device.",
    },
    "UsbOutputChannels": {
        "type": "integer",
        "minimum": 1,
        "description": "Number of audio channels sent from the device to the PC.",
    },
    "RunInProtobufMode": {
        **_STRING_BOOL,
        "description": "If True, device auto-starts in protobuf COM port mode.",
    },
    "SupplyVoltage": {
        "type": "integer",
        "minimum": 0,
        "description": "USB PD voltage in mV to supply the A2B bus.",
    },
    "AudioRouteMatrixDownstream": {
        **_ROUTE_MATRIX,
        "description": (
            "Routing from USB input channels to A2B output channels. "
            "Number of rows must equal UsbInputChannels."
        ),
    },
    "AudioRouteMatrixUpstream": {
        **_ROUTE_MATRIX,
        "description": (
            "Routing from A2B channels to USB output channels. "
            "Number of rows must equal UsbOutputChannels."
        ),
    },
    # Both role-specific blocks are optional at the property level;
    # the mode-specific 'required' list enforces the correct one.
    "A2BMasterConfig": _A2B_MASTER_CONFIG,
    "A2BSlaveConfig": _A2B_SLAVE_CONFIG,
}

_COMMON_REQUIRED: list[str] = [
    "Version",
    "Name",
    "ResetOnNew",
    "LogLevel",
    "A2BRole",
    "AudioResolution",
    "UsbInputChannels",
    "UsbOutputChannels",
    "RunInProtobufMode",
    "SupplyVoltage",
    "AudioRouteMatrixDownstream",
    "AudioRouteMatrixUpstream",
]

MASTER_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "A2Bridge Master Configuration",
    "description": "Validates a device configuration with A2BRole set to 'Master'.",
    "type": "object",
    "required": [*_COMMON_REQUIRED, "A2BMasterConfig"],
    "additionalProperties": False,
    "properties": _COMMON_PROPERTIES,
}

SLAVE_SCHEMA: dict = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "A2Bridge Slave Configuration",
    "description": "Validates a device configuration with A2BRole set to 'Slave'.",
    "type": "object",
    "required": [*_COMMON_REQUIRED, "A2BSlaveConfig"],
    "additionalProperties": False,
    "properties": _COMMON_PROPERTIES,
}

_SCHEMA_MAP: dict[ConfigMode, dict] = {
    ConfigMode.MASTER: MASTER_SCHEMA,
    ConfigMode.SLAVE: SLAVE_SCHEMA,
}


def _detect_mode(config: dict) -> Optional[ConfigMode]:
    """Return the :class:`ConfigMode` derived from the ``A2BRole`` field, or ``None``."""
    role = config.get("A2BRole", "")
    if role == "Master":
        return ConfigMode.MASTER
    if role == "Slave":
        return ConfigMode.SLAVE
    return None


def _format_error(err: ValidationError) -> str:
    """Convert a :class:`jsonschema.ValidationError` to a concise human-readable string.

    :param err: Raw validation error produced by :class:`jsonschema.Draft7Validator`.
    :returns: Single-line string with the field path and the violation message.
    """
    path = " -> ".join(str(p) for p in err.absolute_path)
    location = f"at '{path}'" if path else "at root"
    return f"{location}: {err.message}"


def _load_and_parse_json(
    json_path: Path,
) -> tuple[Optional[dict], Optional[ValidationResult]]:
    """Read a JSON file from disk and parse it into a Python dict.

    Handles file-encoding and JSON-syntax errors.  On a syntax error the
    message includes the offending source line with a caret pointing at the
    column where the parser failed.


    :param json_path: Absolute or relative path to the JSON file.
    :returns:
        ``(config_dict, None)`` on success, or ``(None, result)`` where
        *result* is a failed :class:`ValidationResult` describing the error.
    """
    raw_text = ""
    try:
        raw_text = json_path.read_text(encoding="utf-8")
        config = json.loads(raw_text)
    except UnicodeDecodeError as exc:
        return None, ValidationResult(
            is_valid=False,
            mode=None,
            errors=[f"File encoding error (expected UTF-8): {exc}"],
        )
    except json.JSONDecodeError as exc:
        lines = raw_text.splitlines()
        bad_line = lines[exc.lineno - 1] if 0 < exc.lineno <= len(lines) else ""
        error_msg = (
            f"Invalid JSON syntax at line {exc.lineno}, col {exc.colno}: {exc.msg}"
        )
        if bad_line:
            error_msg += f"\n    {bad_line}\n    {' ' * (exc.colno - 1)}^"
        return None, ValidationResult(is_valid=False, mode=None, errors=[error_msg])

    if not isinstance(config, dict):
        return None, ValidationResult(
            is_valid=False,
            mode=None,
            errors=["Top-level JSON value must be an object ({...})."],
        )

    return config, None


def _resolve_config_mode(
    mode: "ConfigMode | str",
    config: dict,
    errors: list[str],
) -> Optional[ConfigMode]:
    """Resolve the effective :class:`ConfigMode` from the request and the parsed config.

    When *mode* is ``AUTO`` the role is read from the ``A2BRole`` field.
    When a specific mode is forced, a mismatch with ``A2BRole`` is recorded in
    *errors* but resolution still succeeds so that all remaining errors are
    collected in the same pass.

    :param mode: Requested mode, or the string ``'auto'``.
    :param config: Parsed configuration dict; must contain ``A2BRole``.
    :param errors: Mutable list; a mismatch error is appended when the forced
        mode conflicts with the ``A2BRole`` field.
    :returns:
        Resolved :class:`ConfigMode`, or ``None`` when auto-detection fails
        because ``A2BRole`` is absent or has an unrecognised value.
    """
    if isinstance(mode, str):
        mode = ConfigMode(mode.lower())

    detected = _detect_mode(config)

    if mode is ConfigMode.AUTO:
        return detected  # None signals "cannot detect"

    if detected is not None and detected != mode:
        errors.append(
            f"'A2BRole' in file is {config.get('A2BRole')!r} but "
            f"validation mode is '{mode.value}' – mismatch."
        )
    return mode


def _validate_against_schema(
    config: dict,
    mode: ConfigMode,
    errors: list[str],
) -> list:
    """Run JSON Schema validation and collect all violations.

    :param config: Parsed configuration dict to validate.
    :param mode: Resolved :class:`ConfigMode` that selects the correct schema.
    :param errors: Mutable list; a human-readable message is appended for each
        schema violation found.
    :returns:
        List of raw :class:`jsonschema.ValidationError` objects, empty when the
        config is schema-valid.  The caller uses this to decide whether to
        proceed with cross-field consistency checks.
    """
    schema = _SCHEMA_MAP[mode]
    validator = Draft7Validator(schema)
    schema_errors = sorted(
        validator.iter_errors(config), key=lambda e: list(e.absolute_path)
    )
    for err in schema_errors:
        errors.append(_format_error(err))
    return schema_errors


def _run_consistency_checks(
    config: dict,
    mode: ConfigMode,
    errors: list[str],
) -> None:
    """Run cross-field semantic checks that cannot be expressed in JSON Schema.

    Should only be called after :func:`_validate_against_schema` confirms the
    config is structurally valid, since these checks assume required fields are
    present and of the correct type.

    :param config: Parsed, schema-valid configuration dict.
    :param mode: Resolved :class:`ConfigMode` of the configuration.
    :param errors: Mutable list; a message is appended for each inconsistency
        found.
    """
    _check_matrix_row_count(config, errors)
    if mode is ConfigMode.MASTER:
        _check_master_slave_count(config, errors)
    if mode is ConfigMode.SLAVE:
        _check_slave_tdm_channels(config, errors)


def validate_config(
    json_path: "str | Path",
    mode: "ConfigMode | str" = ConfigMode.AUTO,
) -> ValidationResult:
    """Validate an A2Bridge JSON configuration file.

    Performs three layers of checks in order:

    1. **JSON standard compliance** – file exists, is valid UTF-8, and parses
       as JSON with a top-level object.
    2. **Schema validation** – all required fields are present with correct
       types and values for the detected or requested device role.
    3. **Cross-field consistency** – routing matrix row counts match the
       declared USB channel counts; for Master configs, ``SlavesOnBus``
       matches the number of ``SlaveConfiguration`` entries.

    Layers 2 and 3 are skipped when layer 1 fails; layer 3 is skipped when
    layer 2 reports any violations.

    :param json_path: Path to the ``.json`` configuration file.
    :param mode:
        Validation mode.  ``ConfigMode.AUTO`` (default) reads ``A2BRole``
        from the file to select the schema.  ``ConfigMode.MASTER`` /
        ``ConfigMode.SLAVE`` force a specific schema and also assert that
        ``A2BRole`` matches.
    :returns:
        :class:`ValidationResult` with ``is_valid``, resolved ``mode``, and
        a list of human-readable ``errors`` (empty when valid).
    """
    json_path = Path(json_path)
    errors: list[str] = []

    if not json_path.exists():
        return ValidationResult(
            is_valid=False,
            mode=None,
            errors=[f"File not found: {json_path}"],
        )

    config, load_error = _load_and_parse_json(json_path)
    if load_error is not None:
        return load_error

    resolved_mode = _resolve_config_mode(mode, config, errors)
    if resolved_mode is None:
        return ValidationResult(
            is_valid=False,
            mode=None,
            errors=[
                f"Cannot auto-detect mode: 'A2BRole' is "
                f"{config.get('A2BRole', '<missing>')!r}. "
                "Expected 'Master' or 'Slave'."
            ],
        )

    schema_errors = _validate_against_schema(config, resolved_mode, errors)

    if not schema_errors:
        _run_consistency_checks(config, resolved_mode, errors)

    return ValidationResult(
        is_valid=len(errors) == 0,
        mode=resolved_mode,
        errors=errors,
    )


def _check_matrix_row_count(config: dict, errors: list[str]) -> None:
    """Verify that routing matrix row counts is not larger than the declared USB channel counts."""
    usb_in = config.get("UsbInputChannels")
    usb_out = config.get("UsbOutputChannels")
    downstream = config.get("AudioRouteMatrixDownstream", [])
    upstream = config.get("AudioRouteMatrixUpstream", [])

    if isinstance(usb_in, int) and isinstance(downstream, list):
        if len(downstream) > usb_in:
            errors.append(
                f"'AudioRouteMatrixDownstream' has {len(downstream)} row(s) but "
                f"'UsbInputChannels' is {usb_in} – row count must not be larger than input channel count."
            )

    if isinstance(usb_out, int) and isinstance(upstream, list):
        if len(upstream) > usb_out:
            errors.append(
                f"'AudioRouteMatrixUpstream' has {len(upstream)} row(s) but "
                f"'UsbOutputChannels' is {usb_out} – row count must  not be larger than output channel count."
            )


def _check_master_slave_count(config: dict, errors: list[str]) -> None:
    """Verify that SlavesOnBus matches the number of SlaveConfiguration entries."""
    master_cfg = config.get("A2BMasterConfig", {})
    slaves_on_bus = master_cfg.get("SlavesOnBus")
    slave_config_list = master_cfg.get("SlaveConfiguration", [])

    if isinstance(slaves_on_bus, int) and isinstance(slave_config_list, list):
        if slaves_on_bus != len(slave_config_list):
            errors.append(
                f"'A2BMasterConfig.SlavesOnBus' is {slaves_on_bus} but "
                f"'SlaveConfiguration' has {len(slave_config_list)} entry/entries – "
                "counts must match."
            )


def _check_slave_tdm_channels(config: dict, errors: list[str]) -> None:
    """Verify that TdmRxChannels/TdmTxChannels cover all A2B channels used in the route matrices.

    * Each row in ``AudioRouteMatrixUpstream`` represents one A2B channel received by the
      slave device, so the row count must not exceed ``TdmRxChannels``.
    * Every element value in ``AudioRouteMatrixDownstream`` is an A2B output channel index
      (1-based) transmitted by the slave device, so the highest referenced channel must not
      exceed ``TdmTxChannels``.
    """
    slave_cfg = config.get("A2BSlaveConfig", {})
    tdm_rx = slave_cfg.get("TdmRxChannels")
    tdm_tx = slave_cfg.get("TdmTxChannels")
    upstream = config.get("AudioRouteMatrixUpstream", [])
    downstream = config.get("AudioRouteMatrixDownstream", [])

    if isinstance(tdm_rx, int) and isinstance(upstream, list):
        rx_rows = len(upstream)
        if rx_rows > tdm_rx:
            errors.append(
                f"'AudioRouteMatrixUpstream' has {rx_rows} row(s) but "
                f"'A2BSlaveConfig.TdmRxChannels' is {tdm_rx} – "
                "the slave cannot receive more A2B channels than TdmRxChannels."
            )

    if isinstance(tdm_tx, int) and isinstance(downstream, list):
        all_channels = [
            ch
            for row in downstream
            if isinstance(row, list)
            for ch in row
            if isinstance(ch, int)
        ]
        if all_channels:
            max_ch = max(all_channels)
            if max_ch > tdm_tx:
                errors.append(
                    f"'AudioRouteMatrixDownstream' references A2B channel {max_ch} but "
                    f"'A2BSlaveConfig.TdmTxChannels' is {tdm_tx} – "
                    "all A2B output channel indices must be within TdmTxChannels."
                )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="json_validator",
        description=(
            "Validate an A2Bridge JSON configuration file against the official schema.\n\n"
            "Validation layers:\n"
            "  1. JSON standard compliance  – syntax and UTF-8 encoding\n"
            "  2. Schema validation         – required fields, types, allowed values\n"
            "  3. Cross-field consistency   – routing matrix row counts, slave counts\n\n"
            "Requirements:\n"
            '  Python 3.9+  and  pip install "jsonschema>=4.0"'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes:\n"
            "  0  Config is valid\n"
            "  1  Validation failed (errors printed to stderr)\n"
            "  2  Bad CLI arguments\n\n"
            "Examples:\n"
            "  # Auto-detect role from A2BRole field inside the file\n"
            "  python json_validator.py config.json\n\n"
            "  # Force master schema (also asserts A2BRole == 'Master')\n"
            "  python json_validator.py master.json --mode master\n\n"
            "  # Force slave schema (also asserts A2BRole == 'Slave')\n"
            "  python json_validator.py slave.json --mode slave\n"
        ),
    )
    parser.add_argument(
        "json_path",
        metavar="JSON_FILE",
        help="Path to the A2Bridge JSON configuration file to validate.",
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=[m.value for m in ConfigMode],
        default=ConfigMode.AUTO.value,
        metavar="{master,slave,auto}",
        help=(
            "Validation mode.  'auto' (default) reads A2BRole from the file. "
            "'master' or 'slave' forces a specific schema and asserts A2BRole matches."
        ),
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Entry-point for the CLI.  Returns an exit code (0 = success, 1 = invalid)."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    result = validate_config(args.json_path, mode=args.mode)

    if result.is_valid:
        print(str(result))
        return 0
    print(str(result), file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
