'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { isLocalURL, externalURL, authorizeHeaders } = require('../security.cjs');
const origin = 'http://127.0.0.1:43210';
test('token only follows the exact authenticated loopback origin', () => {
  assert.equal(isLocalURL(origin + '/api/health', origin), true);
  for (const candidate of ['http://127.0.0.1:43211/', 'http://localhost:43210/', 'https://127.0.0.1:43210/',
    'http://127.0.0.1.evil:43210/', 'http://user:pass@127.0.0.1:43210/', 'file:///etc/passwd']) {
    assert.equal(isLocalURL(candidate, origin), false, candidate);
    assert.deepEqual(authorizeHeaders(candidate, origin, 'secret', {'X-MDE-Token': 'old'}), {});
  }
  assert.equal(authorizeHeaders(origin + '/static/app.js', origin, 'secret', {})['X-MDE-Token'], 'secret');
});
test('only ordinary public HTTP(S) links open outside the application', () => {
  assert.equal(externalURL('https://example.com/video?t=5'), true);
  for (const candidate of ['javascript:alert(1)', 'file:///tmp/a', 'ftp://example.com',
    'https://user:pass@example.com', 'http://127.0.0.1:9999', 'http://localhost/', 'http://192.168.1.1',
    'http://[::1]/', 'http://example.local/']) assert.equal(externalURL(candidate), false, candidate);
});
