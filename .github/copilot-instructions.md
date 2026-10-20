# FlowGuard rules for Copilot
- spec/ is the source of truth. Read spec/00-scope.md and spec/03-api-contract.md
before changing code.
- Never change field names, scenario names, status codes or the policy table.
If something looks wrong, say so instead of changing it.
- Max 2 attempts. Only SAFE_READ operations auto-retry. Never write an unbounded loop.
- LLM output is a recommendation only; it never authorizes an action.
- No secrets, .env files or credentials in code, prompts, logs or commits.
- Only edit the files the task names. No new features, UI, database servers or agents.
- Run the tests and report the real result. Never claim tests passed if you did not run them.