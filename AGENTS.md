# MusicStewardship development instructions

## Collaboration and authority

The project architect makes architectural and subject-matter decisions. Codex
performs implementation, analysis, testing, and documentation under that direction.
ChatGPT and Codex should use repository documents to preserve shared context rather
than relying on conversation memory.

These instructions govern development conduct. They do not replace, approve, or
supersede existing architecture documents. Read the applicable requirements,
designs, interface definitions, implementation, and tests before changing a component.
If sources conflict or a change requires an architectural decision, identify the
conflict and obtain the architect's direction; do not silently resolve it in code.

Start with [project state](01_docs/PROJECT_STATE.md), the
[project charter](PROJECT_CHARTER.md), and the
[design documentation chain](01_docs/DesignDocumentationChain.md).
The state document is an evidence-based summary, not a new architectural authority.
Keep architectural requirements, observed implementation behavior, executed-test
results, and working hypotheses explicitly separate. Passing tests do not approve
an architecture or establish historical identity.

## Preservation and domain boundaries

- Preserve original source evidence and provenance, including source values,
  locators, rule/processing lineage, residual material, and competing interpretations.
- Never discard observations simply because they are incomplete, ambiguous, or
  contradictory. Preserve alternatives for later investigation.
- Respect the existing WORK → PERFORMANCE → RECORDING model. Keep source
  submissions, CatalogedInstances, releases, and owned files distinct from those
  historical/musical identities.
- Preserve CatalogedInstance submission/evidence history and operational revision
  history. Corrections must retain earlier submissions and interpretations.
- Maintain the distinction between CORE, ASSOCIATED, and RESIDUAL ingestion
  information. Keep information class separate from processing outcome,
  disposition, assurance, and provenance. RESIDUAL is not synonymous with failure.
- Preserve the C→D Rev B two-section interface: (1) CORE acceptance/provenance,
  including explicit source identity, and (2) extensible SEMANTIC OBSERVATIONS,
  which may be empty. These sections are not catalog information levels 0–4 or
  a replacement for the orthogonal ingestion classifications. Descriptive values
  and resolved historical identities are not CORE admission requirements. Do not
  reconstruct source_id/source_record by parsing source_object_key.
- Keep evidence discovery, contextual assessment, likely-same grouping, and
  identity reconciliation separate.
- Likely-same TITLE and CONTRIBUTOR_NAME groups are reversible representation
  evidence, not historical Work or Person entities. Grouping must not silently
  create entities, merge CatalogedInstances, or overwrite original representations.
- Do not infer identity solely from matching representations, repeated names or
  titles, normalization agreement, or candidate-set membership.
- Do not invent numerical confidence estimates. Report factual evidence and
  unresolved questions; any new confidence or promotion policy requires the
  architect's decision.
- Do not delete or reorganize source collections.

## Change and verification discipline

- Architecture changes, including refactoring architectural boundaries, require
  explicit approval from the project architect.
- Destructive operations require explicit authorization. Test cleanup must stay
  within authorized disposable temporary storage; it must never target source
  collections or persistent research artifacts.
- Prefer focused changes supported by regression tests appropriate to the behavior
  being changed. Preserve established baselines unless an approved change explicitly
  supersedes them.
- Follow the existing design-documentation chain and sparse traceability standard;
  do not introduce a replacement documentation or decision system.
- Distinguish inspected implementation, tests present, tests actually executed,
  documented intentions, and unresolved concerns in reports and project-state updates.
- Inspect commands and test side effects before execution. For a read-only request,
  do not run workflows that create files, databases, caches, reports, or migrations.
- Keep changes within the authorized scope. Obtain approval before additional work
  when the user has explicitly limited the change set.
- Do not commit changes without explicit authorization.

## Session continuity

At session start, read this file and PROJECT_STATE.md, inspect current Git state,
and consult the architectural sources applicable to the task. Verify recorded
versions and commit references when they affect the work; flag discrepancies.

At meaningful milestones (a completed feature, verified baseline, approved decision,
or significant blocker), update PROJECT_STATE.md within the authorized task scope.
Record the date, completed work, evidence and test results, relevant commit IDs,
unresolved issues, and concrete next steps. Retain dated history and refresh the
current summary so resolved environment issues are not presented as open defects.
Do not update it after every minor command or imply an unapproved decision is final.
If a task forbids documentation edits, report the milestone in conversation and
leave the file unchanged. A state update never authorizes a Git commit.

## Existing architectural anchors

- [Orthogonal ingestion dimensions](01_docs/02_Architecture/Orthogonal_Ingestion_Universe.md)
- [Working E-R baseline and information levels](01_docs/Design/ER_SCHEMA_WORKING_BASELINE.md)
- [C → D interface Rev B](01_docs/05_Ingestion/C_to_D_Interface_RevB.md)
- [D3 likely-same grouping contract](01_docs/04_Catalog/D3_Likely_Same_Grouping.md)
- [Production development approach](01_docs/Design/Production_Forest_Architecture_and_Development_Approach_v0.1.md)
- [Traceability tagging standard](01_docs/TraceabilityTaggingStandard.md)
