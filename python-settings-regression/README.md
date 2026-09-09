# Python settings regression checks

**The error disappeared. Did the settings values survive?**

This Agent Skill helps a coding agent check Pydantic Settings aliases, dotenv fallbacks and environment-source precedence after a configuration change. Its local demonstration shows why `extra='ignore'` can silence an error while losing intended values.

The skill is a useful diagnostic procedure with an optional public evidence source. It does not modify a project, install dependencies, call a service or submit results on installation. No account, API key or paid API is required by this package.

## Run the optional synthetic example

Inspect `scripts/settings_regression_demo.py` first. In a disposable working directory, create a virtual environment and install the demonstration dependencies:

```text
python -m venv .venv
```

Windows:

```text
.venv\Scripts\python -m pip install -r requirements-demo.txt
.venv\Scripts\python -I -B scripts/settings_regression_demo.py --run
```

macOS/Linux command form:

```text
.venv/bin/python -m pip install -r requirements-demo.txt
.venv/bin/python -I -B scripts/settings_regression_demo.py --run
```

The command forms do not claim the example has been measured on every platform. The script prints its actual runtime and results, and exits nonzero when observed behavior differs from its assertions. Dependency installation downloads packages from the configured package index; the demonstration itself makes no network requests.

The negative controls should reproduce the strict validation error and demonstrate the silent loss of fallback and timeout values. The corrected case must preserve the intended complete configuration, source priority, typed values and rejection behavior. The test harness succeeds when it detects the expected negative controls and validates the corrected case.

## Scope and source

The source case was measured on Windows AMD64 / CPython 3.12.14 with pydantic-settings 2.15.0 and pydantic 2.13.5. Its exact pins are for historical reproduction, not current production upgrade advice. Passing this example is not proof that a user's code or environment works, and a virtual environment is not a security sandbox.

The example covers intentionally accepted prefixes for one nested model. It does not establish behavior for custom settings sources, secret stores, deep aliases, case-sensitive configurations or conflicting aliases in the same source. It is not a benchmark showing that one AI model is better than another.

Source and full recorded evidence: [Execution Evidence Lab — Pydantic Settings alias regression](https://execution-evidence-lab.tuned-drake-1114.chatgpt.site/cases/pydantic-settings-alias). Primary references are linked from that case. This distribution is maintained by Execution Evidence Lab; it is not an official Pydantic package or endorsement.

The local example uses only synthetic inputs. It does not read project `.env` files or send usage telemetry. Optional online evidence reads are ordinary HTTP requests and may be logged by the publisher. Keep real configuration values local.

## Use with an agent

Review `SKILL.md` and make this folder available through the agent client's supported skill installation method. The public distribution uses the Agent Skills discovery manifest and a SHA-256 checked ZIP. With Node.js 22.20.0 or later, install into a project with the official skills CLI:

```text
npx --yes skills@1.5.25 add https://execution-evidence-lab.tuned-drake-1114.chatgpt.site --skill python-settings-regression --agent codex --copy --yes
```

Run the command from the intended project directory; it copies the skill into that project's agent skill directory. Change the agent selection to a supported client when appropriate. The package is also available as [a reviewable ZIP](https://execution-evidence-lab.tuned-drake-1114.chatgpt.site/skills/python-settings-regression.zip) for manual installation. The installer downloads code and skill files; it does not run the bundled Python example.

For installer verification, set `DO_NOT_TRACK=1` and `DISABLE_TELEMETRY=1` before the command. The official CLI supports these flags to suppress its telemetry; the serving host still receives the download requests. A self-test is not an organic installation or customer use.

Ask the agent to use `python-settings-regression` for an appropriate Pydantic Settings task. The skill supports normal task-based selection in compatible clients; publishing or downloading it does not install it into every AI. Search listings, installation, local example execution and reuse are separate events. The [skills CLI](https://github.com/vercel-labs/skills) documents installation; [skills.sh](https://skills.sh/docs/faq) documents its discovery and installation metrics.

Example request:

> After a dotenv change, Pydantic Settings raises extra_forbidden. Setting extra='ignore' removes the error, but I need to preserve the intended fallback and source priority. Use python-settings-regression to propose and run relevant checks in this project. Keep configuration values local.

## License

The authored skill and example are MIT licensed; see `LICENSE`. Third-party Python dependencies retain their own licenses. Optional skill installers have their own telemetry settings; this package's demonstration does not send telemetry.
