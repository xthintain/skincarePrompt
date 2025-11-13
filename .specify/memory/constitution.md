<!--
  ============================================================================
  SYNC IMPACT REPORT
  ============================================================================
  Version Change: 0.0.0 → 1.0.0

  Modified Principles:
  - Initial constitution creation

  Added Sections:
  - I. Data-Driven Architecture
  - II. Layered System Design
  - III. Academic Rigor (NON-NEGOTIABLE)
  - IV. Model Reproducibility
  - V. API-First Design
  - VI. Visualization Standards
  - Technology Stack Requirements
  - Quality Assurance Standards
  - Governance

  Removed Sections: None (initial creation)

  Templates Status:
  - ✅ .specify/templates/plan-template.md (validated - constitution check section compatible)
  - ✅ .specify/templates/spec-template.md (validated - aligns with requirements structure)
  - ✅ .specify/templates/tasks-template.md (validated - supports phased implementation)

  Follow-up TODOs: None
  ============================================================================
-->

# 化妆品分析和推荐系统 Constitution

## Core Principles

### I. Data-Driven Architecture

**PRINCIPLE**: Every component in the system MUST be grounded in data processing, with clear data lineage from source to presentation.

**RULES**:
- All data MUST flow through the defined pipeline: Data Source → ETL → Data Warehouse → Business Logic → Application Layer → Presentation
- Data transformations MUST use pandas/numpy for processing, ensuring consistency and auditability
- Data quality checks MUST be implemented at each pipeline stage
- Raw data MUST be preserved separately from processed data
- Each data transformation MUST be reversible or documented for traceability

**RATIONALE**: The system's core value is deriving insights from data. Without clear data lineage and quality controls, recommendations and analytics become unreliable and impossible to debug or improve.

### II. Layered System Design

**PRINCIPLE**: The system MUST maintain strict separation of concerns across four layers: Data, Business Logic, Application, and Presentation.

**RULES**:
- **Data Layer**: MUST handle only storage (data warehouse), ETL, and data sources. NO business logic.
- **Business Logic Layer**: MUST contain recommendation engines, data analysis modules, feature engineering, and model training. NO direct user interaction or data storage logic.
- **Application Layer**: MUST provide APIs, BI analytics, and scheduling. NO direct database access (use Business Logic Layer).
- **Presentation Layer**: MUST handle only UI/UX via React Dashboard. NO business logic or direct data access.
- Cross-layer communication MUST occur through well-defined interfaces only
- Each layer MUST be independently testable

**RATIONALE**: Layered architecture ensures maintainability, scalability, and allows independent evolution of each layer. It prevents tangled dependencies that make the system brittle and difficult to extend.

### III. Academic Rigor (NON-NEGOTIABLE)

**PRINCIPLE**: All machine learning and data analysis implementations MUST be validated against peer-reviewed academic research with proper citations.

**RULES**:
- Every algorithm implementation (recommendation, clustering, classification) MUST cite at least one relevant peer-reviewed paper
- Model performance claims MUST be supported by experimental validation using standard metrics
- Experiments MUST use cross-validation (minimum 5-fold) for reliability
- Algorithm selection MUST compare at least 3 alternative approaches with documented rationale
- Evaluation MUST include standard metrics: accuracy, precision, recall, F1-score for classification; RMSE, MAE, Precision@K for recommendations
- Results MUST include statistical significance testing where applicable

**RATIONALE**: This is an academic project requiring credibility and reproducibility. Without rigorous validation and proper citations, the work lacks scientific merit and cannot be published or defended.

### IV. Model Reproducibility

**PRINCIPLE**: All machine learning models MUST be reproducible with documented parameters, random seeds, and training procedures.

**RULES**:
- All models MUST use scikit-learn or documented equivalent libraries
- Random seeds MUST be set and documented for all stochastic operations
- Model hyperparameters MUST be recorded (manually or via configuration files)
- Training data splits MUST be consistent and documented
- Model artifacts MUST be persisted using joblib or pickle with versioning
- Model training scripts MUST be runnable from command line with clear documentation

**RATIONALE**: Reproducibility is fundamental to scientific work. Without it, results cannot be verified, models cannot be retrained, and the system becomes a black box that cannot be improved or debugged.

### V. API-First Design

**PRINCIPLE**: All business logic MUST be exposed through RESTful APIs, enabling frontend flexibility and system integration.

**RULES**:
- All endpoints MUST follow REST conventions (GET, POST, PUT, DELETE)
- API MUST return JSON format with consistent error structures
- Authentication/authorization MUST use JWT tokens
- API versioning MUST be implemented (e.g., /api/v1/...)
- Rate limiting and request validation MUST be implemented
- API documentation MUST be auto-generated (Swagger/OpenAPI)

**RATIONALE**: Decoupling frontend from backend through APIs allows independent development, easier testing, and future flexibility (e.g., mobile apps, third-party integrations).

### VI. Visualization Standards

**PRINCIPLE**: All data visualizations MUST serve a clear analytical purpose and follow consistent design patterns.

**RULES**:
- Python visualizations (matplotlib, seaborn, plotly) MUST be used for exploratory analysis and reports
- React Dashboard MUST use established charting libraries (ECharts/Recharts) - NO custom chart implementations without justification
- Color schemes MUST be consistent across all visualizations
- Charts MUST include proper labels, legends, and units
- Interactive features (filters, drill-downs) MUST be documented in component specifications
- Accessibility MUST be considered (colorblind-safe palettes, screen reader support)

**RATIONALE**: Consistency in visualization improves user comprehension and system maintainability. Using established libraries reduces bugs and development time compared to custom implementations.

## Technology Stack Requirements

**PRINCIPLE**: The approved technology stack MUST be used unless a compelling, documented reason justifies deviation.

### Approved Stack

**Data Processing**:
- pandas >= 2.0.0 for data manipulation
- numpy >= 1.24.0 for numerical operations

**Data Storage**:
- PostgreSQL >= 13 (primary recommendation) OR MySQL >= 8.0
- SQLAlchemy >= 2.0.0 for ORM

**Machine Learning**:
- scikit-learn >= 1.3.0 for all ML algorithms (recommendation, clustering, classification)
- NO deep learning frameworks (TensorFlow/PyTorch) unless explicitly approved for future phases

**Backend**:
- Flask >= 2.3.0 OR FastAPI >= 0.95.0 for API services
- Flask-CORS for cross-origin support

**Frontend**:
- React >= 18.2.0 for UI framework
- ECharts >= 5.4.0 OR Recharts >= 2.5.0 for data visualization
- Ant Design >= 5.4.0 OR Material-UI >= 5.11.0 for UI components
- Axios >= 1.3.0 for HTTP requests

**Deployment**:
- Docker >= 20.10 for containerization
- docker-compose for orchestration
- WSL Ubuntu 20.04 as development/deployment environment

**Testing**:
- pytest >= 7.3.0 for Python tests
- Jest >= 29.5.0 for JavaScript tests

**RULES**:
- New dependencies MUST be justified in writing before introduction
- Version constraints MUST be documented in requirements.txt (Python) and package.json (Node.js)
- Security vulnerabilities in dependencies MUST be addressed within 2 weeks of disclosure

**RATIONALE**: Technology standardization reduces complexity, improves team efficiency, and ensures compatibility. The chosen stack is mature, well-documented, and suitable for the project's academic and technical requirements.

## Quality Assurance Standards

### Testing Requirements

**RULES**:
- Unit tests SHOULD be written for critical business logic (recommendation algorithms, data transformations)
- Integration tests MUST be written for API endpoints
- Data quality tests MUST be implemented in ETL pipelines
- Model evaluation tests MUST verify expected performance thresholds
- Tests SHOULD NOT block development but MUST be addressed before final delivery

**RATIONALE**: Testing ensures reliability but should not impede rapid prototyping in academic research. Focus testing efforts on critical paths and user-facing functionality.

### Code Quality

**RULES**:
- Python code MUST follow PEP 8 style guidelines
- JavaScript/React code SHOULD follow ESLint recommended rules
- Functions SHOULD have docstrings describing purpose, parameters, and return values
- Complex algorithms MUST include inline comments explaining logic
- Git commits MUST have descriptive messages following conventional format

**RATIONALE**: Consistent code style improves readability and collaboration, especially important for academic projects that may be shared or published.

### Documentation Requirements

**RULES**:
- API endpoints MUST be documented with request/response examples
- Machine learning models MUST document training procedure, hyperparameters, and performance metrics
- Data schemas MUST be documented in data-model.md or database migrations
- README MUST include setup instructions, dependencies, and quick start guide
- Architecture decisions MUST be documented in cons.md with rationale

**RATIONALE**: Documentation is critical for academic work, enabling reproducibility, knowledge transfer, and proper evaluation of the system.

## Governance

### Constitution Authority

This constitution supersedes all other development practices and decisions. When conflicts arise between convenience and constitutional principles, principles take precedence.

### Amendment Process

1. **Proposal**: Any team member may propose an amendment with written justification
2. **Review**: Amendment MUST be reviewed against project goals and existing principles
3. **Approval**: Amendment MUST be approved by project lead or unanimous team consensus
4. **Documentation**: Amendment MUST update this document with incremented version and date
5. **Propagation**: All dependent templates and documentation MUST be updated to reflect changes

### Version Semantics

- **MAJOR**: Backward-incompatible changes (principle removal, fundamental redefinition)
- **MINOR**: New principles added or substantial guidance expansions
- **PATCH**: Clarifications, wording improvements, non-semantic refinements

### Compliance

**RULES**:
- All code reviews MUST verify compliance with architectural principles (Layers I-II)
- All pull requests introducing ML code MUST include citations (Principle III)
- All API changes MUST follow REST conventions (Principle V)
- Complexity that violates simplicity principles MUST be justified in plan.md Complexity Tracking section
- Constitution violations that cannot be resolved MUST be escalated to project lead

### Review Cadence

- Constitution SHOULD be reviewed at major project milestones (end of each phase in plan.md)
- Constitution MUST be reviewed if recurring patterns violate principles
- Constitution MAY be reviewed at any time if new requirements emerge

**Version**: 1.0.0 | **Ratified**: 2025-11-12 | **Last Amended**: 2025-11-12
