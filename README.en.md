# SupplyPilot AI

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md)

An AI-powered platform for supply acquisition automation, product rating, and inventory portfolio decisions in global travel e-commerce.

SupplyPilot AI covers the complete workflow—from launching marketing campaigns, decomposing acquisition tasks, submitting and automatically validating products, rating products, and managing inventory pools to identifying supply gaps, warning about supplier risks, and reviewing product-line performance. The project demonstrates how AI agents, explainable scoring models, and event-driven automation can be embedded directly into supply-chain workflows instead of merely adding a chat interface on top of data.

> Current stage: M0 design finalization and the engineering foundation are complete. M1 will focus on demo data and the product shell.

## Core Scenario

Using a “Southeast Asia Summer Travel Festival” as an example, the system can:

1. Convert natural-language campaign requirements into structured acquisition criteria.
2. Identify supply gaps across target markets, hotel categories, and flight routes.
3. Automatically create and distribute acquisition tasks for the Hotel and Flight product lines.
4. Validate supplier submissions for pricing, inventory, and campaign fit.
5. Rate products with product-line-specific models and provide confidence scores and explanations.
6. Monitor inventory-pool health and supplier concentration, triggering supplemental acquisition alerts.
7. Recommend products for listing and storefront ranking.
8. Generate post-campaign reports for product lines and suppliers.

## Product Capabilities

- Campaign and acquisition-task collaboration
- AI-assisted structuring of acquisition requirements
- Bulk product submission and automated validation
- Full-lifecycle inventory-pool management
- Explainable Hotel and Flight rating models
- Product Line Intelligence Agent
- Supply-gap, concentration, and inventory-health analysis
- Event-driven automation rules and alerts
- Cross-campaign product-line and supplier reviews

## MVP Scope

The first phase focuses on the Hotel and Flight product lines and delivers a demonstrable end-to-end workflow:

```text
Create campaign → Break down acquisition tasks → Import products → Validate automatically
                → Rate products → Review manually → Recommend listing
                → Analyze supply → Review campaign
```

The MVP includes campaign management, CSV imports, rule-based validation, two scoring models, an inventory-pool dashboard, supply analysis, agent-powered data Q&A, automated alerts, and reproducible synthetic data.

## Technical Architecture

| Layer | Technology |
|---|---|
| Web | Next.js, TypeScript, and Tailwind CSS; ECharts will be introduced for charting |
| API | FastAPI, Pydantic, SQLAlchemy 2, and Alembic |
| Database | PostgreSQL 16 |
| Background jobs | Redis and Celery |
| Data analysis | SQL and Polars as needed |
| AI | LLM tool calling, controlled analytics tools, and optional RAG |
| Delivery | Docker Compose, automated tests, and GitHub Actions |

Architecture principles: explainable scoring, versioned models and rules, controlled agent operations, confirmation for critical changes, and auditable automated state transitions. See the [system architecture](docs/architecture.md) for the complete decisions.

## Repository Structure

```text
supplypilot-ai/
├── README.md
├── README.en.md
├── README.ja.md
├── CONTRIBUTING.md
├── .gitignore
├── docs/
│   ├── PRD.md
│   ├── architecture.md
│   ├── scoring-model.md
│   ├── agent-design.md
│   ├── data-dictionary.md
│   └── demo-script.md
├── frontend/             # Next.js web app and foundational components
├── backend/              # FastAPI, Celery, SQLAlchemy, and migrations
├── docker-compose.yml
├── Makefile
├── data/
│   └── README.md
└── notebooks/
    └── README.md
```

## Documentation

- [Product requirements](docs/PRD.md)
- [Frontend pages and layout](docs/frontend-design.md)
- [MVP development plan](docs/development-plan.md)
- [System architecture](docs/architecture.md)
- [Product scoring model](docs/scoring-model.md)
- [Agent design](docs/agent-design.md)
- [Data dictionary](docs/data-dictionary.md)
- [Demo script](docs/demo-script.md)
- [Contribution guide](CONTRIBUTING.md)

M0 finalizes the system architecture, data states, scoring models, and agent boundaries. Future milestones will iterate on these contracts.

## Run Locally

Copy the environment variables and start all services:

```bash
cp .env.example .env
docker compose up --build
```

- Web: <http://localhost:3000>
- API health check: <http://localhost:8000/api/v1/health>
- OpenAPI: <http://localhost:8000/api/docs>

Run the local quality gate with `make check`. For the first setup, install the development dependencies described in `backend/README.md` and `frontend/README.md`.

## Milestones

- [x] Define the project positioning and name
- [x] Complete the initial PRD
- [x] Establish the documentation and engineering skeleton
- [x] Complete the information architecture, data model, and system architecture
- [ ] Prepare a reproducible synthetic dataset
- [ ] Implement the core campaign, acquisition-task, and inventory-pool workflow
- [ ] Implement the Hotel and Flight rating engines
- [ ] Implement supply intelligence, automation rules, and the agent
- [ ] Complete testing, containerization, demo video, and project retrospective

## Project Status

SupplyPilot AI has completed M0. The [PRD](docs/PRD.md) is the baseline for product scope; changes to technical and business contracts should be recorded through ADRs, migrations, and corresponding tests.
