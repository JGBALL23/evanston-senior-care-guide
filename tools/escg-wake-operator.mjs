/**
 * ESCG authorized outreach operator wake-up.
 * Hourly cloud scheduler; one session fire at most per GitHub Actions run.
 * Keeps routine token out of public logs. Never sends emails or posts itself.
 */
import { pathToFileURL } from 'node:url';

export function validateFireUrl(value) {
  if (!value) throw new Error('Missing ESCG_OPERATOR_FIRE_URL secret');
  let url;
  try { url = new URL(value); } catch { throw new Error('Invalid ESCG_OPERATOR_FIRE_URL'); }
  if (url.protocol !== 'https:' || url.hostname !== 'api.anthropic.com' || url.port ||
      !/^\/v1\/claude_code\/routines\/trig_[a-zA-Z0-9]+\/fire$/.test(url.pathname) ||
      url.search || url.hash || url.username || url.password) {
    throw new Error('ESCG_OPERATOR_FIRE_URL must be the official HTTPS Claude routine endpoint');
  }
  return url.href;
}

export function buildContext() {
  return [
    'ESCG designated outreach operator: run ONE substantive authorized acquisition cycle.',
    'You are the EXISTING sole external email/social operator; retain your saved permissions and safety rules.',
    'Read current ops/state.json and ops/growth.json on ops/operator-state; the acquisition backlog is ops/esc-tour-loop.json on automation/esc-tour-loop.',
    'First check new inbound, consented family inquiries and replies. Answer within previously granted authority; never ask for, record or publish medical or other sensitive family details in GitHub.',
    'Next, if eligible, complete the highest-value ALREADY-PREPARED permitted external action: publish a due community post only under its current group rules, or send an appropriate verified small batch of organizational referral emails after sent-mail, decline and duplicate preflight.',
    'Existing examples to assess: Winnetka/Rogers Park post readiness and Skokie/Niles referral handoffs, checking whether actions were already performed before sending/posting.',
    'Treat those as candidates, not mandates; do not post to closed/private communities without permission or cold-message families.',
    'Log real outcomes and blockers to the existing private-safe operator state. Keep all credentials and personal family information out of public commits.',
    'If no authorized useful action exists, report idle accurately rather than manufacturing outreach. Track genuine visitors and voluntary tour inquiries, not AI sessions.',
    'Do NOT modify or merge production site code or switch the designated sender without explicit authorization.'
  ].join('\n');
}

export async function fireOperator(env, fetchFn = fetch) {
  if (env.ESCG_WAKE_ENABLED !== 'true') {
    return { status: 'disabled', message: 'ESCG_WAKE_ENABLED is not true. No Claude routine was triggered.' };
  }
  const url = validateFireUrl(env.ESCG_OPERATOR_FIRE_URL);
  const token = env.ESCG_OPERATOR_FIRE_TOKEN || '';
  if (!/^sk-ant-oat01-[a-zA-Z0-9_-]+$/.test(token)) {
    throw new Error('ESCG_OPERATOR_FIRE_TOKEN is missing or is not a Claude routine trigger token');
  }
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 20000);
  let response;
  try {
    response = await fetchFn(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'anthropic-version': '2026-10-21',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ text: buildContext() }),
      signal: controller.signal
    });
  } finally { clearTimeout(timer); }
  // No retries: Claude creates a fresh session for every successful POST.
  const json = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Claude routine request returned HTTP ${response.status}; no automatic retry (duplicate-session prevention)`);
  if (json.type !== 'routine_fire' || !/^session_[a-zA-Z0-9]+$/.test(json.claude_code_session_id || '')) {
    throw new Error('Claude response was not a confirmed routine_fire session');
  }
  return { status: 'started', session: json.claude_code_session_url || json.claude_code_session_id,
    message: 'Claude session created; outreach, post, reply or inquiry has NOT been confirmed yet.' };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  fireOperator(process.env).then(result => console.log(JSON.stringify(result)))
    .catch(err => { console.error(`ESCG operator wake failed: ${err.message}`); process.exitCode = 1; });
}
