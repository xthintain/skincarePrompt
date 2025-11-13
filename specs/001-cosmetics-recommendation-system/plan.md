# Implementation Plan: Cosmetics Analysis and Recommendation System

**Branch**: `001-cosmetics-recommendation-system` | **Date**: 2025-11-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-cosmetics-recommendation-system/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an intelligent cosmetics analysis and recommendation system that provides personalized product recommendations based on user profiles (skin type, concerns, allergies). The system analyzes product ingredients for safety, enables product comparison, visualizes market trends through an analytics dashboard, and manages user profiles. Technical approach employs collaborative and content-based filtering using scikit-learn, with data stored in PostgreSQL warehouse following star schema design, backend APIs via Flask/FastAPI, and React dashboard for visualization using ECharts/Recharts.

## Technical Context

**Language/Version**: Python 3.10+ (backend, ML, ETL), JavaScript/Node.js 18+ (frontend)
**Primary Dependencies**: scikit-learn >= 1.3.0, pandas >= 2.0.0, numpy >= 1.24.0, Flask >= 2.3.0 OR FastAPI >= 0.95.0, React >= 18.2.0, ECharts >= 5.4.0
**Storage**: PostgreSQL >= 13 with SQLAlchemy >= 2.0.0 ORM, star schema data warehouse design
**Testing**: pytest >= 7.3.0 (Python backend/ML), Jest >= 29.5.0 (JavaScript frontend)
**Target Platform**: WSL Ubuntu 20.04, Docker >= 20.10 containers, web browser (Chrome/Firefox/Safari latest)
**Project Type**: web (backend + frontend separation)
**Performance Goals**: <3s recommendation generation, <2s dashboard load for 100K products, 1000 concurrent users
**Constraints**: <200ms p95 API response (excluding ML inference), 100% allergen detection accuracy, 70% recommendation relevance
**Scale/Scope**: Initial 100-1000 users, 10K-100K products, 4 user stories (P1-P3), 20 functional requirements, 6 key entities

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Data-Driven Architecture ✅ COMPLIANT

**Check**: All data flows through: Data Source → ETL (pandas/numpy) → PostgreSQL Warehouse → Business Logic (recommendation engine) → Flask/FastAPI APIs → React Dashboard

- ✅ Data pipeline clearly defined in project architecture (cons.md)
- ✅ ETL using pandas/numpy per constitution requirement
- ✅ Raw vs. processed data separation: source data preserved, transformations documented
- ✅ Data quality validation required (FR-019)

**Status**: PASS - Architecture follows data-driven design with clear lineage

### Principle II: Layered System Design ✅ COMPLIANT

**Check**: Four-layer separation maintained per architecture document

- ✅ **Data Layer**: PostgreSQL warehouse, ETL scripts (pandas), data sources (CSV/JSON)
- ✅ **Business Logic Layer**: Recommendation engines (scikit-learn), feature engineering, model training, ingredient analysis
- ✅ **Application Layer**: Flask/FastAPI REST APIs, scheduling (optional Celery), no direct DB access
- ✅ **Presentation Layer**: React Dashboard with ECharts, API calls only, no business logic

**Status**: PASS - Strict layer separation enforced by web app structure

### Principle III: Academic Rigor (NON-NEGOTIABLE) ⚠️ REQUIRES ATTENTION

**Check**: ML algorithms must cite peer-reviewed papers with validation

- ⚠️ Research phase MUST identify and document papers for:
  - Collaborative filtering algorithms (user-based, item-based)
  - Content-based filtering (TF-IDF, cosine similarity)
  - Hybrid recommendation approaches
  - Clustering algorithms (K-means, DBSCAN)
  - Classification models (Random Forest, SVM)
- ⚠️ Experiments MUST use 5-fold cross-validation
- ⚠️ Metrics MUST include: RMSE, MAE, Precision@K, Recall@K for recommendations; accuracy, precision, recall, F1 for classification

**Status**: CONDITIONAL PASS - Requires research phase to identify papers and validation plan

### Principle IV: Model Reproducibility ✅ COMPLIANT

**Check**: Models must be reproducible with documented parameters

- ✅ Using scikit-learn (constitution-approved)
- ⚠️ MUST set random seeds in all model training code
- ⚠️ MUST document hyperparameters in configuration files
- ⚠️ MUST use joblib/pickle for model persistence with versioning
- ⚠️ Training scripts MUST be CLI-runnable

**Status**: CONDITIONAL PASS - Requirements clear, implementation must enforce

### Principle V: API-First Design ✅ COMPLIANT

**Check**: Business logic exposed via RESTful APIs

- ✅ Flask or FastAPI chosen for REST API
- ⚠️ MUST implement JWT authentication
- ⚠️ MUST version APIs (/api/v1/...)
- ⚠️ MUST generate Swagger/OpenAPI documentation
- ⚠️ MUST implement rate limiting
- ✅ JSON response format standard

**Status**: CONDITIONAL PASS - Framework chosen, specifics in Phase 1 contracts

### Principle VI: Visualization Standards ✅ COMPLIANT

**Check**: Consistent visualization patterns using approved libraries

- ✅ Python: matplotlib, seaborn, plotly for EDA and reports
- ✅ React: ECharts or Recharts (no custom chart implementations)
- ⚠️ MUST define consistent color scheme in Phase 1
- ⚠️ MUST ensure accessibility (colorblind-safe palettes)

**Status**: CONDITIONAL PASS - Libraries approved, design standards in Phase 1

### Technology Stack Compliance ✅ COMPLIANT

**Check**: Using approved stack from constitution

- ✅ pandas >= 2.0.0, numpy >= 1.24.0
- ✅ PostgreSQL >= 13, SQLAlchemy >= 2.0.0
- ✅ scikit-learn >= 1.3.0 (no TensorFlow/PyTorch)
- ✅ Flask >= 2.3.0 OR FastAPI >= 0.95.0
- ✅ React >= 18.2.0, ECharts >= 5.4.0 OR Recharts >= 2.5.0
- ✅ Docker >= 20.10, WSL Ubuntu 20.04
- ✅ pytest >= 7.3.0, Jest >= 29.5.0

**Status**: PASS - All technology choices compliant with approved stack

### Overall Gate Status: ✅ CONDITIONAL PASS

**Conditions to resolve in Phase 0 Research**:
1. Identify and document peer-reviewed papers for all ML algorithms
2. Design 5-fold cross-validation experimental plan
3. Define evaluation metrics collection strategy
4. Document random seed and hyperparameter management approach
5. Design JWT authentication flow
6. Define API versioning and rate limiting strategy
7. Establish color scheme and accessibility standards for visualizations

**Violations requiring justification**: NONE

## Project Structure

### Documentation (this feature)

```text
specs/001-cosmetics-recommendation-system/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   ├── api-spec.yaml    # OpenAPI specification
│   └── README.md        # API documentation
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/              # SQLAlchemy ORM models (User, Product, Ingredient, etc.)
│   ├── services/            # Business logic layer
│   │   ├── recommendation/  # Recommendation engine (collaborative, content-based, hybrid)
│   │   ├── analysis/        # Ingredient analysis, product comparison
│   │   ├── analytics/       # Dashboard data aggregation
│   │   └── etl/             # ETL pipelines (data extraction, transformation, loading)
│   ├── api/                 # Flask/FastAPI REST endpoints
│   │   ├── v1/              # API version 1
│   │   │   ├── recommendations.py
│   │   │   ├── products.py
│   │   │   ├── users.py
│   │   │   ├── analytics.py
│   │   │   └── auth.py
│   │   └── middleware/      # Authentication, rate limiting, CORS
│   ├── utils/               # Helpers, validators, formatters
│   └── config.py            # Configuration management
├── tests/
│   ├── contract/            # API contract tests
│   ├── integration/         # Integration tests (API + DB)
│   └── unit/                # Unit tests (models, services)
├── models/                  # Trained ML model artifacts (.pkl files)
├── data/                    # Data storage (managed by user)
│   ├── raw/                 # Original data sources
│   └── processed/           # Cleaned data
├── notebooks/               # Jupyter notebooks for EDA and experimentation
├── scripts/                 # ETL and model training scripts
├── requirements.txt         # Python dependencies
└── Dockerfile               # Backend container configuration

frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Dashboard/       # Dashboard page components
│   │   │   ├── OverviewPanel.jsx
│   │   │   ├── RecommendationPanel.jsx
│   │   │   ├── AnalyticsPanel.jsx
│   │   │   └── IngredientPanel.jsx
│   │   ├── Products/        # Product browsing and comparison
│   │   │   ├── ProductList.jsx
│   │   │   ├── ProductDetail.jsx
│   │   │   └── ProductComparison.jsx
│   │   ├── Profile/         # User profile management
│   │   │   ├── ProfileForm.jsx
│   │   │   └── PreferencesPanel.jsx
│   │   ├── Shared/          # Reusable components
│   │   │   ├── FilterBar.jsx
│   │   │   ├── Charts/      # Chart wrappers (ECharts/Recharts)
│   │   │   └── Layout.jsx
│   │   └── Auth/            # Authentication components
│   ├── services/            # API client services
│   │   ├── api.js           # Axios configuration
│   │   ├── recommendations.js
│   │   ├── products.js
│   │   ├── users.js
│   │   └── analytics.js
│   ├── utils/               # Helpers, formatters, validators
│   ├── App.jsx              # Root component
│   └── index.jsx            # Entry point
├── tests/
│   └── components/          # Component tests (Jest + React Testing Library)
├── public/                  # Static assets
├── package.json             # Node.js dependencies
└── Dockerfile               # Frontend container configuration (Nginx)

database/
├── migrations/              # Alembic migration scripts
└── seeds/                   # Seed data for testing

docker-compose.yml           # Multi-container orchestration
README.md                    # Project setup and quick start
```

**Structure Decision**: Selected **Option 2: Web application** structure due to clear frontend (React Dashboard) and backend (Flask/FastAPI APIs) separation. This aligns with Constitution Principle II (Layered System Design) and enables independent development and deployment of frontend and backend. The `backend/src/` follows layer architecture: `models/` (Data Layer), `services/` (Business Logic), `api/` (Application Layer). Frontend serves as Presentation Layer with no business logic.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations identified** - All constitution checks pass or have clear resolution paths in research phase. Technology choices and architecture fully compliant with approved stack and principles.

---

## Post-Design Constitution Check (Phase 1 Complete)

**Re-evaluation Date**: 2025-11-12
**Status**: ✅ **ALL GATES PASSED**

### Resolution of Conditional Items

All 7 conditions from initial Constitution Check have been fully resolved in Phase 0 (Research) and Phase 1 (Design):

1. ✅ **Academic Papers Identified**: research.md documents 8 peer-reviewed papers for all ML algorithms (Sarwar 2001, Koren 2009, Pazzani 2007, Burke 2002, Arthur & Vassilvitskii 2007, Ester 1996, Breiman 2001, Dietterich 1998)

2. ✅ **5-Fold Cross-Validation Plan**: research.md Section 3 defines stratified K-fold validation protocol with comprehensive metrics (RMSE, MAE, Precision@K, Recall@K, accuracy, precision, recall, F1-score, ROC-AUC)

3. ✅ **Evaluation Metrics Strategy**: Defined in research.md with implementation code examples using scikit-learn

4. ✅ **Random Seed Management**: research.md Section 4 specifies global random seed (42) in YAML config, joblib model versioning with metadata

5. ✅ **JWT Authentication**: research.md Section 5 + contracts/api-spec.yaml define complete JWT flow with access/refresh tokens, bcrypt password hashing, rate limiting

6. ✅ **API Versioning & Rate Limiting**: research.md Section 6 + contracts/api-spec.yaml specify URI versioning (/api/v1/), token bucket rate limiting (100/1000 req/hour tiers), Redis-backed implementation

7. ✅ **Visualization Standards**: research.md Section 7 defines Okabe-Ito colorblind-safe palette, ECharts/Recharts usage, WCAG 2.1 Level AA compliance

### Final Constitution Compliance Summary

| Principle | Status | Evidence |
|-----------|--------|----------|
| **I. Data-Driven Architecture** | ✅ PASS | data-model.md implements star schema with clear data lineage: dim tables (user, product, ingredient, date) + fact tables (interactions, recommendations). ETL defined in quickstart.md. Raw vs processed data separation enforced. |
| **II. Layered System Design** | ✅ PASS | plan.md Project Structure enforces 4-layer separation: Data (models/), Business Logic (services/), Application (api/), Presentation (frontend/components/). No cross-layer violations in design. |
| **III. Academic Rigor** | ✅ PASS | research.md cites 8 peer-reviewed papers with full bibliographic details. 5-fold CV protocol defined. Metrics include RMSE, MAE, Precision@K, F1-score per constitution requirement. |
| **IV. Model Reproducibility** | ✅ PASS | research.md Section 4 + quickstart.md define: YAML config for hyperparameters, random seed=42, joblib versioning with metadata, CLI-runnable training scripts. |
| **V. API-First Design** | ✅ PASS | contracts/api-spec.yaml (OpenAPI 3.0.3) defines 15+ REST endpoints with JWT auth, versioning (/api/v1/), rate limiting, JSON responses, auto-generated docs. |
| **VI. Visualization Standards** | ✅ PASS | research.md Section 7 defines Okabe-Ito palette (colorblind-safe), ECharts primary lib, WCAG 2.1 AA compliance, ARIA labels, keyboard navigation. |
| **Technology Stack** | ✅ PASS | All dependencies match approved stack: Python 3.10+, pandas 2.0+, numpy 1.24+, PostgreSQL 13+, scikit-learn 1.3+, Flask/FastAPI, React 18+, ECharts 5.4+. No violations. |

### Design Artifacts Verification

- ✅ **research.md**: 7 sections resolving all clarifications with academic foundation
- ✅ **data-model.md**: 10 entities, star schema, validation rules, indexes, migrations
- ✅ **contracts/api-spec.yaml**: OpenAPI 3.0.3 with 15+ endpoints mapping to all 20 FRs
- ✅ **contracts/README.md**: API documentation with examples, testing guide, security notes
- ✅ **quickstart.md**: Setup guide with Docker, manual setup, testing, ETL, troubleshooting

### Readiness for Implementation

**Status**: ✅ **READY FOR PHASE 2 (Tasks Generation)**

All design work complete. System architecture, data model, API contracts, and research foundations established. No blocking issues identified.

**Next Command**: `/speckit.tasks` to generate actionable implementation tasks based on this plan and spec.md user stories.
