from pathlib import Path
import bpy,json
P=Path(__file__).resolve().parents[1];out={}
for file in ['Orion/Orion_Master.blend','Banderol/S8000_Banderol_Master.blend','Banderol/S8000_Banderol_VisualFit_Master.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(P/file));c=bpy.data.collections['10_SOURCE'];out[file]={'objects':len(c.all_objects),'mesh_faces':sum(len(o.data.polygons) for o in c.all_objects if o.type=='MESH'),'materials':{m.name:dict((k,list(m.node_tree.nodes.get('Principled BSDF').inputs[k].default_value) if k=='Base Color' else m.node_tree.nodes.get('Principled BSDF').inputs[k].default_value) for k in ['Base Color','Roughness','Metallic']) for m in bpy.data.materials if m.use_nodes and m.node_tree.nodes.get('Principled BSDF')},'collections':{cc.name:len(cc.all_objects) for cc in c.children},'source_names':[o.name for o in c.all_objects]}
(P/'Documentation/I_inventory.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{'objects':v['objects'],'faces':v['mesh_faces'],'materials':list(v['materials'])} for k,v in out.items()},indent=2))
