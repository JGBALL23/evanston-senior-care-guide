import test from 'node:test';
import assert from 'node:assert/strict';
import { validateFireUrl, buildContext, fireOperator } from './escg-wake-operator.mjs';

const token = 'sk-ant-oat01-test_token';
const url = 'https://api.anthropic.com/v1/claude_code/routines/trig_01ABCDEFGH/fire';
test('validates official routine endpoint and rejects untrusted hosts', () => {
  assert.equal(validateFireUrl(url), url);
  for (const input of ['https://evil.test/any', 'http://api.anthropic.com/v1/claude_code/routines/trig_X/fire',
    'https://api.anthropic.com.evil.test/v1/claude_code/routines/trig_X/fire', 'https://api.anthropic.com/v1/messages']) {
    assert.throws(() => validateFireUrl(input));
  }
});
test('disabled without consent, never calls HTTP', async () => {
  let calls = 0;
  const result = await fireOperator({}, () => { calls++; throw new Error('should not run'); });
  assert.equal(result.status, 'disabled');
  assert.equal(calls, 0);
});
test('fires one existing authorized routine with right headers, no external action by job', async () => {
  let calls = 0;
  const result = await fireOperator({ ESCG_WAKE_ENABLED: 'true', ESCG_OPERATOR_FIRE_URL: url, ESCG_OPERATOR_FIRE_TOKEN: token },
    async (target, args) => {
      calls++;
      assert.equal(target, url);
      assert.equal(args.method, 'POST');
      assert.equal(args.headers.Authorization, `Bearer ${token}`);
      assert.match(JSON.parse(args.body).text, /Skokie\/Niles/);
      return { ok: true, json: async () => ({ type: 'routine_fire', claude_code_session_id: 'session_0123', claude_code_session_url: 'https://claude.ai/code/session_0123' }) };
    });
  assert.equal(calls, 1);
  assert.equal(result.status, 'started');
});
test('HTTP errors never retry and do not imply outreach success', async () => {
  let calls = 0;
  await assert.rejects(() => fireOperator({ ESCG_WAKE_ENABLED: 'true', ESCG_OPERATOR_FIRE_URL: url, ESCG_OPERATOR_FIRE_TOKEN: token },
    async () => { calls++; return { ok: false, status: 429, json: async () => ({}) }; }), /429/);
  assert.equal(calls, 1);
});
test('prompt prohibits unsolicited family contact and sensitive data', () => {
  assert.match(buildContext(), /do not post to closed\/private communities/);
  assert.match(buildContext(), /medical or other sensitive family details/);
});
