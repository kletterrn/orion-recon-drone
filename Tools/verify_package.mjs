import {readFileSync, openSync, readSync, closeSync, writeFileSync} from 'node:fs';
import {inflateSync} from 'node:zlib';
import {resolve, join} from 'node:path';
import {createHash} from 'node:crypto';
import {PakVirtualFS} from './node_modules/enfusion-mcp/dist/pak/vfs.js';

const build = resolve(process.argv[2]);
const pak = join(build,'packed/data.pak');
const fs = new PakVirtualFS([pak]);
const manifest = JSON.parse(readFileSync(join(build,'manifest.json')));
const names = [...fs.fileIndex.keys()];
const matches = [];
for (const item of manifest) {
  // Packing compiles metadata and the project descriptor separately.
  if (item.path.endsWith('.meta') || item.path.endsWith('.gproj')) continue;
  const key = names.find(x=>x.toLowerCase()===item.path.toLowerCase());
  if (!key) throw Error('Missing packed resource: '+item.path);
  const entry = fs.fileIndex.get(key).entry;
  const fd = openSync(pak,'r');
  const bytes = Buffer.alloc(entry.compressed ? entry.compressedLen : entry.decompressedLen);
  readSync(fd,bytes,0,bytes.length,entry.offset); closeSync(fd);
  const actual = entry.compressed ? inflateSync(bytes) : bytes;
  const hash = createHash('sha256').update(actual).digest('hex');
  if (hash!==item.sha256) throw Error('Packed bytes differ: '+item.path);
  matches.push(item.path);
}
const leaked=names.filter(x=>/WorkbenchGame|Probe.*\.c$|references_private|\.blend$|\.fbx$/i.test(x));
if(leaked.length) throw Error('Excluded resources leaked: '+leaked.join(', '));
const report={passed:true, checked:matches.length, resources:names.length, matches, leaked};
writeFileSync(join(build,'packed-integrity.json'),JSON.stringify(report,null,2));
console.log(`PASS: ${matches.length} packed resources match staged source; ${names.length} total; no test/editor sources`);
