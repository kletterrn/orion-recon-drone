import {readFileSync,writeFileSync,openSync,readSync,closeSync,readdirSync} from 'node:fs';
import {inflateSync} from 'node:zlib';
import {pathToFileURL} from 'node:url';
import {createHash} from 'node:crypto';
import {resolve,join,relative} from 'node:path';

const root=resolve(import.meta.dirname,'../../..');
const pak=resolve(process.argv[2]||join(root,'Integration/RC8/Validation/Package03/data.pak'));
const packageRoot=process.env.ENFUSION_MCP_PACKAGE||'C:/Users/david/AppData/Local/npm-cache/_npx/be402e1c82700767/node_modules/enfusion-mcp';
const {PakVirtualFS}=await import(pathToFileURL(join(packageRoot,'dist/pak/vfs.js')));
const vfs=new PakVirtualFS([pak]);
const names=[...vfs.fileIndex.keys()];
const paths=[];
for(const folder of ['Assets/ORD/Models/RC8/Textures','Assets/ORD/Models/RC8/Data','Sounds/ORD/RC8','Scripts/Game/ORD']) {
 const full=join(root,folder);
 function walk(dir) {for(const item of readdirSync(dir,{withFileTypes:true})){
  const path=join(dir,item.name);if(item.isDirectory())walk(path);else if(/\.(edds|emat|wav|acp|sig|c)$/i.test(item.name))paths.push(relative(root,path).replaceAll('\\','/'));
 }}
 walk(full);
}
paths.push(...['Assets/ORD/Models/RC8/ORD_Orion_RC8.xob','Assets/ORD/Models/RC8/ORD_Banderol_RC8.xob',
 'Prefabs/ORD/ORD_Aircraft.et','Prefabs/ORD/ORD_Banderol.et','Prefabs/ORD/ORD_BanderolStore.et',
 'Worlds/ORD/ORD_Runway_Layers/default.layer','UI/ORD/Sensor.layout','Configs/System/chimeraInputCommon.conf']);
const checks=[];
for(const name of paths){
 const key=names.find(k=>k.toLowerCase()===name.toLowerCase());if(!key)throw Error('Missing '+name);
 const ref=vfs.fileIndex.get(key),entry=ref.entry;
 const fd=openSync(pak,'r'),buf=Buffer.alloc(entry.compressed?entry.compressedLen:entry.decompressedLen);
 readSync(fd,buf,0,buf.length,entry.offset);closeSync(fd);
 const actual=entry.compressed?inflateSync(buf):buf,source=readFileSync(join(root,name));
 if(!actual.equals(source))throw Error('Mismatch '+name);
 checks.push({name,bytes:actual.length,sha256:createHash('sha256').update(actual).digest('hex')});
}
const leaked=names.filter(x=>/WorkbenchGame|ORD_RC8_ImportProbe|ORD_RC8_TextureBuildPlugin|ORD_RC8_FinalModelBuildPlugin|ORD_RC8CaptureProbe/i.test(x));
if(leaked.length)throw Error('Temporary handler leaked into pack: '+leaked.join(', '));
const report={pak,resources:names.length,checked:checks.length,files:checks,temporaryHandlers:false};
const out=join(root,'Integration/RC8/Reports/packed_integrity_rc8.json');
writeFileSync(out,JSON.stringify(report,null,2));
console.log(`RC8 PAK verified: ${checks.length} exact source matches among ${names.length} resources; no temporary handlers.`);
