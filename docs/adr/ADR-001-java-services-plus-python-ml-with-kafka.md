# ADR-001: Why split into Java services plus a Python ML service, with Kafka between them?

- Status: Accepted
- Date: 2026-11-03

## Context
SentinelPay has two very different jobs. One is accepting, validating and storing payments reliably. The other is scoring each payment for fraud with a machine-learning model. The ML ecosystem (training, feature code, model libraries) lives in Python. Typed, long-running transactional services are a natural fit for Java and Spring Boot.

## Decision
Build the payment-handling services in Java (Spring Boot) and the scoring service in Python (FastAPI) as separate deployables. Connect them with Kafka: Java services publish transactions as events, the ML service consumes them and publishes scores back.

## Trade-offs
- Gain: each side uses the language and libraries it is best at, and they scale and deploy independently.
- Gain: Kafka decouples them. A slow or crashed ML service does not block payment intake, and events can be replayed.
- Cost: two toolchains, two build and test setups, and more to run and monitor.
- Cost: scores arrive asynchronously, so anything needing an instant answer is harder to build.
- Cost: event schemas become a contract between languages and must be versioned carefully, and Kafka is extra infrastructure to operate.
