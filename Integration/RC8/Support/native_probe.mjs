import {WorkbenchClient} from 'file:///C:/Users/david/AppData/Local/npm-cache/_npx/be402e1c82700767/node_modules/enfusion-mcp/dist/workbench/client.js';
const c=new WorkbenchClient('127.0.0.1',5775);console.log(JSON.stringify(await c.rawCall('ORD_RC8_ImportProbe',JSON.parse(process.argv[2]||'{}'),{timeout:8000})));
