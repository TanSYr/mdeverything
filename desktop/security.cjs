'use strict';
const net = require('node:net');

function isLocalURL(value, origin) {
  try {
    const url = new URL(value);
    return Boolean(origin) && url.origin === origin && !url.username && !url.password;
  } catch { return false; }
}

function externalURL(value) {
  try {
    const url = new URL(value);
    const host = url.hostname.toLowerCase().replace(/\.$/, '');
    if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) return false;
    if (host === 'localhost' || /\.(localhost|local|internal)$/.test(host) || host.startsWith('[')) return false;
    if (net.isIP(host) === 4) {
      const [a, b] = host.split('.').map(Number);
      if (a === 0 || a === 10 || a === 127 || a >= 224 || (a === 169 && b === 254) ||
          (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168)) return false;
    }
    return host.includes('.');
  } catch { return false; }
}

function authorizeHeaders(url, origin, token, headers) {
  const result = Object.fromEntries(Object.entries(headers).filter(([key]) => key.toLowerCase() !== 'x-mde-token'));
  if (isLocalURL(url, origin)) result['X-MDE-Token'] = token;
  return result;
}
module.exports = { isLocalURL, externalURL, authorizeHeaders };
