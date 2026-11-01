#!/usr/bin/env node
/**
 * ServiceVoxel L1 证据包 → GitHub 批量上传
 * 零依赖，只用 Node 内置模块。Node 18+ 可跑（你是 v24，没问题）。
 *
 *   node upload.js --dry                  ← 先预演，只列文件不上传
 *   node upload.js --token github_pat_xxx ← 正式上传
 */
'use strict';
const fs = require('fs');
const path = require('path');
const https = require('https');

const OWNER = 'zmufo';
const REPO  = 'servicevoxel-l1-evidence';
const BRANCH = 'main';
const MSG = 'L1-SILENCE-001: 十项判据冻结与判定，10/10 TRUE';

function parseArgs(argv) {
  const a = { token: null, dir: process.cwd(), dry: false };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === '--token') a.token = argv[++i];
    else if (argv[i] === '--dir') a.dir = argv[++i];
    else if (argv[i] === '--dry') a.dry = true;
  }
  return a;
}

// 路径保留 / 作分隔符，只对中文等做编码
function apiPath(p) {
  return p.split('/').map(encodeURIComponent).join('/');
}

function req(method, urlPath, token, bodyObj) {
  return new Promise((resolve, reject) => {
    const data = bodyObj ? Buffer.from(JSON.stringify(bodyObj), 'utf8') : null;
    const headers = {
      Authorization: 'token ' + token,
      Accept: 'application/vnd.github+json',
      'User-Agent': 'servicevoxel-uploader',
      'X-GitHub-Api-Version': '2022-11-28'
    };
    if (data) {
      headers['Content-Type'] = 'application/json';
      headers['Content-Length'] = data.length;
    }
    const r = https.request(
      { hostname: 'api.github.com', port: 443, path: urlPath, method, headers },
      res => {
        let buf = '';
        res.setEncoding('utf8');
        res.on('data', c => (buf += c));
        res.on('end', () => {
          let json = null;
          try { json = buf ? JSON.parse(buf) : null; } catch (e) { json = null; }
          resolve({ status: res.statusCode, body: json, raw: buf.slice(0, 300) });
        });
      }
    );
    r.on('error', reject);
    r.setTimeout(60000, () => r.destroy(new Error('请求超时')));
    if (data) r.write(data);
    r.end();
  });
}

async function getSha(token, filePath) {
  const r = await req('GET', `/repos/${OWNER}/${REPO}/contents/${apiPath(filePath)}?ref=${BRANCH}`, token, null);
  if (r.status === 200 && r.body && r.body.sha) return r.body.sha;
  return null;
}

async function putFile(token, filePath, localAbs, sha) {
  const b64 = fs.readFileSync(localAbs).toString('base64');
  const body = { message: MSG, content: b64, branch: BRANCH };
  if (sha) body.sha = sha;   // 已存在则更新（脚本可重复跑）
  return req('PUT', `/repos/${OWNER}/${REPO}/contents/${apiPath(filePath)}`, token, body);
}

function walk(dir, base, out) {
  for (const it of fs.readdirSync(dir, { withFileTypes: true })) {
    const abs = path.join(dir, it.name);
    if (it.isDirectory()) {
      if (it.name === '.git' || it.name === 'node_modules') continue;
      walk(abs, base, out);
    } else {
      out.push({ rel: path.relative(base, abs).split(path.sep).join('/'), abs });
    }
  }
  return out;
}

(async () => {
  const args = parseArgs(process.argv);
  const files = walk(args.dir, args.dir, []);

  console.log(`将上传 ${files.length} 个文件:`);
  files.forEach((f, i) => console.log(`  [${i + 1}] ${f.rel}`));

  if (args.dry) {
    console.log('\n[dry] 预演模式，未上传。确认无误后加 --token 正式执行。');
    return;
  }
  if (!args.token) {
    console.error('\n需要 --token。生成方式见说明。');
    process.exit(1);
  }

  let ok = 0, fail = 0;
  const failed = [];
  for (const f of files) {
    const sha = await getSha(args.token, f.rel);
    const r = await putFile(args.token, f.rel, f.abs, sha);
    if (r.status === 201 || r.status === 200) {
      console.log(`  [OK ${r.status}] ${f.rel}`);
      ok++;
    } else {
      console.log(`  [XX ${r.status}] ${f.rel}  ${(r.body && r.body.message) || r.raw}`);
      fail++;
      failed.push(f.rel);
    }
  }
  console.log(`\n完成: 成功 ${ok} / 失败 ${fail}`);
  if (fail) {
    console.log('失败文件（可直接重跑本脚本重试）:');
    failed.forEach(f => console.log('  - ' + f));
  }
})().catch(e => {
  console.error('运行异常: ' + e.message);
  process.exit(1);
});