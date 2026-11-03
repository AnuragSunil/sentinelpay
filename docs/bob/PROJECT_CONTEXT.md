# SentinelPay - Project Context

Stable facts about the project. Rarely changed. Only the owner edits "Tech decisions".
Bob reads this file at the start of every prompt.

## Purpose

- SentinelPay is a fraud detection platform for payment transactions.
- Java Spring Boot microservices ingest transactions and call a Python FastAPI ML service for fraud scores.
- A React frontend lets analysts review scored transactions; Kafka, Redis, PostgreSQL, Docker, Kubernetes and AWS run the platform.

## Repo layout

| Path | Contents |
|------|----------|
| `services/` | Spring Boot microservices (Java) |
| `ml/` | FastAPI ML scoring service (Python) and model code |
| `web/` | React frontend |
| `infra/` | Docker, Kubernetes, and AWS infrastructure definitions |
| `docs/` | Documentation; `docs/bob/` holds Bob's context, log, and archive |

Note: at the time of writing (B-001), only `docs/bob/` exists. The other folders are the intended layout and are not yet created.

## Tech decisions

<!-- Owner adds items here. Bob must not add dependencies, frameworks, or services that are not listed here without stating a reason in BOB_LOG.md and flagging it at the top of the reply. -->

-

## Conventions

- Start of every prompt: read this file and the top 5 entries of `docs/bob/BOB_LOG.md`. Do not read the whole repo unless asked.
- End of every prompt: add ONE new entry at the top of `docs/bob/BOB_LOG.md` in the exact format defined in that file's header.
- Log only what was actually done. If a step failed or was skipped, say so.
- Keep the log to the 10 newest entries. Move older entries by appending to `docs/bob/archive/<YYYY-MM>.md`. Never delete log history.
- Secrets: never write secrets, keys, tokens, or passwords into any file. Use environment variables or placeholders like `<SET_ME>`. Never ask the owner to paste secrets.
- Authorization is enforced in the backend, never by hiding UI.
- Prefer the smallest change that satisfies the prompt. Do not refactor unrelated files.
- Any new dependency, framework, or service not listed under "Tech decisions" requires a stated reason in the log and a flag at the top of the reply.
- End of every reply: list the files changed and say "Log entry B-<n> written."

## Do-not list

- Do NOT write secrets, keys, tokens, or passwords into any file.
- Do NOT ask the owner to paste secrets.
- Do NOT rely on hiding UI elements for authorization.
- Do NOT use `"*"` in IAM policies or CloudFormation without a written reason.
- Do NOT use `localStorage` for tokens in the frontend.
- Do NOT add CDN `<script>` or `<style>` links in the frontend.
- Do NOT add new npm dependencies without owner approval.
- Do NOT add a dependency, framework, or service missing from "Tech decisions" without logging a reason and flagging it.
- Do NOT refactor unrelated files.
- Do NOT delete log history.
- Do NOT read the whole repo unless asked.
