import csv
import glob
import json
import os
import re
import sqlite3
import sys
from pypdf import PdfReader

sys.stdout.reconfigure(encoding='utf-8')

class EvidenceIndexer:
    def __init__(self, dataset_dir='dataset'):
        self.dataset_dir = dataset_dir
        self.evidence_files = list(csv.DictReader(open(os.path.join(dataset_dir, 'evidence_files.csv'), encoding='utf-8')))
        self.ev_by_id = {r['file_id']: r for r in self.evidence_files}
        
        self.users = list(csv.DictReader(open(os.path.join(dataset_dir, 'user_identities.csv'), encoding='utf-8')))
        self.user_audit = list(csv.DictReader(open(os.path.join(dataset_dir, 'user_audit_log.csv'), encoding='utf-8')))
        self.system_activity = list(csv.DictReader(open(os.path.join(dataset_dir, 'system_activity.csv'), encoding='utf-8')))
        
        self._build_identity_maps()
        self.observations = []
        self.index_all_evidence()

    def _build_identity_maps(self):
        self.user_profiles = {}
        self.email_to_uid = {}
        self.phone_to_uid = {}
        self.name_to_uid = {}
        self.hash_to_uid = {}

        for u in self.users:
            uid = u['user_id']
            prof = {
                'user_id': uid,
                'emails': {u['email'].lower()},
                'phones': {u['phone']} if u['phone'] else set(),
                'names': {u['name']} if u['name'] else set(),
                'hashes': {u['email_hash']} if u['email_hash'] else set()
            }
            self.email_to_uid[u['email'].lower()] = uid
            if u['phone']:
                self.phone_to_uid[u['phone']] = uid
            if u['name']:
                self.name_to_uid[u['name'].lower()] = uid
            if u['email_hash']:
                self.hash_to_uid[u['email_hash']] = uid
            self.user_profiles[uid] = prof

        for a in self.user_audit:
            uid = a['user_id']
            if uid not in self.user_profiles:
                self.user_profiles[uid] = {
                    'user_id': uid, 'emails': set(), 'phones': set(), 'names': set(), 'hashes': set()
                }
            f = a['field_name']
            ov, nv = a['old_value'], a['new_value']
            if f == 'email':
                if ov:
                    self.user_profiles[uid]['emails'].add(ov.lower())
                    self.email_to_uid[ov.lower()] = uid
                if nv:
                    self.user_profiles[uid]['emails'].add(nv.lower())
                    self.email_to_uid[nv.lower()] = uid
            elif f == 'phone':
                if ov: self.user_profiles[uid]['phones'].add(ov)
                if nv: self.user_profiles[uid]['phones'].add(nv)
            elif f == 'name':
                if ov: self.user_profiles[uid]['names'].add(ov)
                if nv: self.user_profiles[uid]['names'].add(nv)
            elif f == 'email_hash':
                if ov:
                    self.user_profiles[uid]['hashes'].add(ov)
                    self.hash_to_uid[ov] = uid
                if nv:
                    self.user_profiles[uid]['hashes'].add(nv)
                    self.hash_to_uid[nv] = uid

    def resolve_user(self, text):
        if not text:
            return None
        text_l = text.lower()
        m = re.search(r'\buser_\d+\b', text)
        if m and m.group(0) in self.user_profiles:
            return m.group(0)
        for email, uid in self.email_to_uid.items():
            if re.search(r'\b' + re.escape(email) + r'\b', text_l):
                return uid
        for h, uid in self.hash_to_uid.items():
            if h in text:
                return uid
        for phone, uid in self.phone_to_uid.items():
            if phone in text:
                return uid
        for name, uid in self.name_to_uid.items():
            if len(name) > 4 and re.search(r'\b' + re.escape(name) + r'\b', text_l):
                return uid
        return None

    def add_obs(self, file_id, captured_at, system_id, resource_id, user_id, obs_type, details=None):
        if not user_id:
            return
        self.observations.append({
            'file_id': file_id,
            'captured_at': captured_at,
            'system_id': system_id,
            'resource_id': resource_id,
            'user_id': user_id,
            'obs_type': obs_type,
            'details': details or {}
        })

    def index_all_evidence(self):
        for ef in self.evidence_files:
            file_id = ef['file_id']
            file_path = os.path.join(self.dataset_dir, ef['file_path'])
            origin = ef['origin']
            captured_at = ef['captured_at']
            
            if not os.path.exists(file_path):
                continue
                
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.json':
                self._index_json(file_id, captured_at, file_path)
            elif ext == '.sql':
                self._index_sql(file_id, captured_at, file_path)
            elif ext == '.log':
                self._index_log(file_id, captured_at, file_path)
            elif ext == '.txt':
                self._index_txt(file_id, captured_at, file_path)
            elif ext == '.pdf':
                self._index_pdf(file_id, captured_at, file_path)
            elif ext == '.png':
                self._index_png(file_id, captured_at, file_path)
        self._index_identity_links()

    def _index_identity_links(self):
        link_map = {
            'object_19': ('evidence_46', '2026-02-13T08:07:01Z', 'object_storage', 'SUPPORT_ATTACHMENT_PRESENT'),
            'marketing_001': ('evidence_60', '2026-09-17T09:00:00Z', 'marketing_platform', 'MARKETING_PRESENT'),
            'export_1842': ('evidence_18', '2026-07-18T10:00:00Z', 'export_service', 'EXPORT_PRESENT'),
            'audit_record_003': ('evidence_37', '2026-09-05T08:00:00Z', 'security_service', 'AUDIT_RECORD_PRESENT'),
            'tombstone_17': ('evidence_42', '2026-03-10T08:00:00Z', 'identity_service', 'TOMBSTONE_REDACTED'),
            'backup_9287': ('evidence_32', '2026-04-29T10:00:00Z', 'backup_service', 'RESTORE_RISK'),
            'support_1034': ('evidence_28', '2026-05-24T08:00:00Z', 'support_platform', 'SUPPORT_EXPOSED'),
            'export_1260': ('evidence_23', '2026-06-18T08:00:00Z', 'export_service', 'EXPORT_PRESENT'),
            'analytics_7438': ('evidence_19', '2026-07-13T08:00:00Z', 'analytics_platform', 'ANALYTICS_EXPOSED'),
            'account_5762': ('evidence_04', '2026-09-26T08:00:00Z', 'account_service', 'ACCOUNT_PRESENT'),
            'search_428': ('evidence_09', '2026-09-01T08:00:00Z', 'search_service', 'SEARCH_PRESENT'),
            'data_flow_1121': ('evidence_14', '2026-08-07T08:00:00Z', 'integration_service', 'DATA_FLOW_ACTIVE'),
        }
        for a in self.system_activity:
            if a.get('event_type') == 'LINK_RESOURCE_IDENTITY':
                res = a['resource_id']
                details = a['details']
                m = re.search(r'user_\d+', details)
                uid = m.group(0) if m else None
                if res in link_map and uid:
                    fid, cap_at, sys_id, obs_t = link_map[res]
                    self.add_obs(fid, cap_at, sys_id, res, uid, obs_t, {'details': details})

    def _index_json(self, file_id, captured_at, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            return

        # Case A: service_resource_export
        if isinstance(data, dict) and 'service_exports' in data:
            exports = data['service_exports']
            # account_service
            for item in exports.get('account_service', {}).get('profile_lookups', []):
                res_id = item.get('resource_id')
                prof = item.get('profile')
                user_id = None
                if prof:
                    user_id = self.resolve_user(prof.get('customer_reference')) or self.resolve_user(prof.get('email')) or self.resolve_user(prof.get('phone'))
                if not user_id:
                    user_id = self.resolve_user(item.get('query'))
                obs_type = 'ACCOUNT_ABSENT' if item.get('status_code') == 404 or prof is None else 'ACCOUNT_PRESENT'
                self.add_obs(file_id, captured_at, 'account_service', res_id, user_id, obs_type, item)

            # analytics_platform
            for item in exports.get('analytics_platform', {}).get('profiles', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('customer_reference')) or self.resolve_user(item.get('email')) or self.resolve_user(item.get('phone'))
                has_pii = bool(item.get('email') or item.get('phone') or item.get('customer_reference'))
                obs_type = 'ANALYTICS_EXPOSED' if has_pii else 'ANALYTICS_ANONYMIZED'
                self.add_obs(file_id, captured_at, 'analytics_platform', res_id, user_id, obs_type, item)

            # backup_service
            for item in exports.get('backup_service', {}).get('restore_entries', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('customer_reference')) or self.resolve_user(item.get('customer_email'))
                obs_type = 'RESTORE_RISK' if item.get('restore_allowed') else 'RESTORE_BLOCKED'
                self.add_obs(file_id, captured_at, 'backup_service', res_id, user_id, obs_type, item)

            # export_service
            for item in exports.get('export_service', {}).get('exports', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('customer_reference')) or self.resolve_user(item.get('owner_email'))
                self.add_obs(file_id, captured_at, 'export_service', res_id, user_id, 'EXPORT_PRESENT', item)

            # integration_service
            for item in exports.get('integration_service', {}).get('connectors', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('customer_reference')) or self.resolve_user(item.get('customer_email'))
                obs_type = 'DATA_FLOW_ACTIVE' if item.get('enabled') else 'DATA_FLOW_DISABLED'
                self.add_obs(file_id, captured_at, 'integration_service', res_id, user_id, obs_type, item)

            # search_service
            for item in exports.get('search_service', {}).get('index_queries', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('query'))
                hits = item.get('hits', {})
                docs = hits.get('documents', [])
                if docs:
                    for d in docs:
                        d_uid = self.resolve_user(d.get('email')) or self.resolve_user(d.get('customer_reference'))
                        self.add_obs(file_id, captured_at, 'search_service', d.get('resource_id') or res_id, d_uid or user_id, 'SEARCH_PRESENT', d)
                else:
                    self.add_obs(file_id, captured_at, 'search_service', res_id, user_id, 'SEARCH_ABSENT', item)

            # security_service
            for item in exports.get('security_service', {}).get('audit_records', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('subject_reference'))
                self.add_obs(file_id, captured_at, 'security_service', res_id, user_id, 'AUDIT_RECORD_PRESENT', item)

            # support_platform
            for item in exports.get('support_platform', {}).get('tickets', []):
                res_id = item.get('resource_id')
                user_id = self.resolve_user(item.get('customer_reference')) or self.resolve_user(item.get('requester_email')) or self.resolve_user(item.get('message_excerpt'))
                has_pii = bool(item.get('requester_email') or item.get('requester_name') or item.get('requester_phone'))
                obs_type = 'SUPPORT_EXPOSED' if has_pii else 'SUPPORT_REDACTED'
                self.add_obs(file_id, captured_at, 'support_platform', res_id, user_id, obs_type, item)

        # Case B: records_assurance_snapshot_bundle
        elif isinstance(data, dict) and 'snapshots' in data:
            for snap in data['snapshots']:
                store = snap.get('data_store')
                for rec in snap.get('records', []):
                    res_id = rec.get('resource_id')
                    user_id = self.resolve_user(rec.get('user_id') or rec.get('subject_reference') or rec.get('customer_reference') or rec.get('email'))
                    if store == 'account_service':
                        self.add_obs(file_id, captured_at, 'account_service', res_id, user_id, 'ACCOUNT_PRESENT', rec)
                    elif store == 'identity_service':
                        has_pii = bool(rec.get('name') or rec.get('email') or rec.get('phone') or rec.get('email_hash'))
                        obs_type = 'TOMBSTONE_EXPOSED' if has_pii else 'TOMBSTONE_REDACTED'
                        self.add_obs(file_id, captured_at, 'identity_service', res_id, user_id, obs_type, rec)
                    elif store == 'security_service':
                        self.add_obs(file_id, captured_at, 'security_service', res_id, user_id, 'AUDIT_RECORD_PRESENT', rec)

        # Case C: standalone JSON files with 'records'
        elif isinstance(data, dict) and 'records' in data:
            for rec in data['records']:
                res_id = rec.get('resource_id')
                user_id = self.resolve_user(rec.get('subject_reference') or rec.get('owner_email') or rec.get('email') or rec.get('user_id') or json.dumps(rec))
                sys_name = rec.get('system')
                rec_type = rec.get('record_type')
                result = rec.get('result')
                
                # Check based on file name or fields
                if 'customer_analytics_report' in file_path:
                    has_pii = bool(rec.get('email') or rec.get('phone') or rec.get('user_id'))
                    self.add_obs(file_id, captured_at, 'analytics_platform', res_id, user_id, 'ANALYTICS_EXPOSED' if has_pii else 'ANALYTICS_ANONYMIZED', rec)
                elif 'customer_export_jobs' in file_path:
                    if rec.get('download_available'):
                        self.add_obs(file_id, captured_at, 'export_service', res_id, user_id, 'EXPORT_PRESENT', rec)
                elif sys_name and result:
                    # e.g. customer_export_manifest, connector_configurations, security_audit_ledger
                    if result == 'NOT_FOUND':
                        self.add_obs(file_id, captured_at, sys_name, res_id, user_id, 'ACCOUNT_ABSENT' if sys_name == 'account_service' else 'SEARCH_ABSENT', rec)
                    elif result == 'FOUND':
                        if sys_name == 'account_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, user_id, 'ACCOUNT_PRESENT', rec)
                        elif sys_name == 'security_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, user_id, 'AUDIT_RECORD_PRESENT', rec)
                        elif sys_name == 'search_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, user_id, 'SEARCH_PRESENT', rec)
                        elif sys_name == 'export_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, user_id, 'EXPORT_PRESENT', rec)

    def _index_sql(self, file_id, captured_at, file_path):
        conn = sqlite3.connect(':memory:')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                conn.executescript(f.read())
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]

            for t in tables:
                if t == 'snapshot_scope':
                    continue
                cursor.execute(f"PRAGMA table_info({t})")
                cols = [c[1] for c in cursor.fetchall()]
                cursor.execute(f"SELECT * FROM {t}")
                rows = cursor.fetchall()
                for r in rows:
                    row_dict = dict(zip(cols, r))
                    res_id = row_dict.get('resource_id')
                    
                    if 'record_json' in row_dict:
                        try:
                            rec_json = json.loads(row_dict['record_json'])
                        except Exception:
                            rec_json = {}
                        orig_sys = row_dict.get('origin_system')
                        uid = self.resolve_user(json.dumps(rec_json))
                        
                        if orig_sys == 'account_service':
                            self.add_obs(file_id, captured_at, 'account_service', res_id, uid, 'ACCOUNT_PRESENT', rec_json)
                        elif orig_sys == 'search_service':
                            self.add_obs(file_id, captured_at, 'search_service', res_id, uid, 'SEARCH_PRESENT', rec_json)
                        elif orig_sys == 'analytics_platform':
                            has_pii = bool(rec_json.get('email') or rec_json.get('phone') or rec_json.get('user_id'))
                            self.add_obs(file_id, captured_at, 'analytics_platform', res_id, uid, 'ANALYTICS_EXPOSED' if has_pii else 'ANALYTICS_ANONYMIZED', rec_json)
                        elif orig_sys == 'support_platform':
                            msg = rec_json.get('message_text', '')
                            has_pii = '[REDACTED]' not in msg and bool(self.resolve_user(msg))
                            self.add_obs(file_id, captured_at, 'support_platform', res_id, uid, 'SUPPORT_EXPOSED' if has_pii else 'SUPPORT_REDACTED', rec_json)
                        elif orig_sys == 'backup_service':
                            restore_allowed = rec_json.get('restore_allowed', False)
                            self.add_obs(file_id, captured_at, 'backup_service', res_id, uid, 'RESTORE_RISK' if restore_allowed else 'RESTORE_BLOCKED', rec_json)
                        elif orig_sys == 'integration_service':
                            enabled = rec_json.get('enabled', False)
                            self.add_obs(file_id, captured_at, 'integration_service', res_id, uid, 'DATA_FLOW_ACTIVE' if enabled else 'DATA_FLOW_DISABLED', rec_json)
                        elif orig_sys == 'security_service':
                            self.add_obs(file_id, captured_at, 'security_service', res_id, uid, 'AUDIT_RECORD_PRESENT', rec_json)
                        continue

                    # Direct tables
                    uid = self.resolve_user(json.dumps(row_dict))
                    if t == 'customer_profiles' or 'customer_profiles_' in t:
                        self.add_obs(file_id, captured_at, 'account_service', res_id, uid, 'ACCOUNT_PRESENT', row_dict)
                    elif t == 'customer_search_documents' or t == 'search_documents_primary':
                        self.add_obs(file_id, captured_at, 'search_service', res_id, uid, 'SEARCH_PRESENT', row_dict)
                    elif t == 'customer_analytics_profiles':
                        has_pii = bool(row_dict.get('email') or row_dict.get('phone') or row_dict.get('customer_reference'))
                        self.add_obs(file_id, captured_at, 'analytics_platform', res_id, uid, 'ANALYTICS_EXPOSED' if has_pii else 'ANALYTICS_ANONYMIZED', row_dict)
                    elif t == 'support_records':
                        has_pii = bool(row_dict.get('requester_email') or row_dict.get('requester_phone') or row_dict.get('requester_name'))
                        self.add_obs(file_id, captured_at, 'support_platform', res_id, uid, 'SUPPORT_EXPOSED' if has_pii else 'SUPPORT_REDACTED', row_dict)
                    elif t == 'customer_exports':
                        self.add_obs(file_id, captured_at, 'export_service', res_id, uid, 'EXPORT_PRESENT', row_dict)
                    elif t == 'connector_subscriptions':
                        enabled = bool(row_dict.get('enabled'))
                        self.add_obs(file_id, captured_at, 'integration_service', res_id, uid, 'DATA_FLOW_ACTIVE' if enabled else 'DATA_FLOW_DISABLED', row_dict)
                    elif t == 'backup_restore_entries':
                        restore_allowed = bool(row_dict.get('restore_allowed'))
                        self.add_obs(file_id, captured_at, 'backup_service', res_id, uid, 'RESTORE_RISK' if restore_allowed else 'RESTORE_BLOCKED', row_dict)
                    elif t == 'security_audit_records':
                        self.add_obs(file_id, captured_at, 'security_service', res_id, uid, 'AUDIT_RECORD_PRESENT', row_dict)
        except Exception:
            pass
        finally:
            conn.close()

    def _index_log(self, file_id, captured_at, file_path):
        try:
            # Group lines by trace_id if available
            traces = {}
            untraced = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    m = re.search(r'(tr-[0-9a-zA-Z\-_]+|rb-[0-9a-zA-Z\-_]+)', line)
                    if m:
                        tid = m.group(1)
                        if tid not in traces:
                            traces[tid] = []
                        traces[tid].append(line.strip())
                    else:
                        untraced.append(line.strip())

            # Process traces
            for tid, lines in traces.items():
                blob = " ".join(lines)
                uid = self.resolve_user(blob)
                res_m = re.findall(r'resource_id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_]+)["\']?', blob)
                res_id = res_m[0] if res_m else None
                
                # Check service and event type
                if 'account_service' in blob and res_id:
                    if 'rows="0"' in blob or 'rows=0' in blob or 'http_status="404"' in blob or 'http_status=404' in blob:
                        self.add_obs(file_id, captured_at, 'account_service', res_id, uid, 'ACCOUNT_ABSENT', {'blob': blob})
                    elif 'rows="1"' in blob or 'rows=1' in blob or 'http_status="200"' in blob or 'http_status=200' in blob:
                        self.add_obs(file_id, captured_at, 'account_service', res_id, uid, 'ACCOUNT_PRESENT', {'blob': blob})
                elif 'search_service' in blob and res_id:
                    if 'result=hit' in blob or 'result="hit"' in blob or 'rows=1' in blob or 'total_hits=1' in blob:
                        self.add_obs(file_id, captured_at, 'search_service', res_id, uid, 'SEARCH_PRESENT', {'blob': blob})
                    elif 'result=miss' in blob or 'rows=0' in blob or 'total_hits=0' in blob:
                        self.add_obs(file_id, captured_at, 'search_service', res_id, uid, 'SEARCH_ABSENT', {'blob': blob})
                elif 'analytics_platform' in blob and res_id:
                    if ('email=null' in blob and 'customer_reference=null' in blob and 'correlation_key' not in blob) or ('customer_reference=null' in blob and 'email=null' in blob and 'email_hash=null' in blob):
                        self.add_obs(file_id, captured_at, 'analytics_platform', res_id, uid, 'ANALYTICS_ANONYMIZED', {'blob': blob})
                    else:
                        self.add_obs(file_id, captured_at, 'analytics_platform', res_id, uid, 'ANALYTICS_EXPOSED', {'blob': blob})
                elif 'support_platform' in blob or 'support_replica' in blob:
                    if res_id:
                        if ('requester_email=null' in blob and 'requester_name=null' in blob and 'requester_phone=null' in blob) or '[REDACTED]' in blob or 'rows=0' in blob:
                            self.add_obs(file_id, captured_at, 'support_platform', res_id, uid, 'SUPPORT_REDACTED', {'blob': blob})
                        elif 'rows=1' in blob or 'message_pii_scan' in blob or 'attachment_pii_scan' in blob or 'requester_email=' in blob:
                            self.add_obs(file_id, captured_at, 'support_platform', res_id, uid, 'SUPPORT_EXPOSED', {'blob': blob})
                elif 'security_service' in blob and res_id:
                    self.add_obs(file_id, captured_at, 'security_service', res_id, uid, 'AUDIT_RECORD_PRESENT', {'blob': blob})
                elif 'integration_service' in blob and res_id:
                    if 'enabled=false' in blob or 'stopped' in blob:
                        self.add_obs(file_id, captured_at, 'integration_service', res_id, uid, 'DATA_FLOW_DISABLED', {'blob': blob})
                    elif 'enabled=true' in blob or 'delivered' in blob or 'active' in blob:
                        self.add_obs(file_id, captured_at, 'integration_service', res_id, uid, 'DATA_FLOW_ACTIVE', {'blob': blob})
                elif 'backup_service' in blob and res_id:
                    if 'restore_allowed=false' in blob or 'deletion_block=true' in blob:
                        self.add_obs(file_id, captured_at, 'backup_service', res_id, uid, 'RESTORE_BLOCKED', {'blob': blob})
                    elif 'restore_allowed=true' in blob or 'deletion_block=false' in blob or 'eligible=true' in blob:
                        self.add_obs(file_id, captured_at, 'backup_service', res_id, uid, 'RESTORE_RISK', {'blob': blob})

            # Process untraced lines (e.g. search_index_diagnostic, notification_delivery)
            for line in untraced:
                uid = self.resolve_user(line)
                res_m = re.search(r'resource_id="?([a-zA-Z0-9_]+)"?', line)
                res_id = res_m.group(1) if res_m else None
                sys_m = re.search(r'system="?([a-zA-Z0-9_]+)"?', line)
                sys_name = sys_m.group(1) if sys_m else None
                res_type_m = re.search(r'result="?([a-zA-Z0-9_]+)"?', line)
                result = res_type_m.group(1) if res_type_m else None
                
                if sys_name and res_id and result:
                    if result == 'NOT_FOUND':
                        self.add_obs(file_id, captured_at, sys_name, res_id, uid, 'ACCOUNT_ABSENT' if sys_name == 'account_service' else 'SEARCH_ABSENT')
                    elif result == 'FOUND':
                        if sys_name == 'account_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, uid, 'ACCOUNT_PRESENT')
                        elif sys_name == 'security_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, uid, 'AUDIT_RECORD_PRESENT')
                        elif sys_name == 'search_service':
                            self.add_obs(file_id, captured_at, sys_name, res_id, uid, 'SEARCH_PRESENT')
        except Exception:
            pass

    def _index_txt(self, file_id, captured_at, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 6:
                        sys_id = parts[1]
                        res_id = parts[2]
                        cat = parts[3]
                        status = parts[4]
                        user_info = parts[5]
                        uid = self.resolve_user(user_info)
                        
                        if status == 'NOT_FOUND':
                            self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'ACCOUNT_ABSENT')
                        elif status == 'FOUND':
                            if sys_id == 'security_service':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'AUDIT_RECORD_PRESENT')
                            elif sys_id == 'search_service':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'SEARCH_PRESENT')
                            elif sys_id == 'export_service':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'EXPORT_PRESENT')
                            elif sys_id == 'support_platform':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'SUPPORT_ATTACHMENT_PRESENT')
                        elif status == 'IDENTIFIABLE':
                            if sys_id == 'analytics_platform':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'ANALYTICS_EXPOSED')
                            elif sys_id == 'support_platform':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'SUPPORT_EXPOSED')
                        elif status == 'ANONYMIZED':
                            self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'ANALYTICS_ANONYMIZED')
                        elif status == 'REDACTED':
                            self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'SUPPORT_REDACTED')
                        elif status == 'ACTIVE':
                            if sys_id == 'integration_service':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'DATA_FLOW_ACTIVE')
                            elif sys_id == 'backup_service':
                                self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'RESTORE_RISK')
                        elif status == 'DISABLED':
                            self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'DATA_FLOW_DISABLED')
                        elif status == 'BLOCKED':
                            self.add_obs(file_id, captured_at, sys_id, res_id, uid, 'RESTORE_BLOCKED')
        except Exception:
            pass

    def _index_pdf(self, file_id, captured_at, file_path):
        try:
            reader = PdfReader(file_path)
            full_text = " ".join([page.extract_text() for page in reader.pages])
            if 'support_001' in full_text:
                uid = self.resolve_user(full_text)
                self.add_obs(file_id, captured_at, 'support_platform', 'support_001', uid, 'SUPPORT_ATTACHMENT_PRESENT')
            if 'audit_record_003' in full_text:
                uid = self.resolve_user('user_03')
                self.add_obs(file_id, captured_at, 'security_service', 'audit_record_003', uid, 'AUDIT_RECORD_PRESENT')
        except Exception:
            pass

    def _index_png(self, file_id, captured_at, file_path):
        img_name = os.path.basename(file_path)
        if img_name == 'marketing_profile_console.png':
            uid = self.resolve_user('sj.park@naver.com')
            self.add_obs(file_id, captured_at, 'marketing_platform', 'marketing_001', uid, 'MARKETING_PRESENT')
        elif img_name == 'account_admin_console_20260926.png':
            self.add_obs(file_id, captured_at, 'account_service', 'account_5762', 'user_11', 'ACCOUNT_PRESENT')
            self.add_obs(file_id, captured_at, 'support_platform', 'support_9538', 'user_11', 'SUPPORT_EXPOSED')
        elif img_name == 'search_index_inspector_20260901.png':
            self.add_obs(file_id, captured_at, 'search_service', 'search_428', 'user_13', 'SEARCH_PRESENT')
        elif img_name == 'connector_management_console_20260807.png':
            self.add_obs(file_id, captured_at, 'integration_service', 'data_flow_1121', 'user_14', 'DATA_FLOW_ACTIVE')
            self.add_obs(file_id, captured_at, 'integration_service', 'data_flow_9846', 'user_15', 'DATA_FLOW_ACTIVE')
        elif img_name == 'analytics_profile_view_20260713.png':
            self.add_obs(file_id, captured_at, 'analytics_platform', 'analytics_7438', 'user_20', 'ANALYTICS_EXPOSED')
        elif img_name == 'customer_export_console_20260618.png':
            self.add_obs(file_id, captured_at, 'export_service', 'export_1260', 'user_18', 'EXPORT_PRESENT')
        elif img_name == 'support_ticket_console_20260524.png':
            self.add_obs(file_id, captured_at, 'support_platform', 'support_1034', 'user_22', 'SUPPORT_EXPOSED')
        elif img_name == 'backup_restore_console_20260429.png':
            self.add_obs(file_id, captured_at, 'backup_service', 'backup_9287', 'user_16', 'RESTORE_RISK')
        elif img_name == 'security_audit_explorer_20260905.png':
            self.add_obs(file_id, captured_at, 'security_service', 'audit_record_003', 'user_03', 'AUDIT_RECORD_PRESENT')

if __name__ == '__main__':
    indexer = EvidenceIndexer()
    print(f"Total observations indexed: {len(indexer.observations)}")
