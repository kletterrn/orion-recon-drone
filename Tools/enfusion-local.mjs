// Invoke the installed Enfusion MCP tools with freshly loaded machine paths.
import {pathToFileURL, fileURLToPath} from 'node:url';
import {readdirSync, existsSync, openSync, readSync, closeSync} from 'node:fs';
import {inflateSync} from 'node:zlib';
const root = process.env.ENFUSION_MCP_PACKAGE || fileURLToPath(new URL('./node_modules/enfusion-mcp',import.meta.url));
const {loadConfig} = await import(pathToFileURL(root + '/dist/config.js'));
const config = loadConfig();
// MCP currently scans only addons/*.pak; current Reforger nests these in data/.
const data = config.gamePath + '/addons/data';
if (existsSync(data)) {
 const {PakVirtualFS} = await import(pathToFileURL(root + '/dist/pak/vfs.js'));
 PakVirtualFS.instance = new PakVirtualFS(readdirSync(data).filter(p=>p.endsWith('.pak')).map(p=>data+'/'+p));
 PakVirtualFS.instanceGamePath = config.gamePath;
 PakVirtualFS.prototype.readFile = function(path) {
  const ref=this.fileIndex.get(path.replaceAll('\\','/'));
  if (!ref) return null;
  const fd=openSync(ref.pakPath,'r');
  try {
   const buffer=Buffer.alloc(ref.entry.compressed ? ref.entry.compressedLen : ref.entry.decompressedLen);
   readSync(fd,buffer,0,buffer.length,ref.entry.offset);
   const result=ref.entry.compressed ? inflateSync(buffer) : buffer;
   if (result.length!==ref.entry.decompressedLen) throw new Error('Decompressed length mismatch');
   return result;
  } finally {closeSync(fd);}
 };

}
const name = process.argv[2];
if (name === 'pak-list') {
 const {PakVirtualFS} = await import(pathToFileURL(root + '/dist/pak/vfs.js'));
 const query = JSON.parse(process.argv[3]).query.toLowerCase();
 console.log([...PakVirtualFS.instance.fileIndex.keys()].filter(x=>x.toLowerCase().includes(query)).slice(0,100).join('\n'));
 process.exit(0);
}
if (name === 'game-grep') {
 const {PakVirtualFS} = await import(pathToFileURL(root + '/dist/pak/vfs.js'));
 const needle=JSON.parse(process.argv[3]).query;
 for (const key of PakVirtualFS.instance.fileIndex.keys()) {
  if(!key.toLowerCase().startsWith('scripts/game/') || !key.toLowerCase().endsWith('.c')) continue;
  const body=PakVirtualFS.instance.readFile(key).toString('utf8');
  if(body.includes(needle)) { const lines=body.split('\n'); lines.forEach((line,i)=>{if(line.includes(needle)) console.log(key+':'+(i+1)+'\n'+lines.slice(Math.max(0,i-6),i+5).join('\n'));}); }
 }
 process.exit(0);
}
const registrations = {'game-read':'registerGameRead','asset-search':'registerAssetSearch','mod-build':'registerModBuild','game-browse':'registerGameBrowse'};
if (!registrations[name]) throw new Error('Unsupported tool');
const module = await import(pathToFileURL(root + '/dist/tools/' + name + '.js'));
let invoke;
module[registrations[name]]({registerTool(n,schema,callback) { invoke=callback; }},config);
const result=await invoke(JSON.parse(process.argv[3] || '{}'));
for (const item of result.content || []) if (item.text) console.log(item.text);





