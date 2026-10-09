PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS library_cards (
    library_card_id TEXT PRIMARY KEY,
    source_object_id TEXT NOT NULL,
    source_object_key TEXT NOT NULL,
    source_record_revision TEXT NOT NULL,
    interface_revision TEXT,
    c_processing_revision TEXT,
    d_processing_revision TEXT,
    received_at TEXT NOT NULL,
    card_json TEXT NOT NULL,
    UNIQUE(source_object_id, source_record_revision)
);

CREATE TABLE IF NOT EXISTS library_card_revisions (
    library_card_revision_id TEXT PRIMARY KEY,
    library_card_id TEXT NOT NULL REFERENCES library_cards(library_card_id),
    revision_number INTEGER NOT NULL,
    interface_revision TEXT,
    c_processing_revision TEXT,
    d_processing_revision TEXT,
    card_json TEXT NOT NULL,
    received_at TEXT NOT NULL,
    UNIQUE(library_card_id, revision_number)
);

CREATE INDEX IF NOT EXISTS idx_library_card_revisions_card
ON library_card_revisions(library_card_id);

CREATE INDEX IF NOT EXISTS idx_library_cards_source_object
ON library_cards(source_object_id);

CREATE TABLE IF NOT EXISTS cataloged_instances (
    cataloged_instance_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'PROVISIONAL',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cataloged_instance_revisions (
    cataloged_instance_revision_id TEXT PRIMARY KEY,
    cataloged_instance_id TEXT NOT NULL,
    revision_number INTEGER NOT NULL,
    revision_status TEXT NOT NULL DEFAULT 'CURRENT',
    state_json TEXT NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(cataloged_instance_id)
        REFERENCES cataloged_instances(cataloged_instance_id),
    UNIQUE(cataloged_instance_id, revision_number)
);

CREATE INDEX IF NOT EXISTS idx_ci_revisions_instance
ON cataloged_instance_revisions(cataloged_instance_id);

CREATE TABLE IF NOT EXISTS cataloged_instance_evidence (
    cataloged_instance_evidence_id TEXT PRIMARY KEY,
    cataloged_instance_id TEXT NOT NULL,
    library_card_id TEXT NOT NULL,
    relationship_status TEXT NOT NULL DEFAULT 'ACTIVE',
    reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(cataloged_instance_id)
        REFERENCES cataloged_instances(cataloged_instance_id),
    FOREIGN KEY(library_card_id)
        REFERENCES library_cards(library_card_id)
);

CREATE INDEX IF NOT EXISTS idx_ci_evidence_instance
ON cataloged_instance_evidence(cataloged_instance_id);

CREATE INDEX IF NOT EXISTS idx_ci_evidence_card
ON cataloged_instance_evidence(library_card_id);

CREATE TABLE IF NOT EXISTS recordings (
    recording_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'PROVISIONAL',
    current_data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS performances (
    performance_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'PROVISIONAL',
    current_data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS works (
    work_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'PROVISIONAL',
    current_data_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS catalog_observations (
    observation_id TEXT PRIMARY KEY,
    library_card_id TEXT,
    library_card_revision_id TEXT REFERENCES library_card_revisions(library_card_revision_id),
    subject_type TEXT NOT NULL,
    subject_id TEXT,
    observed_field TEXT NOT NULL,
    observed_value_json TEXT NOT NULL,
    interpreted_value_json TEXT,
    context_json TEXT,
    evidence_json TEXT,
    observed_at TEXT NOT NULL,
    FOREIGN KEY(library_card_id)
        REFERENCES library_cards(library_card_id)
);

CREATE INDEX IF NOT EXISTS idx_observation_subject
ON catalog_observations(subject_type, subject_id);

CREATE INDEX IF NOT EXISTS idx_observation_card
ON catalog_observations(library_card_id);

CREATE TABLE IF NOT EXISTS catalog_associations (
    association_id TEXT PRIMARY KEY,
    association_type TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    evidence_json TEXT,
    supersedes_association_id TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(supersedes_association_id)
        REFERENCES catalog_associations(association_id)
);

CREATE INDEX IF NOT EXISTS idx_association_subject
ON catalog_associations(subject_type, subject_id, association_type);

CREATE INDEX IF NOT EXISTS idx_association_object
ON catalog_associations(object_type, object_id, association_type);

CREATE INDEX IF NOT EXISTS idx_association_supersedes
ON catalog_associations(supersedes_association_id);

CREATE VIEW IF NOT EXISTS current_cataloged_instance_revisions AS
SELECT r.*
FROM cataloged_instance_revisions r
WHERE r.revision_number = (
    SELECT MAX(r2.revision_number)
    FROM cataloged_instance_revisions r2
    WHERE r2.cataloged_instance_id = r.cataloged_instance_id
);

CREATE VIEW IF NOT EXISTS current_catalog_associations AS
SELECT a.*
FROM catalog_associations a
WHERE NOT EXISTS (
    SELECT 1
    FROM catalog_associations newer
    WHERE newer.supersedes_association_id = a.association_id
);

CREATE VIEW IF NOT EXISTS current_catalog_chain AS
SELECT
    ci.cataloged_instance_id,
    cir.cataloged_instance_revision_id,
    cir.revision_number,
    cir.state_json AS cataloged_instance_state,
    ci_r.object_id AS recording_id,
    r_p.object_id AS performance_id,
    p_w.object_id AS work_id,
    ci_r.status AS recording_association_status,
    r_p.status AS performance_association_status,
    p_w.status AS work_association_status
FROM cataloged_instances ci
LEFT JOIN current_cataloged_instance_revisions cir
    ON cir.cataloged_instance_id = ci.cataloged_instance_id
LEFT JOIN current_catalog_associations ci_r
    ON ci_r.subject_type = 'CATALOGED_INSTANCE'
   AND ci_r.subject_id = ci.cataloged_instance_id
   AND ci_r.association_type = 'CATALOGED_INSTANCE_RECORDING'
LEFT JOIN current_catalog_associations r_p
    ON r_p.subject_type = 'RECORDING'
   AND r_p.subject_id = ci_r.object_id
   AND r_p.association_type = 'RECORDING_PERFORMANCE'
LEFT JOIN current_catalog_associations p_w
    ON p_w.subject_type = 'PERFORMANCE'
   AND p_w.subject_id = r_p.object_id
   AND p_w.association_type = 'PERFORMANCE_WORK';

CREATE TABLE IF NOT EXISTS catalog_schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

INSERT OR IGNORE INTO catalog_schema_metadata(key,value) VALUES
('schema_name','MusicStewardship Catalog'),
('schema_revision','0.1'),
('identity_model',
 'LibraryCard -> CatalogedInstance -> Recording -> Performance -> Work');
