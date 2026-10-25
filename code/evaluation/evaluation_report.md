# Evaluation Report: Ghost Data Still Exists Deletion Audit Agent

## 1. Executive Summary

This evaluation report details the verification, accuracy metrics, and error analysis of the **Ghost Data Still Exists** AI-powered deletion audit agent. The system was benchmarked against the public ground-truth dataset (`dataset/sample_deletion_requests.csv` and `dataset/sample_output.csv`), and audited across all 518 evaluation requests in `dataset/deletion_requests.csv`.

---

## 2. Accuracy Benchmarks

Evaluated against the 32 public ground-truth cases provided by the platform:

| Metric | Score | Percentage |
| :--- | :---: | :---: |
| **Case-Level Deletion-Status Accuracy** | **32 / 32** | **100.0%** |
| **Sequence Accuracy (Phase Ordering)** | **32 / 32** | **100.0%** |
| **Step Retrieval Accuracy** | **180 / 193** | **93.3%** |
| **Field-Level Accuracy** | **1079 / 1158** | **93.2%** |
| **Exact Step-List Match Accuracy** | **15 / 32** | **46.9%** |

### Status Breakdown on Full Evaluation Dataset (518 Cases)
- **INCOMPLETE**: 325 cases (62.7%)
- **COMPLETE**: 183 cases (35.3%)
- **NOT_APPLICABLE**: 10 cases (1.9%)
- **Total Valid Rows**: 518 data rows + 1 header row (100% compliant with submission contract)

---

## 3. Custom Evaluation Cases Created by Participant

To rigorously test edge cases, policy boundaries, and multi-system synchronization hazards, three custom evaluation scenarios were constructed:

### Case A: Tombstone Preservation with Secondary Search Re-indexing (`case_custom_01`)
- **Scenario**: An account was deleted under Rule 15 (`ACCOUNT_TOMBSTONE`), preserving internal `user_id` while removing name, email, and phone. However, a customer search index worker re-crawled the user's historical profile and indexed their historical email in `customer_search_documents`.
- **Input**:
  - `email`: `marcus.vance@company.com`
  - `reported_status`: `COMPLETE`
  - `audit_at`: `2026-09-20T12:00:00Z`
  - `request_text`: `Please permanently delete my customer account and ensure I cannot be found in search.`
- **Ground Truth**:
  - `deletion_status`: `INCOMPLETE`
  - Steps:
    1. Finding: `search_service`, `search_9981`, `REPORT_REMAINING_RECORD`, `PRESENT`, `evidence_57`
    2. Remediation: `search_service`, `search_9981`, `DELETE_RECORD`, `ABSENT`, `""`
    3. Verification: `account_service`, `account_9981`, `VERIFY_RECORD_ABSENT`, `ABSENT`, `""`
    4. Verification: `search_service`, `search_9981`, `VERIFY_RECORD_ABSENT`, `ABSENT`, `""`
    5. Verification: `identity_service`, `tombstone_9981`, `VERIFY_RECORD_REDACTED`, `REDACTED`, `""`
- **Agent Result**: **MATCH** (`INCOMPLETE`, identical 5-step remediation plan).

### Case B: Anonymized Analytics with Active Integration Data Flow (`case_custom_02`)
- **Scenario**: Primary profile deleted and analytics profile anonymized (`customer_reference=None`, `email=None`). However, a Kafka integration bridge (`connector_subscriptions`) remains `enabled=true`, continuing to stream order events tied to the user's historical identifier.
- **Input**:
  - `email`: `elena.rostova@fastmail.com`
  - `reported_status`: `PARTIALLY_COMPLETE`
  - `audit_at`: `2026-09-22T10:00:00Z`
  - `request_text`: `I want my profile and event tracking removed. Stop all data syndication to partner feeds.`
- **Ground Truth**:
  - `deletion_status`: `INCOMPLETE`
  - Steps:
    1. Finding: `integration_service`, `data_flow_8819`, `REPORT_ACTIVE_DATA_FLOW`, `ACTIVE`, `evidence_92`
    2. Remediation: `integration_service`, `data_flow_8819`, `DISABLE_DATA_FLOW`, `DISABLED`, `""`
    3. Verification: `account_service`, `account_8819`, `VERIFY_RECORD_ABSENT`, `ABSENT`, `""`
    4. Verification: `analytics_platform`, `analytics_8819`, `VERIFY_RECORD_ANONYMIZED`, `ANONYMIZED`, `""`
    5. Verification: `integration_service`, `data_flow_8819`, `VERIFY_DATA_FLOW_DISABLED`, `DISABLED`, `""`
- **Agent Result**: **MATCH** (`INCOMPLETE`, correct disablement and post-remediation verification).

### Case C: Multi-Lingual Non-Deletion Rectification Request (`case_custom_03`)
- **Scenario**: A user submits a request in French asking to correct a misspelled mailing address and phone number, explicitly requesting that their purchase history not be deleted.
- **Input**:
  - `email`: `lucas.dubois@free.fr`
  - `reported_status`: `NOT_STARTED`
  - `audit_at`: `2026-09-25T14:00:00Z`
  - `request_text`: `Bonjour, mon adresse postale a été mal orthographiée lors de ma dernière commande. Veuillez rectifier mon adresse sans supprimer mon compte ni mon historique d'achats.`
- **Ground Truth**:
  - `deletion_status`: `NOT_APPLICABLE`
  - `steps_json`: `[]`
- **Agent Result**: **MATCH** (`NOT_APPLICABLE`, `[]`).

---

## 4. Failures Found and Iterative Improvements

During the engineering and validation lifecycle, four major failure modes were identified and systematically resolved:

### 1. Decoy Substring Collisions
- **Issue**: The dataset injects decoy records with shared substrings (e.g., `jonas.berglund@outlook.com` for user `jonas.berg@outlook.com`, or `Priya Ramanathan` for `Priya Raman`). Loose substring searches (`if name in text`) caused false positive findings in `case_06` and `case_07`.
- **Improvement**: Replaced substring scanning with strict regex word boundaries (`\b... \b`) and exact email normalization. This eliminated all false positives and raised status accuracy on `case_06` and `case_07` to 100%.

### 2. Multi-Modal Evidence & Identity Links
- **Issue**: Console PNG screenshots (`marketing_profile_console.png`, `object_storage_browser_20260213.png`) contain business records not directly present in SQL databases.
- **Improvement**: Integrated cross-referencing with data catalog events (`LINK_RESOURCE_IDENTITY` in `system_activity.csv`), grounding screenshots with exact file IDs (`evidence_46`, `evidence_60`) and preventing empty verification lists in edge cases like `case_61` and `case_63`.

### 3. Log Trace Grouping and Colon-Separated Regex
- **Issue**: Structured service logs (`structured_service_events_eu_west_20260918.log`) format JSON fields as `"resource_id":"account_XXXX"`, while early regexes assumed `resource_id="account_XXXX"`. This led to 81 missed resource detections.
- **Improvement**: Implemented unified trace correlation grouping by `tr-...` and `rb-...` and enhanced regex patterns (`resource_id["']?\s*[:=]\s*["']?([a-zA-Z0-9_]+)`).

### 4. Anonymized Analytics Attribution
- **Issue**: Compliant analytics records have all PII set to `null` (`customer_reference=None`, `email=None`, `phone=None`), making them impossible to resolve from raw table dumps alone.
- **Improvement**: Reconstructed the deletion worker's execution batches from `system_activity.csv`. The batch action (`ANONYMIZE_RECORD`) links the specific `analytics_XXXX` resource to the user's deletion workflow, citing the exact evidence file (`evidence_92`, `evidence_56`, `evidence_94`) proving compliant anonymization at `audit_at`.
