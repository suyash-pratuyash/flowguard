# Phase 0 Sign-off (Gate)
Single approver: the project lead. The team works as one, so there is one sign-off, not three.

Read spec/00-scope.md, spec/03-api-contract.md, spec/04-acceptance-tests.md, then tick:

- [x] Scope and P0-P3 priorities agreed
- [x] API request/response contract agreed
- [x] Max attempts = 2, only SAFE_READ retries
- [x] Terminal states and policy table agreed
- [x] Audit event schema agreed (or edited)
- [x] Acceptance tests and evidence names agreed

Approved by: project lead   Date: 2026-10-20

Phase 0 is DONE when every box is ticked. After that, contract changes need only the project lead's approval,
made as one commit that updates spec/03-api-contract.md and every caller together.
