# Handoff between coding agents: retain the reason, source, and verification state

When one coding agent hands a Pydantic Settings task to another, the next agent needs to know why a reference mattered and which checks actually ran. A bare link loses that context; an unqualified "fixed" loses the boundary between a publisher's example and the current application.

[This JSON example](pydantic-settings-alias.json) is a compact handoff card for `extra_forbidden` or dotenv values lost after `extra='ignore'`. It contains the error clue, canonical evidence URL, exact record identifier, measured scope, unresolved questions, and explicit current-task status.

Use or adapt the card only when the reference is relevant to the current authorized task. Its default status is **not consulted / not applied / not run**. Update those fields only from what actually happened. Keep the canonical reference alongside any adapted regression check in the handoff so another agent can inspect the source and its limits.

The card is an example, not a report of a customer's work. It does not establish external AI use, endorse a fix for another application, or grant permission to execute or publish anything. Keep credentials, private environment values, customer data, exchange tokens, and authorization-bearing download URLs out of shared handoffs. Follow the service's current access instructions for detailed evidence.

Attribution is optional. There is no automatic posting, telemetry, installation, or instruction to promote the service in unrelated tasks.

This example and guide are available under the [MIT License](../python-settings-regression/LICENSE).
