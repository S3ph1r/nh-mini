// NH-Mini Dashboard — frontend logic

const API = '';  // same origin

// ── Navigation ───────────────────────────────────────────────────────────────

function navigate(page) {
  document.querySelectorAll('.nh-page').forEach(p => p.style.display = 'none');
  document.querySelectorAll('.nhi-nav-item').forEach(a => a.classList.remove('active'));

  const target = document.getElementById(`page-${page}`);
  if (target) target.style.display = 'block';

  const navItem = document.querySelector(`[data-page="${page}"]`);
  if (navItem) navItem.classList.add('active');
}

document.querySelectorAll('.nhi-nav-item').forEach(link => {
  link.addEventListener('click', e => {
    e.preventDefault();
    const page = link.dataset.page;
    navigate(page);
    if (page === 'overview') loadOverview();
    if (page === 'infrastructure') loadInfrastructure();
    if (page === 'projects') loadProjects();
    if (page === 'services') loadServices();
    if (page === 'alerts') loadAlerts();
  });
});

// ── Helpers ───────────────────────────────────────────────────────────────────

function statusBadge(status) {
  const cls = status === 'running' ? 'nh-status-running'
            : status === 'stopped' ? 'nh-status-stopped'
            : status === 'on-demand' ? 'nh-status-on-demand'
            : 'nh-status-unknown';
  return `<span class="nh-status-badge ${cls}">${status}</span>`;
}

function containerCard(c, dim = false) {
  const ip = c.ip_address || c.ip || '—';
  const mem = c.resources ? `${Math.round(c.resources.memory_mb / 1024)}GB` : '';
  const cpu = c.resources ? `${c.resources.cpu_cores || c.resources.cpu || '?'} CPU` : '';
  return `
    <div class="nh-card nhi-glass ${dim ? 'nh-card-dim' : ''}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem">
        <div style="font-weight:600;font-size:0.95rem">${c.name}</div>
        ${statusBadge(c.status || 'unknown')}
      </div>
      <div style="font-size:0.78rem;color:var(--nhi-text-muted)">${c.vmid ? `CT${c.vmid}` : ''} · ${ip}</div>
      ${mem || cpu ? `<div style="font-size:0.75rem;color:var(--nhi-text-muted);margin-top:0.25rem">${mem} · ${cpu}</div>` : ''}
    </div>`;
}

function fmtTime(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  return d.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' }) +
         ' · ' + d.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit' });
}

// ── Health check ──────────────────────────────────────────────────────────────

async function checkHealth() {
  try {
    const r = await fetch(`${API}/api/health`);
    const ok = r.ok;
    document.getElementById('status-dot').className = `nh-status-dot ${ok ? 'nh-status-dot-ok' : 'nh-status-dot-err'}`;
    document.getElementById('status-text').textContent = ok ? 'online' : 'error';
  } catch {
    document.getElementById('status-dot').className = 'nh-status-dot nh-status-dot-err';
    document.getElementById('status-text').textContent = 'offline';
  }
}

// ── Overview ──────────────────────────────────────────────────────────────────

async function loadOverview() {
  try {
    const r = await fetch(`${API}/api/overview`);
    const d = await r.json();

    document.getElementById('node-name').textContent = d.node?.hostname || 'homelab';

    const ri = d.real_infrastructure || {};
    document.getElementById('ov-real-running').textContent = `${ri.running ?? '—'}/${ri.total ?? '—'}`;
    document.getElementById('ov-real-sub').textContent = 'running / total';

    const all = d.all_containers || {};
    document.getElementById('ov-all-total').textContent = all.total ?? '—';
    document.getElementById('ov-all-sub').textContent = `${all.running ?? 0} running · ${all.stopped ?? 0} stopped`;

    document.getElementById('ov-projects').textContent = d.projects?.total ?? '—';
    document.getElementById('ov-workspace').textContent = `active: ${d.projects?.active_workspace || 'none'}`;

    if (d.last_discovery) {
      document.getElementById('last-discovery').textContent = `last scan: ${fmtTime(d.last_discovery)}`;
    }

    // Container cards in overview
    const infra = await fetch(`${API}/api/infrastructure`).then(r => r.json());
    const grid = document.getElementById('ov-containers');
    grid.innerHTML = (infra.real || []).map(c => containerCard(c)).join('');

  } catch (e) {
    console.error('Overview load failed:', e);
  }
}

// ── Infrastructure ────────────────────────────────────────────────────────────

async function loadInfrastructure() {
  try {
    const d = await fetch(`${API}/api/infrastructure`).then(r => r.json());

    document.getElementById('infra-real').innerHTML =
      (d.real || []).map(c => containerCard(c)).join('');

    document.getElementById('infra-legacy').innerHTML =
      (d.legacy || []).map(c => containerCard(c, true)).join('');

    document.getElementById('infra-external').innerHTML =
      (d.external || []).map(c => `
        <div class="nh-card nhi-glass" style="opacity:0.85">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem">
            <div style="font-weight:600;font-size:0.95rem">${c.name}</div>
            ${statusBadge(c.status)}
          </div>
          <div style="font-size:0.78rem;color:var(--nhi-text-muted)">${c.ip} · ${c.os || ''}</div>
          <div style="font-size:0.75rem;color:var(--nhi-text-muted);margin-top:0.25rem">${c.role}</div>
        </div>`).join('');

  } catch (e) {
    console.error('Infrastructure load failed:', e);
  }
}

// ── Projects ──────────────────────────────────────────────────────────────────

async function loadProjects() {
  try {
    const d = await fetch(`${API}/api/projects`).then(r => r.json());

    document.getElementById('proj-active-badge').textContent = `active: ${d.active_workspace || 'none'}`;

    const list = document.getElementById('projects-list');
    list.innerHTML = (d.projects || []).map(p => `
      <div class="nh-project-card nhi-glass ${p.is_active ? 'nh-project-active' : ''}">
        <div style="display:flex;justify-content:space-between;align-items:flex-start">
          <div style="font-weight:600;font-size:1rem">${p.name}</div>
          <div style="display:flex;gap:0.4rem;align-items:center">
            ${p.is_active ? '<span class="nh-status-badge nh-status-running">active</span>' : ''}
            <span class="nh-status-badge nh-status-unknown" style="text-transform:lowercase">${p.status || 'dev'}</span>
          </div>
        </div>
        ${p.description ? `<div style="font-size:0.83rem;color:var(--nhi-text-muted);margin-top:0.4rem">${p.description}</div>` : ''}
        ${p.stack ? `<div style="font-size:0.72rem;color:var(--nhi-text-muted);margin-top:0.4rem;font-family:monospace;opacity:0.7">${p.stack}</div>` : ''}
        <div style="font-size:0.75rem;color:var(--nhi-text-muted);margin-top:0.5rem">
          ${p.version ? `v${p.version} · ` : ''}modified ${fmtTime(p.last_modified)}
        </div>
      </div>`).join('');

  } catch (e) {
    console.error('Projects load failed:', e);
  }
}

// ── Services ──────────────────────────────────────────────────────────────────

async function loadServices(probe = false) {
  const grid = document.getElementById('services-grid');
  if (!grid) return;
  grid.innerHTML = '<div style="color:var(--nhi-text-muted);font-size:0.85rem">Loading...</div>';

  try {
    const d = await fetch(`${API}/api/services${probe ? '?probe=true' : ''}`).then(r => r.json());

    const entries = Object.entries(d).filter(([k]) => !k.startsWith('_'));
    const meta = d._meta || {};

    grid.innerHTML = entries.map(([key, svc]) => {
      const status = svc.status || 'unknown';
      const icon = status === 'available' ? '🟢' : status === 'unreachable' ? '🔴' : status === 'local' ? '⚪' : '❓';
      const endpoint = svc.port ? `${svc.host}:${svc.port}` : (svc.host || '—');
      const consumers = svc.consumers ? svc.consumers.join(', ') : '';
      const backends = svc.backends
        ? Object.entries(svc.backends).map(([n, p]) => `${n} ${p}`).join(' · ')
        : '';

      return `
        <div class="nh-service-card nhi-glass">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.6rem">
            <div>
              <span style="font-size:1rem;margin-right:0.4rem">${icon}</span>
              <span style="font-weight:600;font-size:0.95rem">${svc.name}</span>
            </div>
            <code style="font-size:0.72rem;color:var(--nhi-text-muted);background:rgba(0,0,0,0.2);padding:0.1rem 0.4rem;border-radius:4px">${key}</code>
          </div>
          <div style="font-size:0.8rem;color:var(--nhi-text-primary);margin-bottom:0.5rem">${svc.purpose}</div>
          <div style="font-size:0.75rem;color:var(--nhi-text-muted)">
            <span style="opacity:0.7">endpoint</span> <code style="color:var(--nhi-text-primary)">${endpoint}</code>
          </div>
          ${svc.pattern ? `<div style="font-size:0.73rem;color:var(--nhi-text-muted);margin-top:0.3rem"><span style="opacity:0.7">pattern</span> ${svc.pattern}</div>` : ''}
          ${consumers ? `<div style="font-size:0.73rem;color:var(--nhi-text-muted);margin-top:0.3rem"><span style="opacity:0.7">consumers</span> ${consumers}</div>` : ''}
          ${backends ? `<div style="font-size:0.73rem;color:var(--nhi-text-muted);margin-top:0.3rem"><span style="opacity:0.7">backends</span> ${backends}</div>` : ''}
          ${svc.notes ? `<div style="font-size:0.72rem;color:var(--nhi-text-muted);margin-top:0.4rem;border-top:1px solid rgba(255,255,255,0.06);padding-top:0.4rem;opacity:0.75">${svc.notes}</div>` : ''}
        </div>`;
    }).join('');

    if (meta.generated_at) {
      const ts = document.createElement('div');
      ts.style = 'font-size:0.72rem;color:var(--nhi-text-muted);margin-top:1rem';
      ts.textContent = `${probe ? 'Live probe' : 'Cached'} · ${fmtTime(meta.generated_at)}`;
      grid.appendChild(ts);
    }

  } catch (e) {
    grid.innerHTML = '<div style="color:#fc8181">Failed to load services</div>';
  }
}

// ── Refresh button ────────────────────────────────────────────────────────────

document.getElementById('btn-refresh').addEventListener('click', async () => {
  const btn = document.getElementById('btn-refresh');
  btn.textContent = '⟳';
  btn.disabled = true;
  try {
    await fetch(`${API}/api/discovery/refresh`, { method: 'POST' });
    await loadOverview();
  } finally {
    btn.textContent = '↻';
    btn.disabled = false;
  }
});

document.addEventListener('click', e => {
  if (e.target.id === 'btn-probe') {
    e.target.textContent = '⟳';
    e.target.disabled = true;
    loadServices(true).finally(() => {
      e.target.textContent = '▶ Probe live';
      e.target.disabled = false;
    });
  }
  if (e.target.id === 'btn-heartbeat') {
    e.target.textContent = '⟳ Running...';
    e.target.disabled = true;
    fetch(`${API}/api/heartbeat/run`, { method: 'POST' })
      .then(() => loadAlerts())
      .finally(() => {
        e.target.textContent = '▶ Probe now';
        e.target.disabled = false;
      });
  }
  // Badge topbar click → vai ad alerts
  if (e.target.id === 'alerts-badge') {
    navigate('alerts');
    loadAlerts();
  }
});

// ── Alerts ───────────────────────────────────────────────────────────────────

async function loadAlerts() {
  try {
    const d = await fetch(`${API}/api/alerts`).then(r => r.json());
    const summary = d.summary || { total: 0, high: 0, medium: 0, low: 0 };
    const alerts  = (d.alerts || []).filter(a => a.status === 'active');
    const healthy = d.healthy || [];

    // Summary cards
    document.getElementById('al-total').textContent = summary.total;
    document.getElementById('al-high').textContent  = summary.high;
    document.getElementById('al-healthy').textContent = healthy.length;
    document.getElementById('al-updated').textContent =
      d.generated_at ? `updated ${fmtTime(d.generated_at)}` : 'no data — run heartbeat';

    // Topbar badge
    const badge = document.getElementById('alerts-badge');
    const navCount = document.getElementById('nav-alerts-count');
    if (summary.high > 0) {
      badge.style.display = 'inline-flex';
      badge.textContent = summary.high;
      badge.className = 'nh-alerts-badge nh-alerts-badge-high';
      navCount.style.display = 'inline';
      navCount.textContent = summary.total;
    } else if (summary.total > 0) {
      badge.style.display = 'inline-flex';
      badge.textContent = summary.total;
      badge.className = 'nh-alerts-badge nh-alerts-badge-medium';
      navCount.style.display = 'inline';
      navCount.textContent = summary.total;
    } else {
      badge.style.display = 'none';
      navCount.style.display = 'none';
    }

    // Alert cards
    const list = document.getElementById('alerts-list');
    if (alerts.length === 0) {
      list.innerHTML = `<div class="nh-card nhi-glass" style="color:var(--nhi-accent-green);display:flex;align-items:center;gap:0.7rem">
        <span style="font-size:1.3rem">✅</span>
        <div>
          <div style="font-weight:600">All systems operational</div>
          <div style="font-size:0.8rem;color:var(--nhi-text-muted);margin-top:0.2rem">
            ${d.heartbeat_status === 'no_data' ? 'Heartbeat daemon non ancora eseguito — clicca Probe now' : 'Nessun alert attivo'}
          </div>
        </div>
      </div>`;
    } else {
      list.innerHTML = alerts.map(a => {
        const sevCls = a.severity === 'HIGH'   ? 'nh-alert-card-high'
                     : a.severity === 'MEDIUM' ? 'nh-alert-card-medium'
                     : 'nh-alert-card-low';
        const sevIcon = a.severity === 'HIGH' ? '🔴' : a.severity === 'MEDIUM' ? '🟡' : '🔵';
        const since = a.first_seen ? `since ${fmtTime(a.first_seen)}` : '';
        const typeLabel = a.type === 'SERVICE_DOWN' ? 'Service Down'
                        : a.type === 'CONTAINER_STOPPED' ? 'Container Stopped'
                        : a.type || '';
        return `
          <div class="nh-alert-card nhi-glass ${sevCls}" style="margin-bottom:0.8rem">
            <div style="display:flex;justify-content:space-between;align-items:flex-start">
              <div style="display:flex;align-items:center;gap:0.5rem">
                <span>${sevIcon}</span>
                <span style="font-weight:600">${a.service_name}</span>
              </div>
              <div style="display:flex;gap:0.4rem">
                <span class="nh-status-badge nh-alert-badge-${a.severity.toLowerCase()}">${a.severity}</span>
                <span class="nh-status-badge nh-status-unknown" style="font-size:0.68rem">${typeLabel}</span>
              </div>
            </div>
            <div style="font-size:0.82rem;color:var(--nhi-text-muted);margin-top:0.5rem">${a.message}</div>
            <div style="font-size:0.72rem;color:var(--nhi-text-muted);margin-top:0.3rem;opacity:0.7">${since}</div>
          </div>`;
      }).join('');
    }

    // Healthy services list
    const healthyEl = document.getElementById('alerts-healthy-list');
    healthyEl.innerHTML = healthy.map(key => `
      <span class="nh-healthy-chip">🟢 ${key}</span>
    `).join('');

  } catch (e) {
    console.error('Alerts load failed:', e);
  }
}

// ── Init ─────────────────────────────────────────────────────────────────────

checkHealth();
loadOverview();
loadAlerts();  // carica subito per aggiornare il badge topbar
setInterval(checkHealth, 30000);
setInterval(loadOverview, 60000);
setInterval(loadAlerts, 300000);  // ogni 5 minuti (allineato al heartbeat timer)
