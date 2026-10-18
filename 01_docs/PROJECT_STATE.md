# MusicStewardship project state

**Recorded:** 2026-10-18 (America/New_York)

**Repository:** `C:\Projects\MusicStewardship`

**Current development baseline:** `d36e62f` (application baseline `04b95e5`)

**Status:** Evidence-based development snapshot; not an architecture amendment.

The project architect owns architectural and subject-matter decisions. ChatGPT and
Codex collaborate under that direction. This document indexes existing guidance
and records implementation observations, investigation candidates, and decisions
still needed. It does not supersede any source document or approve proposed work.

Evidence labels used below:

- **Inspected implementation:** behavior visible in source; not proof of runtime correctness.
- **Tests present:** regression code exists; execution status is stated separately.
- **Verified execution:** an actually executed check, with scope, command, and result;
  passing checks do not prove untested behavior or approve architecture.
- **Documented intention:** requirement, design, proposal, or deferred capability.
- **Open investigation / architect decision:** unresolved; not an established defect or approved design.

## 1. Objectives and architectural principles

The [project charter](../PROJECT_CHARTER.md) defines application-independent,
long-term stewardship of recorded music, metadata, provenance, editorial decisions,
relationships, performance assets, observations, and accumulated knowledge. Client
applications consume exported representations rather than owning canonical knowledge.

Existing principles include:

- Represent source evidence faithfully before abstracting or promoting identities.
- Preserve incomplete, ambiguous, residual, and contradictory observations.
- Respect WORK → PERFORMANCE → RECORDING → CATALOGED INSTANCE; distinguish
  historical identity from publication context and owned library artifacts.
- Keep acceptance/provenance, current operational state, structured evidence,
  residual evidence, and revision history distinct (information levels 0–4).
- Keep CORE / ASSOCIATED / RESIDUAL information class orthogonal to processing,
  outcome, assurance, and provenance.
- C preserves/describes what the source supplied; D assesses compatibility,
  grouping, reconciliation, and catalog meaning.
- Matching representations and likely-same groups do not establish historical
  identity. Contributor roles are evidence/relationships, not person identity keys.
- Report evidence separately from promotion policy; do not invent numerical confidence.

### C→D Rev B interface boundary

The established Rev B design has exactly two sections:

1. **CORE acceptance and provenance:** minimum persistent acceptance identity and
   provenance, including explicit source_id/source_record. Do not infer these by
   parsing source_object_key. Title, artist, date, genre, research, and resolved
   musical/historical identities are not admission requirements.
2. **SEMANTIC OBSERVATIONS:** zero or more extensible observations retaining source
   values, interpretations, semantic/role context, and processing provenance.
   Convenience projections do not replace the observations.

These sections are distinct from both catalog information levels 0–4 and the
orthogonal CORE / ASSOCIATED / RESIDUAL ingestion information classes. See
[Rev B sections 3–5](05_Ingestion/C_to_D_Interface_RevB.md).

D3 forms reversible TITLE / CONTRIBUTOR_NAME representation groups. A likely-same
title group is not a Work and a likely-same contributor-name group is not a Person.
Historical entity promotion/reconciliation remains a separate operation; no silent
entity creation or CI coalescence is authorized by grouping. See
[D3 sections 3, 7–8](04_Catalog/D3_Likely_Same_Grouping.md).

Sources: [baseline understanding](Design/BASELINE_UNDERSTANDING.md),
[E-R baseline](Design/ER_SCHEMA_WORKING_BASELINE.md),
[orthogonal ingestion architecture](02_Architecture/Orthogonal_Ingestion_Universe.md),
[C→D Rev B](05_Ingestion/C_to_D_Interface_RevB.md), and
[D3 contract](04_Catalog/D3_Likely_Same_Grouping.md).

## 2. Existing authoritative and reference documents

Authority is contextual and retains each document's declared status. Inclusion here
does not promote a working baseline or proposal to an accepted decision. Conflicts
require architect review rather than an assumed global precedence rule.

| Existing source | Declared role/status and use |
|---|---|
| [Project charter](../PROJECT_CHARTER.md); [principles](01_Foundation/Principles.md) | Mission, preservation, application independence, reproducibility, sandbox/graduation |
| [Design documentation chain](DesignDocumentationChain.md); [traceability standard](TraceabilityTaggingStandard.md) | Project standards: intent → requirements → design → implementation → verification; sparse identifiers |
| [Baseline understanding](Design/BASELINE_UNDERSTANDING.md) | Working baseline, 2026-09-13; representation versus identity and historical prototype evidence |
| [E-R baseline](Design/ER_SCHEMA_WORKING_BASELINE.md) | Working/provisional E-R v0.1, dated 2026-10-02; musical spine, CatalogedInstance, information levels, histories |
| [Orthogonal ingestion universe](02_Architecture/Orthogonal_Ingestion_Universe.md) | Architectural statement defining independent ingestion dimensions |
| [Production forest/development approach](Design/Production_Forest_Architecture_and_Development_Approach_v0.1.md) | Production model and validation-versus-production development guidance |
| [C validation criteria](05_Ingestion/C_Validation_Completion_Criteria_v0.1.md); [C notebook](08_Implementation/C_Development_Notebook_2026-09-27.md) | Working validation checklist and recorded implementation findings/open issues |
| [C→D Rev B](05_Ingestion/C_to_D_Interface_RevB.md) | Production-interface baseline candidate; explicit source identity and extensible semantic observations |
| [Certified interface definitions](../04_src/library_card_interface.py) | Implementation registry verifies exact Rev A/B field definitions and certificates; does not itself settle architectural approval status |
| [Provenance assessment design Rev B](05_Ingestion/MusicStewardship_Provenance_Assessment_Design_RevB.md) | D design including evidence assertions and collection context; stage terminology differs from current D2/D3 tools |
| [D3 likely-same grouping](04_Catalog/D3_Likely_Same_Grouping.md) | Architecture baseline / implementation contract, 2026-10-06; representation grouping distinct from identity promotion |
| [Processing-state/outcome amendment](05_Ingestion/Processing_State_and_Outcome_Architecture_Amendment_v0.1.md) | Explicitly proposed amendment; implementation of vocabulary does not by itself establish approval |
| [Collection maintenance/history](05_Ingestion/Source_Collection_Maintenance_and_Processing_History.md) | Deferred architecture, 2026-10-08; continue existing C/D work without a new change-tracking subsystem now |
| [Audio-derived identity evidence](Architecture/Audio_Derived_Identity_Evidence.md) | Architecture for later independent audio evidence; current D3 does not implement it |

Decision records also exist in two locations: `01_docs/90_Decisions` and
`01_docs/Decisions`. ADR-0003 describes Performance Objects; ADR-0004 describes
container architecture; ADR-0005 explicitly accepts Arc as the recursive
programmatic unit. ADR-0006 (structural markers) is proposed. ADR-0001 and ADR-0002
are empty files in this snapshot. Preserve these records and locations.

Existing development-state sources include the C notebook, the
[current-capabilities baseline](08_Implementation/CurrentCapabilitiesBaseline_2026-08-29.md),
[v0.3 forecast](08_Implementation/Baseline_and_Improvement_Forecast_v0.3.md), and
[development history](91_Notes/MusicStewardship_Development_History_and_Evolution.md).
They describe particular dates/scopes, not automatically current verified capability.
No existing `AGENTS.md` or `PROJECT_STATE.md` was found before creating this pair.
The root README describes an amendment package; ROADMAP.md, CHANGELOG.md, and
04_src/README.md are empty; 08_tools/README.md is a template. None was changed.

## 3. Component implementation status

| Component | Inspected implementation | Limits / verification evidence |
|---|---|---|
| C source discovery/extraction | [source_tree.py](../08_tools/ingestion/source_tree/source_tree.py), [source_ingest.py](../08_tools/text/source_ingest.py), metadata evidence tools | Recursive inventory/classification and ffprobe metadata extraction exist; not a new full-corpus certification |
| C transformation/process state | [rosetta_engine.py](../08_tools/ingestion/rosetta_engine.py) | Generic rule execution, observations/logs, skip restoration, removed-input handling; tests under 07_tests/ingestion and 08_tools/ingestion/tests |
| Reusable ingestion package | [engine](../04_src/ingestion/engine.py), decoders, completeness checker | Small reusable classes; not the complete operational orchestration; field accounting is distinct from set-level completeness |
| C→D exchange | [interface contracts](../04_src/library_card_interface.py), [producer](../08_tools/ingestion/build_library_cards_from_rosetta.py), [importer](../08_tools/import/library_card_import.py) | Certified Rev A/B definitions; Rev B preserves explicit source identity and full semantic observations; interface/import regressions present |
| Catalog acceptance/history | [store](../04_src/catalog/catalog_store.py), [schema](../04_src/catalog/schema_v0_1.sql), [population loader](../08_tools/import/catalog_population_loader.py) | Card revisions, CIs/current states/history, observations, associations; revision/idempotence tests present |
| D1 exact correspondence | [d1_exact_entity_match.py](../08_tools/provenance/d1_exact_entity_match.py) | Narrow one-card proof using exact ordered source_context/source_grouping_label equality; no dedicated main-suite D1 test found |
| D2 existing-entity recognition | [recognition](../08_tools/provenance/d2_entity_candidate_recognition.py), [name harvester](../04_src/d_name_ingestion.py) | Exact name/type candidate lookup preserves ambiguity; separate gateway/observation path from catalog representation analysis |
| D2 representation discovery | [representation analysis](../08_tools/provenance/d2_candidate_representation_analysis.py) | Latest card revisions; two title fields and author/composer expressions; Unicode/accent/case/punctuation comparisons; identical-membership candidate consolidation |
| D3.1/D3.2 classification/pairs | [pair evidence](../08_tools/provenance/d3_pair_evidence.py) | TITLE/CONTRIBUTOR_NAME domains, VARIOUS exclusion, consolidated CI pairs with supporting evidence; explicitly no contextual assessment or transitive grouping |
| D3 v0.3 contextual grouping | [likely-same grouping](../08_tools/provenance/d3_likely_same_grouping.py) | Separate D2-input report path; related title/name evidence, title annotations, unresolved title differences, contributor context; no entities created |
| Explicit reconciliation | [catalog_reconciliation.py](../08_tools/catalog/catalog_reconciliation.py) | Reasoned provisional Recording creation and CI associations with rollback; regression tests present; separate from discovery |

### Verified development environment and regression baseline

- Interpreter: `.venv\Scripts\python.exe`, Python **3.12.5**; pytest **9.1.1**.
  Versions rechecked during Phase 5. Use the explicit interpreter; the shell's
  default Python previously resolved to the global installation.
- pytest.ini preserves `04_src`, adds `08_tools/provenance`, and discovers
  `07_tests` plus `08_tools/ingestion/tests`.
- Phase 2: **13 focused D2/D3 tests passed**; default collection then contained 289 tests.
- Phase 3: **294 tests collected**, and **5 maintained ingestion tests passed**.
- Phase 4 full regression on 2026-10-18: **294 passed in 10.17 seconds; 0 failed,
  0 skipped, 0 errors**. The tested Phase 3 contents were subsequently committed
  as d36e62f; no code changed between that run and its commit.

Executed full-suite command from the repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider
```

The reviewed tests direct generated data into tmp_path, TemporaryDirectory, or
in-memory databases. Repository fixtures are read-only inputs. The documentation
generator uses --check against the persistent specification and writes only to a
temporary copy in its generation test. Earlier sandbox runs encountered temporary
directory permission errors; approved runs outside that sandbox passed. This is an
execution-environment constraint, not evidence of an application regression.

99_sandbox, _from_chat, _to_chat, and retired utilities remain outside default
discovery. Check_TTT_grammar_fixture_regression.py remains outside automated
execution: missing research fixtures and fixed output paths are unresolved.

The earlier assessment's 291 statically counted test definitions were not an
executed/collected count; the verified 294-test baseline above is the current
execution record. Passing this suite does not establish full-source completeness,
resolve the investigation candidates below, or certify production architecture.
No tests were rerun for the documentation-only Phase 5 update.

## 4. Git snapshot

At Phase 5 start: `master` at `d36e62f`, 71 commits ahead of locally recorded
origin/master; no tracked changes, and AGENTS.md plus this document untracked.
No fetch was performed; this does not establish current remote state or backup status.

| Reference | Verified local history |
|---|---|
| `3472de8` | Phase 2: Stabilize pytest imports and isolate D2 test fixtures |
| `d36e62f` | Phase 3: Include maintained ingestion tests in regression suite |
| `547d8e4` | Incorrect reference from the ChatGPT discussion, corrected by the user to `3472de8`. Historical correction only; no unresolved Git-history issue. |

Use `3472de8` for Phase 2; the user has resolved the reference discrepancy.
Earlier application commits include
04b95e5 (D3 classification/pairs), 398101c (D2 current revisions), fd7536b (card
history), and 2396b70 (incremental processing). Refresh snapshots at milestones.
Guidance finalization modifies only these two guidance files. The user explicitly
authorized committing AGENTS.md and this document with the message
`Establish Codex project guidance and development continuity`.

## 5. Correctness concerns requiring investigation

These are source-inspection findings and hypotheses, not reproduced failures.
Investigate against intended behavior before selecting a fix.

| Concern | Evidence and next investigation |
|---|---|
| Legacy observations may disappear from D2 current comparisons | catalog_store.py lines 30–49 adds the revision FK/backfills card revisions but does not attach legacy observations; D2 lines 27–39 and 69–84 inner-join observation revision IDs. Exercise a genuine legacy database fixture. |
| Partial catalog acceptance on failed import | Loader lines 180–181 accepts/commits a card before semantic validation at 223–249; store acceptance commits internally. Test failure/retry and decide required transaction boundary. |
| Corrected submissions versus operational state | Revision-history test lines 8–25 preserves one CI revision across changed submissions. Determine intended evidence-versus-current-state refresh policy before changing behavior. |
| Rule edits can reuse stale processing output | Rosetta lines 273–278 skips on input fingerprint equality without a rule-content/version comparison. Test changed rules/bindings with unchanged input; account for force behavior. |
| D1 missing/missing equality | D1 lines 81–84 defaults both absent fields to empty arrays. Define required match evidence and test direct assessment plus CSV behavior. |
| D3 likely-same status despite unresolved titles | Grouping lines 85–97 assigns cross-instance status from membership/count while retaining unresolved differences. Architect must define whether this is acceptable provisional reporting or needs a gate. |
| Pair roles may include third-instance roles | Pair evidence lines 69–74 copies candidate-set-wide roles to each pair. Test a three-CI candidate set and define role scope. |
| D3 paths are not integrated | Grouping lines 112–114 consumes original D2 files, not classification/pair outputs; latest pair module explicitly ends before contextual assessment. Define the intended pipeline first. |
| Source population/revision provenance is absent from D2 representation output | D2 SQL/projection lines 27–54 and 69–113 carries source_object_key but omits explicit source_id/source_record and revision IDs. Design propagation without parsing composite keys or claiming independence. |

**Resolved environment issues (Phases 2–4):** D3 import paths corrected; fixed D2
sandbox inputs/outputs replaced by temporary deterministic fixtures; import-time
Rosetta script converted to a pytest test preserving its four assertions; maintained
ingestion tests included in discovery. Full regression passed. The standalone
grammar checker and broader dependency-manifest/portability work are not completed
by those changes. Previously observed missing openpyxl concerns the workbook path,
which was not established as covered by this passing default suite.

Additional limits: D2 excludes multi-item values and compound contributor
expressions; D3 cannot assess observations it never receives. The older grouping
path lacks the pair module's explicit identity-flag validation and emits an empty
potentially_conflicting list. Pair expansion is quadratic in participating CI
count; investigate representative large sets before broad deployment.

## 6. Deferred decisions and work

- Source-root rescanning, inventory comparison, additions/removals/relocations,
  and complete historical reconstruction: explicitly deferred by the collection
  maintenance document; it directs continued C/D development without a new tracker now.
- Final production component boundaries and graduation from exploratory machinery:
  subject to C validation findings and architect-directed production design.
- Entity promotion/reconciliation evidence floor, merge/split behavior, independent
  source assessment, and any confidence policy: distinct from D3 grouping.
- Audio fingerprinting/audio-derived identity evidence and common external-reference
  services: documented future capabilities, not prerequisites for current D3 work.
- Run-level history and complete rule/dependency-aware invalidation: forecast work;
  recent incremental fixes address part of this area, not the whole capability.
- Full-source coverage and set-level C certification: require explicit evidence;
  small regression baselines do not prove corpus completeness.

## 7. Proposed development priorities

These are recommendations for architect direction, not authorization to implement.

1. Confirm architectural questions below and a single current D-stage contract.
2. Reproduce catalog migration/import atomicity concerns with focused regression
   fixtures; define operational-state refresh behavior before altering it.
3. Make D3 classification, consolidated pairs, contextual assessment, and grouping
   cooperate under that contract while preserving provenance and ambiguity.
4. Expand D3 validation, role-scope, unresolved-title, determinism, and input-order
   coverage while preserving the now-passing 294-test baseline.
5. Address rule-aware invalidation and run-history gaps within approved process-control design.
6. Improve repository navigation/document status only in separately authorized work;
   avoid broad source-tree reorganization or an unsolicited architecture refactor.

## 8. Open questions for the project architect

1. Which terminology should govern D1/D2/D3? The older provenance Rev B design
   section 18 uses D2 for asset correspondence and D3 for candidate accumulation;
   current tools and the D3 contract use representation discovery and grouping.
2. How should consolidated pair evidence feed contextual assessment and useful
   likely-same groups? Is retaining overlapping candidate groups intentional?
3. Should unresolved relevant title differences gate likely-same status, and what
   evidence establishes a substantive contradiction? No automatic transitive merge
   or numerical confidence policy is proposed here.
4. When a corrected card is accepted, should operational CI state remain unchanged
   pending explicit interpretation, or should an approved projection create a revision?
5. What atomicity/recovery boundary is required for card, CI, and observation import?
6. How should legacy unversioned observations be attributed during migration while
   preserving honest provenance, including where attribution is uncertain?
7. Does the earlier ingestion CORE semantic example remain applicable to a stage
   distinct from Rev B's sparse structural acceptance CORE? Clarify the scope without
   making descriptive completeness a new admission requirement.
8. Which working/proposed documents are approved baselines? In particular, the
   processing-outcome amendment still says proposed, while relevant code exists;
   C→D Rev B says baseline candidate, while the field contracts are certified.
9. The E-R baseline section 13 discusses grouping as an identity hypothesis and
   future ordinal confidence/promotion-floor processing; D3 sections 7–8 establish
   no confidence-grade vocabulary and keeps operational grouping distinct from
   historical entity promotion. Confirm the intended scopes before adding policy.
   These are apparent terminology/policy-scope tensions, not a license to add grades,
   probabilistic scores, automatic promotion, or historical identity assertions to D3.

## 9. Dated development-session log

### 2026-10-18 — Repository assessment and development environment integration

- Architect/user requested a comprehensive read-only assessment, followed by creation
  of persistent development instructions and a project-state snapshot.
- Inspected Git, architecture/decision/development documents, C/D source and tests.
  Read-only syntax parsing occurred in the assessment; tests were not executed.
- Searched for existing AGENTS.md and PROJECT_STATE.md; neither existed. Identified
  existing charter, standards, baselines, notebook/history, and ADRs before authoring.
- Created only AGENTS.md and 01_docs/PROJECT_STATE.md. Preserved all existing documents
  and application code. No installations, migrations, pipeline runs, source changes,
  or Git commits. Verified the change scope and documentation references.
- Architectural conflicts and correctness concerns remain open for investigation
  and architect direction. No architectural decisions were made by this session.

### 2026-10-18 — Phases 2–4: test stabilization and full regression

- Completed temporary-fixture isolation for D2 and corrected provenance imports;
  13 focused tests passed. Committed only the authorized test/configuration files
  as 3472de8, with explicit user authorization.
- Converted the import-time Rosetta checker, preserved its original four assertions,
  and expanded maintained-test discovery. Collection: 294; ingestion subset: 5 passed.
- Reviewed write paths before full execution. Full regression: 294 passed, no failures,
  skips, or errors. Preserved source/research artifacts and guidance documents.
- Committed the authorized Phase 3 pair as d36e62f after the passing baseline.
- Standalone grammar checker remains deferred; broader correctness concerns remain
  investigation candidates, not disproved or resolved by the passing suite.

### 2026-10-18 — Phase 5: project guidance integration

- Compared guidance with the E-R baseline, C→D Rev B, and D3 grouping specification.
  Clarified authority versus status/hypotheses, the two-section interface, grouping
  versus entities, and explicit authorization for architecture/destructive/Git actions.
- Recorded verified versions, completed test-environment work, regression results,
  and local commit history. Initially flagged the supplied 547d8e4 reference;
  the user subsequently confirmed it was a discussion error and corrected it to
  3472de8 (see finalization entry below).
- Preserved architectural documents, application code, and research artifacts;
  changed only AGENTS.md and PROJECT_STATE.md. No tests, migrations, installations,
  or commits in this documentation-only milestone.
- Next: architect reviews apparent document tensions and open D3 policy questions;
  guidance commit and any subsequent implementation require explicit authorization.

### 2026-10-18 — Project guidance finalization

- User confirmed Phase 2 commit 3472de8 and identified 547d8e4 as an incorrect
  reference from the ChatGPT discussion. Removed the Git-reference question from
  open issues; retained this historical correction without implying a history problem.
- Reviewed both guidance documents for consistency and verified local link targets.
  Architectural review questions remain open; no architecture decisions were made.
- User authorized staging and committing only AGENTS.md and PROJECT_STATE.md with
  the specified guidance/continuity commit message. Application code, architectural
  source documents, and research artifacts remain unchanged. No tests were rerun
  for this documentation-only correction; the verified baseline remains 294 passing.
- Next: architect review of the open questions before any architecture-changing work.

## 10. Lightweight session continuity and authorization

At session start, read AGENTS.md and this snapshot, inspect Git state, and consult
the applicable architectural sources. Do not treat a stale status entry as authority.

At meaningful milestones within authorized scope, refresh current status and append
a dated log entry recording completed work, verification scope/results, relevant
commit IDs, unresolved issues/decisions, and next steps. Preserve prior dated entries;
avoid updates after every minor command. If documentation edits are excluded from
the task, report the milestone in conversation without editing this file.

Architectural and subject-matter decisions belong to the project architect.
Architecture changes require explicit architect approval; destructive operations
and Git commits require explicit authorization. Temporary test cleanup is limited
to authorized disposable storage and must never target source/research artifacts.
Milestone documentation does not itself approve implementation or a commit.
