import test from 'node:test';
import assert from 'node:assert/strict';
import { preflightUploads, MAX_UPLOAD_BYTES } from '../scripts/uploads.mjs';

test('preflight detecta videos demasiado grandes antes de comenzar las subidas', async () => {
  const files = [{file:'pequeno.mp4'}, {file:'grande.mp4'}];
  const inspect = async file => ({isFile:() => true, size:file.endsWith('grande.mp4') ? MAX_UPLOAD_BYTES + 1 : 100});
  await assert.rejects(preflightUploads('/originales', files, inspect), /grande.mp4.*300 MiB/);
  await preflightUploads('/originales', files, async () => ({isFile:() => true, size:MAX_UPLOAD_BYTES}));
  await assert.rejects(preflightUploads('/originales', files, async () => ({isFile:() => false,size:100})), /archivo válido/);
});

import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { listRemoteObjects, planUploads, uploadPlanned, fingerprint } from '../scripts/uploads.mjs';
import { createCloudflareAPI } from '../scripts/cloudflare-auth.mjs';

test('lista todas las páginas de R2 y no acepta paginación incompleta o respuestas inválidas', async () => {
  const calls = [];
  const api = createCloudflareAPI('fixture-token', async url => {
    calls.push(url);
    const second = new URL(url).searchParams.has('cursor');
    return Response.json({success:true,result:[{key:second ? 'b.mp4' : 'a.mp4',size:1,etag:'hash'}],result_info:second ? {is_truncated:false} : {is_truncated:true,cursor:'next/page+='}});
  });
  const objects = await listRemoteObjects(api, 'account', 'bucket');
  assert.deepEqual([...objects.keys()], ['a.mp4','b.mp4']);
  assert.equal(new URL(calls[1]).searchParams.get('cursor'), 'next/page+=');
  for (const body of [{result:{objects:[]}}, {result:[],result_info:{is_truncated:true}}, {result:[],result_info:{is_truncated:true,cursor:'repeated'}}]) {
    const broken = {page:async () => body};
    await assert.rejects(listRemoteObjects(broken, 'account', 'bucket'), /inválida|Paginación/);
  }
  const denied = createCloudflareAPI('fixture-token', async () => Response.json({success:false,errors:[{code:9109,message:'Denied'}]}, {status:403}));
  await assert.rejects(listRemoteObjects(denied, 'account', 'bucket'), /403/);
});

test('solo sube nuevos o cambiados, incluso con igual tamaño; una repetición no sube nada', async t => {
  const root = await mkdtemp(path.join(tmpdir(), 'media-plan-'));
  t.after(() => rm(root, {recursive:true,force:true}));
  const files = ['same','changed','new'].map(name => ({key:`videos/${name}.mp4`,file:`${name}.mp4`,contentType:'video/mp4'}));
  for (const item of files) await writeFile(path.join(root, item.file), 'ABCD');
  const local = await fingerprint(path.join(root, files[0].file));
  const remote = new Map([
    [files[0].key,{size:4,etag:`"${local.md5}"`}],
    [files[1].key,{size:4,etag:'00000000000000000000000000000000'}],
  ]);
  const plan = await planUploads(root, files, remote);
  assert.deepEqual(plan.map(item => item.upload), [false,true,true]);
  const uploaded = [];
  await uploadPlanned(root, plan, async item => { uploaded.push(item.key); remote.set(item.key,{size:item.size,etag:item.md5}); });
  assert.deepEqual(uploaded, [files[1].key,files[2].key]);
  const repeat = await planUploads(root, files, remote);
  assert.ok(repeat.every(item => !item.upload));
  assert.ok((await planUploads(root, files, remote, {force:true})).every(item => item.upload));
  remote.set(files[0].key,{size:4,etag:local.md5 + '-2'});
  assert.equal((await planUploads(root, files, remote))[0].upload, true, 'multipart desconocido se vuelve a subir conservadoramente');
});

test('no continúa tras una subida fallida ni usa un plan si el original cambió', async t => {
  const root = await mkdtemp(path.join(tmpdir(), 'media-failure-'));
  t.after(() => rm(root, {recursive:true,force:true}));
  const files = ['one','two'].map(name => ({key:`${name}.mp4`,file:`${name}.mp4`}));
  for (const item of files) await writeFile(path.join(root,item.file), 'original');
  const plan = await planUploads(root, files, new Map());
  let calls = 0;
  await assert.rejects(uploadPlanned(root, plan, async () => { calls++; throw new Error('network'); }), /network/);
  assert.equal(calls, 1);
  await writeFile(path.join(root,files[0].file), 'different file');
  await assert.rejects(uploadPlanned(root, plan, async () => { calls++; }), /cambió después/);
  assert.equal(calls, 1);
});
