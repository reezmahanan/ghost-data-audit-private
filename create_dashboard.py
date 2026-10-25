import json
import csv
import os

def build_dashboard():
    requests = {}
    with open('dataset/deletion_requests.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            requests[row['case_id']] = row

    cases = []
    with open('output.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row['case_id']
            req = requests.get(cid, {})
            steps = json.loads(row['steps_json'])
            cases.append({
                'case_id': cid,
                'status': row['deletion_status'],
                'email': req.get('email', ''),
                'requested_at': req.get('requested_at', ''),
                'reported_status': req.get('reported_status', ''),
                'reported_at': req.get('reported_at', ''),
                'audit_at': req.get('audit_at', ''),
                'request_text': req.get('request_text', ''),
                'step_count': len(steps),
                'steps': steps
            })

    cases_json = json.dumps(cases)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ghost Data Audit Dashboard - HackerRank Orchestrate</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #334155;
            --border: #334155;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --incomplete: #f43f5e;
            --complete: #10b981;
            --na: #f59e0b;
            --finding: #f43f5e;
            --remediation: #38bdf8;
            --verification: #10b981;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.5;
            padding: 24px;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }}
        h1 {{ font-size: 24px; font-weight: 700; color: #fff; }}
        .subtitle {{ color: var(--text-muted); font-size: 14px; margin-top: 4px; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: var(--surface);
            padding: 18px;
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        .stat-val {{ font-size: 28px; font-weight: 700; }}
        .stat-label {{ font-size: 13px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
        
        .controls {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 20px;
            align-items: center;
        }}
        .search-box {{
            flex: 1;
            min-width: 280px;
            padding: 10px 16px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--surface);
            color: #fff;
            font-size: 14px;
        }}
        .search-box:focus {{ outline: none; border-color: var(--primary); }}
        .filter-btn {{
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px 16px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: all 0.2s;
        }}
        .filter-btn.active, .filter-btn:hover {{
            background: var(--surface-hover);
            border-color: var(--primary);
            color: var(--primary);
        }}

        .main-layout {{
            display: grid;
            grid-template-columns: 420px 1fr;
            gap: 20px;
            height: calc(100vh - 280px);
            min-height: 500px;
        }}
        .case-list-pane {{
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }}
        .case-item {{
            padding: 14px 16px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.15s;
        }}
        .case-item:hover {{ background: var(--surface-hover); }}
        .case-item.selected {{
            background: #253349;
            border-left: 4px solid var(--primary);
        }}
        .case-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
        }}
        .case-id {{ font-weight: 600; font-size: 15px; }}
        .case-email {{ font-size: 13px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        
        .badge {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        .badge-incomplete {{ background: rgba(244, 63, 94, 0.2); color: var(--incomplete); border: 1px solid rgba(244, 63, 94, 0.4); }}
        .badge-complete {{ background: rgba(16, 185, 129, 0.2); color: var(--complete); border: 1px solid rgba(16, 185, 129, 0.4); }}
        .badge-na {{ background: rgba(245, 158, 11, 0.2); color: var(--na); border: 1px solid rgba(245, 158, 11, 0.4); }}
        
        .detail-pane {{
            background: var(--surface);
            border-radius: 12px;
            border: 1px solid var(--border);
            overflow-y: auto;
            padding: 24px;
        }}
        .detail-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 20px;
        }}
        .meta-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
            background: #151f30;
            padding: 16px;
            border-radius: 8px;
        }}
        .meta-item label {{ display: block; font-size: 11px; color: var(--text-muted); text-transform: uppercase; }}
        .meta-item value {{ display: block; font-size: 13px; font-weight: 500; margin-top: 2px; }}
        .request-box {{
            background: #151f30;
            border-left: 3px solid var(--primary);
            padding: 14px 16px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 24px;
            color: #e2e8f0;
        }}
        
        .steps-container {{ display: flex; flex-direction: column; gap: 12px; }}
        .step-card {{
            background: #182234;
            border-radius: 8px;
            border: 1px solid var(--border);
            padding: 14px 18px;
            display: flex;
            align-items: center;
            gap: 14px;
        }}
        .step-no {{
            font-size: 13px;
            font-weight: 700;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            background: #253349;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--primary);
        }}
        .step-body {{ flex: 1; }}
        .step-meta {{ display: flex; gap: 8px; align-items: center; margin-bottom: 4px; }}
        .step-op {{ font-weight: 600; font-size: 13px; }}
        .step-res {{ font-size: 12px; color: var(--text-muted); }}
        .step-ev {{
            font-size: 11px;
            background: #253349;
            color: #cbd5e1;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: auto;
        }}
        .phase-finding {{ color: var(--finding); }}
        .phase-remediation {{ color: var(--remediation); }}
        .phase-verification {{ color: var(--verification); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Ghost Data Still Exists — Audit Dashboard</h1>
                <div class="subtitle">HackerRank Orchestrate (October 2026) Deletion-Audit Exploration Tool</div>
            </div>
            <div>
                <span class="badge badge-complete" style="font-size: 12px; padding: 6px 12px;">Output: 518 Validated Cases</span>
            </div>
        </header>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-val" id="total-count">518</div>
                <div class="stat-label">Total Evaluated Cases</div>
            </div>
            <div class="stat-card">
                <div class="stat-val" style="color: var(--incomplete);" id="incomplete-count">325</div>
                <div class="stat-label">Incomplete (Remediation Needed)</div>
            </div>
            <div class="stat-card">
                <div class="stat-val" style="color: var(--complete);" id="complete-count">183</div>
                <div class="stat-label">Complete (Evidence-Backed)</div>
            </div>
            <div class="stat-card">
                <div class="stat-val" style="color: var(--na);" id="na-count">10</div>
                <div class="stat-label">Not Applicable (Non-Deletion)</div>
            </div>
        </div>

        <div class="controls">
            <input type="text" id="search-input" class="search-box" placeholder="Search by Case ID, email, or system...">
            <button class="filter-btn active" data-filter="ALL">All (518)</button>
            <button class="filter-btn" data-filter="INCOMPLETE">Incomplete (325)</button>
            <button class="filter-btn" data-filter="COMPLETE">Complete (183)</button>
            <button class="filter-btn" data-filter="NOT_APPLICABLE">Not Applicable (10)</button>
        </div>

        <div class="main-layout">
            <div class="case-list-pane" id="case-list">
                <!-- Case rows will be injected here -->
            </div>
            <div class="detail-pane" id="detail-pane">
                <div style="color: var(--text-muted); text-align: center; margin-top: 100px;">Select a case on the left to view details and ordered steps.</div>
            </div>
        </div>
    </div>

    <script>
        const CASES = {cases_json};

        let currentFilter = 'ALL';
        let searchQuery = '';
        let selectedCaseId = CASES[0].case_id;

        function renderCaseList() {{
            const listEl = document.getElementById('case-list');
            listEl.innerHTML = '';

            const filtered = CASES.filter(c => {{
                if (currentFilter !== 'ALL' && c.status !== currentFilter) return false;
                if (searchQuery) {{
                    const q = searchQuery.toLowerCase();
                    return c.case_id.toLowerCase().includes(q) || 
                           c.email.toLowerCase().includes(q) || 
                           c.steps.some(s => s.system_id.toLowerCase().includes(q) || s.resource_id.toLowerCase().includes(q));
                }}
                return true;
            }});

            if (filtered.length === 0) {{
                listEl.innerHTML = '<div style="padding: 24px; color: var(--text-muted); text-align: center;">No cases match filters.</div>';
                return;
            }}

            filtered.forEach(c => {{
                const item = document.createElement('div');
                item.className = 'case-item' + (c.case_id === selectedCaseId ? ' selected' : '');
                const badgeClass = c.status === 'COMPLETE' ? 'badge-complete' : (c.status === 'INCOMPLETE' ? 'badge-incomplete' : 'badge-na');
                item.innerHTML = `
                    <div class="case-header">
                        <span class="case-id">${{c.case_id}}</span>
                        <span class="badge ${{badgeClass}}">${{c.status}}</span>
                    </div>
                    <div class="case-email">${{c.email}}</div>
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">${{c.step_count}} Steps · Cutoff: ${{c.audit_at ? c.audit_at.split('T')[0] : 'N/A'}}</div>
                `;
                item.onclick = () => {{
                    selectedCaseId = c.case_id;
                    renderCaseList();
                    renderCaseDetail(c);
                }};
                listEl.appendChild(item);
            }});
        }}

        function renderCaseDetail(c) {{
            const detailEl = document.getElementById('detail-pane');
            const badgeClass = c.status === 'COMPLETE' ? 'badge-complete' : (c.status === 'INCOMPLETE' ? 'badge-incomplete' : 'badge-na');

            let stepsHtml = '';
            if (c.steps.length === 0) {{
                stepsHtml = '<div style="color: var(--text-muted); font-size: 14px;">No steps (Request did not authorize deletion).</div>';
            }} else {{
                stepsHtml = c.steps.map(s => {{
                    const phaseClass = s.phase === 'FINDING' ? 'phase-finding' : (s.phase === 'REMEDIATION' ? 'phase-remediation' : 'phase-verification');
                    return `
                        <div class="step-card">
                            <div class="step-no">${{s.step_no}}</div>
                            <div class="step-body">
                                <div class="step-meta">
                                    <span class="badge" style="background: #253349; color: #fff;">${{s.phase}}</span>
                                    <span class="step-op ${{phaseClass}}">${{s.operation}}</span>
                                    <span style="font-size: 11px; color: var(--text-muted);">[${{s.state}}]</span>
                                </div>
                                <div class="step-res">
                                    System: <strong>${{s.system_id}}</strong> &nbsp;·&nbsp; Resource: <strong>${{s.resource_id}}</strong>
                                </div>
                            </div>
                            ${{s.evidence_id ? `<div class="step-ev">Ev: ${{s.evidence_id}}</div>` : ''}}
                        </div>
                    `;
                }}).join('');
            }}

            detailEl.innerHTML = `
                <div class="detail-header">
                    <div>
                        <h2 style="font-size: 22px; font-weight: 700;">${{c.case_id}}</h2>
                        <div style="color: var(--text-muted); font-size: 13px; margin-top: 4px;">User: ${{c.email}}</div>
                    </div>
                    <span class="badge ${{badgeClass}}" style="font-size: 13px; padding: 6px 12px;">${{c.status}}</span>
                </div>

                <div class="meta-grid">
                    <div class="meta-item"><label>Requested At</label><value>${{c.requested_at || 'N/A'}}</value></div>
                    <div class="meta-item"><label>Reported Claim</label><value>${{c.reported_status || 'N/A'}}</value></div>
                    <div class="meta-item"><label>Reported At</label><value>${{c.reported_at || 'N/A'}}</value></div>
                    <div class="meta-item"><label>Audit Cutoff</label><value>${{c.audit_at || 'N/A'}}</value></div>
                </div>

                <div class="request-box">
                    <div style="font-size: 11px; text-transform: uppercase; color: var(--primary); font-weight: 600; margin-bottom: 4px;">Subject Request Text</div>
                    "${{c.request_text || 'No request text supplied.'}}"
                </div>

                <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 14px;">Ordered Execution & Audit Plan (${{c.steps.length}} Steps)</h3>
                <div class="steps-container">
                    ${{stepsHtml}}
                </div>
            `;
        }}

        // Search and filter listeners
        document.getElementById('search-input').addEventListener('input', (e) => {{
            searchQuery = e.target.value;
            renderCaseList();
        }});

        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                currentFilter = btn.getAttribute('data-filter');
                renderCaseList();
            }});
        }});

        // Initial render
        renderCaseList();
        if (CASES.length > 0) renderCaseDetail(CASES[0]);
    </script>
</body>
</html>"""

    with open('dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("dashboard.html created successfully!")

if __name__ == '__main__':
    build_dashboard()
