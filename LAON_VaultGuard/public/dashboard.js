// dashboard.js — LAON VaultGuard frontend (vanilla JS + SSE)

const API = '';
let currentFilter = 'all';

// ── SSE ──
const evtSource = new EventSource('/api/events');

evtSource.addEventListener('connected', () => {
  updateConnection(true);
});

evtSource.addEventListener('scan:started', () => {
  updateConnection(true);
  loadStatus();
});

evtSource.addEventListener('scan:completed', () => {
  loadStatus();
  loadFindings();
});

evtSource.addEventListener('finding:new', () => {
  loadFindings();
  loadStatus();
});

evtSource.addEventListener('finding:acknowledged', () => {
  loadFindings();
  loadStatus();
});

evtSource.onerror = () => {
  updateConnection(false);
};

function updateConnection(connected) {
  const dot = document.getElementById('status-dot');
  const status = document.getElementById('connection-status');
  if (connected) {
    dot.className = 'status-dot online';
    status.textContent = '연결됨';
  } else {
    dot.className = 'status-dot offline';
    status.textContent = '연결 끊김 (재연결 중...)';
  }
}

// ── API ──
async function loadStatus() {
  try {
    const res = await fetch(`${API}/api/status`);
    const data = await res.json();
    document.getElementById('open-count').textContent = data.open_findings;
    document.getElementById('scan-count').textContent = data.total_scans;
    document.getElementById('repo-count').textContent = data.registered_repos;
    const lastScan = data.last_scan
      ? new Date(data.last_scan).toLocaleString('ko-KR')
      : '없음';
    document.getElementById('last-scan').textContent = lastScan;
  } catch (err) {
    console.error('Status load failed:', err);
  }
}

async function loadFindings() {
  let url = `${API}/api/findings?limit=100`;
  if (currentFilter !== 'all') {
    url += `&severity=${currentFilter}`;
  }

  try {
    const res = await fetch(url);
    const data = await res.json();
    const tbody = document.getElementById('findings-body');

    if (data.total === 0) {
      tbody.innerHTML = '<tr><td colspan="7" class="empty-state">탐지된 시크릿이 없습니다 🎉</td></tr>';
      return;
    }

    tbody.innerHTML = data.findings.map(f => `
      <tr>
        <td><span class="badge ${f.severity}">${f.severity}</span></td>
        <td>${f.provider}</td>
        <td>${f.secret_type || f.secretType}</td>
        <td title="${f.file_path || f.filePath}">${shortenPath(f.file_path || f.filePath)}</td>
        <td><code>${f.masked_fingerprint || f.maskedFingerprint}</code></td>
        <td>${new Date(f.detected_at || f.detectedAt).toLocaleString('ko-KR')}</td>
        <td>
          ${f.acknowledged
            ? '<span style="color:var(--green)">✓ 확인됨</span>'
            : `<button class="btn" onclick="acknowledge('${f.id}')">확인</button>`
          }
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Findings load failed:', err);
  }
}

async function acknowledge(id) {
  try {
    await fetch(`${API}/api/findings/${id}/acknowledge`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ note: 'Acknowledged via dashboard' }),
    });
    loadFindings();
    loadStatus();
  } catch (err) {
    console.error('Acknowledge failed:', err);
  }
}

async function triggerScan() {
  try {
    const btn = document.querySelector('.btn.primary');
    btn.disabled = true;
    btn.textContent = '⏳ 스캔 중...';
    await fetch(`${API}/api/scan/trigger`, { method: 'POST' });
    setTimeout(() => {
      btn.disabled = false;
      btn.textContent = '🔄 지금 스캔';
      loadStatus();
      loadFindings();
    }, 5000);
  } catch (err) {
    console.error('Trigger scan failed:', err);
  }
}

function setFilter(filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-bar .btn').forEach(b => b.classList.remove('active'));
  document.querySelector(`.filter-bar .btn:nth-child(${
    ['all','critical','high','medium','info'].indexOf(filter) + 1
  })`)?.classList.add('active');
  loadFindings();
}

function shortenPath(filePath) {
  if (!filePath) return '';
  if (filePath.length <= 40) return filePath;
  return '...' + filePath.slice(-37);
}

// ── Init ──
loadStatus();
loadFindings();
