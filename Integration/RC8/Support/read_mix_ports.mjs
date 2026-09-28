// Invoke the installed Enfusion MCP tools with freshly loaded machine paths.
import {pathToFileURL} from 'node:url';
import {readdirSync, existsSync, openSync, readSync, closeSync} from 'node:fs';
import {inflateSync} from 'node:zlib';
const root = process.env.ENFUSION_MCP_PACKAGE || 'C:/Users/david/AppData/Local/npm-cache/_npx/be402e1c82700767/node_modules/enfusion-mcp';
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
const {PakVirtualFS}=await import(pathToFileURL(root+'/dist/pak/vfs.js'));
const x=PakVirtualFS.instance.readFile('Sounds/FinalMix.afm').toString('utf8').split('\n');for(let i=0;i<x.length;i++) if(/name "(VEH_Engine|VEH_Animations|WPN_Explosions|WPN_TravelingProjectile|SFX|UI)"/.test(x[i])) console.log(x.slice(Math.max(0,i-4),i+10).join('\n'));
