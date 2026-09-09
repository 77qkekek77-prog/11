"""Opt-in, synthetic regression demo: silencing an error can lose settings.

Source: Execution Evidence Lab's public pydantic-settings-alias case and bundle,
read on 2026-09-09. This is a new, smaller demonstration of that public fixture,
not the service's original hashed evidence record or a test of the reader's application.
https://execution-evidence-lab.tuned-drake-1114.chatgpt.site/cases/pydantic-settings-alias
https://execution-evidence-lab.tuned-drake-1114.chatgpt.site/downloads/pydantic-settings-alias/bundle.zip

Review first, then explicitly run:
    python -I -B scripts/settings_regression_demo.py --run

No requests, installation, reporting, project dotenv reads, or user environment
inspection. Importing this file only defines functions. A disposable subprocess
receives no inherited environment; Windows gets an OS-derived SYSTEMROOT only
for interpreter/library bootstrap. Settings see only synthetic LAB_ variables.
Temporary files are created beside this script and removed when the run ends.
"""


def _run_fixture(directory):
    """Worker called by the explicit launcher with a disposable directory."""
    import importlib.metadata
    import json
    import os
    from pathlib import Path
    import platform
    import sys

    pins = {
        "annotated-types": "0.8.0",
        "pydantic": "2.13.5",
        "pydantic-settings": "2.15.0",
        "pydantic-core": "2.46.5",
        "python-dotenv": "1.2.3",
        "typing-inspection": "0.4.4",
        "typing-extensions": "4.16.0",
    }
    versions = {name: importlib.metadata.version(name) for name in pins}
    if sys.platform == "win32":
        # platform.machine() consults PROCESSOR_ARCHITECTURE on this runtime.
        # Obtain OS architecture directly instead of reading host variables.
        import ctypes
        info = ctypes.create_string_buffer(64)
        ctypes.windll.kernel32.GetNativeSystemInfo(info)
        architecture = ctypes.c_ushort.from_buffer(info).value
        machine = {0: "x86", 9: "AMD64", 12: "ARM64"}.get(architecture, f"Windows architecture {architecture}")
    else:
        machine = platform.machine()
    print("Runtime: " + json.dumps({
        "python": platform.python_version(), "implementation": platform.python_implementation(),
        "system": platform.system(), "machine": machine, "packages": versions,
    }, sort_keys=True))
    print("Historical reproduction pins; not current production recommendations.")
    print("Source scope: Windows AMD64, CPython 3.12.14; other runtimes require separate review.")
    checks = []

    def check(name, condition):
        checks.append((name, bool(condition)))
        print(f"{'PASS' if condition else 'FAIL'} {len(checks):02d}: {name}")

    check("historical dependency versions match the public measured fixture", versions == pins)
    if versions != pins:
        print("RESULT: unsupported dependency versions; no settings checks executed.")
        return 2

    # Imports complete with only the explicitly supplied OS bootstrap variable.
    from pydantic import AliasChoices, BaseModel, Field, ValidationError
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class ServiceSettings(BaseModel):
        primary_endpoint: str | None = None
        fallback_endpoint: str | None = None
        timeout_seconds: int = Field(default=30, gt=0)
        retries: int = Field(default=1, ge=0)

    class BrokenSettings(BaseSettings):
        lab_service_settings: ServiceSettings = Field(alias="LAB_SERVICE")
        model_config = SettingsConfigDict(env_nested_delimiter="__", extra="forbid")

    class NaiveSettings(BrokenSettings):
        model_config = SettingsConfigDict(env_nested_delimiter="__", extra="ignore")

    class FixedSettings(BrokenSettings):
        # Both prefixes must be intentional accepted inputs for this same field.
        lab_service_settings: ServiceSettings = Field(
            alias="LAB_SERVICE",
            validation_alias=AliasChoices("LAB_SERVICE", "LAB_SERVICE_SETTINGS"),
        )

    environment = {
        "LAB_SERVICE__PRIMARY_ENDPOINT": "https://env-primary.example.invalid",
        "LAB_SERVICE__RETRIES": "3",
    }
    dotenv = {
        "LAB_SERVICE_SETTINGS__PRIMARY_ENDPOINT": "https://file-primary.example.invalid",
        "LAB_SERVICE_SETTINGS__FALLBACK_ENDPOINT": "https://file-fallback.example.invalid",
        "LAB_SERVICE_SETTINGS__TIMEOUT_SECONDS": "15",
    }
    expected = {
        "primary_endpoint": "https://env-primary.example.invalid",
        "fallback_endpoint": "https://file-fallback.example.invalid",
        "timeout_seconds": 15,
        "retries": 3,
    }

    def evaluate(settings_type, env_values, file_values):
        # Do not copy, inspect, or restore a host environment. This process is disposable.
        os.environ.clear()
        os.environ.update(env_values)
        fixture_path = Path(directory) / "synthetic.env"
        fixture_path.write_text(
            "".join(f"{key}={json.dumps(value)}\n" for key, value in file_values.items()),
            encoding="utf-8",
        )
        try:
            return settings_type(_env_file=fixture_path, _env_file_encoding="utf-8", _secrets_dir=None)
        finally:
            os.environ.clear()

    def error_details(settings_type, env_values, file_values):
        try:
            evaluate(settings_type, env_values, file_values)
        except ValidationError as error:
            return [(item["type"], item["loc"]) for item in error.errors()]
        return []

    rejected = error_details(BrokenSettings, environment, dotenv)
    expected_locations = {(key.lower(),) for key in dotenv}
    check("strict original alias rejects all three mismatched dotenv keys", (
        len(rejected) == 3
        and all(kind == "extra_forbidden" for kind, _ in rejected)
        and {location for _, location in rejected} == expected_locations
    ))
    print("Original error types: " + json.dumps([kind for kind, _ in rejected]))

    naive = evaluate(NaiveSettings, environment, dotenv).lab_service_settings.model_dump()
    lost = {key: {"expected": value, "actual": naive[key]}
            for key, value in expected.items() if naive[key] != value}
    expected_loss = {
        "fallback_endpoint": {"expected": expected["fallback_endpoint"], "actual": None},
        "timeout_seconds": {"expected": 15, "actual": 30},
    }
    print("NEGATIVE CONTROL: extra='ignore' constructs; complete-value contract "
          + ("FAILS (expected)." if lost else "PASSES (unexpected; the reproduction changed)."))
    print("Lost values: " + json.dumps(lost, sort_keys=True))
    check("negative control exposes exactly the expected fallback and timeout loss", lost == expected_loss)

    fixed_model = evaluate(FixedSettings, environment, dotenv)
    fixed = fixed_model.lab_service_settings.model_dump()
    check("explicit AliasChoices constructs with strict extras retained", FixedSettings.model_config["extra"] == "forbid")
    check("environment primary overrides dotenv primary", fixed["primary_endpoint"] == expected["primary_endpoint"])
    check("dotenv fallback survives", fixed["fallback_endpoint"] == expected["fallback_endpoint"])
    check("dotenv timeout survives as integer 15", fixed["timeout_seconds"] == 15 and type(fixed["timeout_seconds"]) is int)
    check("environment retries parse as integer 3", fixed["retries"] == 3 and type(fixed["retries"]) is int)
    check("all resolved values match the intended configuration", fixed == expected)
    check("existing LAB_SERVICE serialization alias remains", fixed_model.model_dump(by_alias=True) == {"LAB_SERVICE": expected})

    file_only = evaluate(FixedSettings, {}, dotenv).lab_service_settings.model_dump()
    check("dotenv-only control supplies the lower-priority primary and fallback", file_only == {
        **expected, "primary_endpoint": "https://file-primary.example.invalid", "retries": 1,
    })
    env_only = evaluate(FixedSettings, environment, {}).lab_service_settings.model_dump()
    check("environment-only control exposes absent fallback and default timeout", env_only == {
        **expected, "fallback_endpoint": None, "timeout_seconds": 30,
    })
    invalid = error_details(FixedSettings, {**environment, "LAB_SERVICE__RETRIES": "not-an-integer"}, dotenv)
    check("invalid integer input is still rejected", any(kind == "int_parsing" for kind, _ in invalid))
    unknown = error_details(FixedSettings, environment, {**dotenv, "LAB_UNEXPECTED": "synthetic-only"})
    check("unknown dotenv key is still rejected", unknown == [("extra_forbidden", ("lab_unexpected",))])

    print("Resolved: " + json.dumps(fixed, sort_keys=True))
    passed = sum(success for _, success in checks)
    print(f"RESULT: {passed}/{len(checks)} checks passed; negative-control behavior "
          + ("matched the expected failure." if lost == expected_loss else "DID NOT match the expected failure."))
    print("This synthetic fixture does not verify a customer's application or production environment.")
    print("Not tested: same-source alias collisions, custom sources, deeper aliases, case-sensitive settings, secret stores.")
    return 0 if passed == len(checks) else 1


def main(argv=None):
    import argparse
    import ctypes
    from pathlib import Path
    import subprocess
    import sys
    import tempfile

    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", action="store_true", help="explicitly run the synthetic regression suite")
    args = parser.parse_args(argv)
    if not args.run:
        parser.print_help()
        return 0

    bootstrap = {}
    if sys.platform == "win32":
        value = ctypes.create_unicode_buffer(32768)
        length = ctypes.windll.kernel32.GetWindowsDirectoryW(value, len(value))
        if not length or length >= len(value):
            print("FAIL: cannot obtain Windows bootstrap directory.", file=sys.stderr)
            return 2
        bootstrap["SYSTEMROOT"] = value.value

    script = Path(__file__).resolve()
    worker = "import runpy,sys; ns=runpy.run_path(sys.argv[1]); raise SystemExit(ns['_run_fixture'](sys.argv[2]))"
    try:
        # An explicit directory avoids tempfile consulting TMP/TEMP or other host values.
        with tempfile.TemporaryDirectory(prefix="settings-demo-", dir=script.parent) as directory:
            result = subprocess.run(
                [sys.executable, "-I", "-B", "-X", "utf8", "-c", worker, str(script), directory],
                cwd=directory, env=bootstrap, capture_output=True, text=True, encoding="utf-8", timeout=30,
            )
            print(result.stdout, end="")
            if result.stderr:
                print(result.stderr, end="", file=sys.stderr)
        print("Cleanup: synthetic temporary directory removed; no external report was sent.")
        return result.returncode
    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"FAIL: {type(error).__name__}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
