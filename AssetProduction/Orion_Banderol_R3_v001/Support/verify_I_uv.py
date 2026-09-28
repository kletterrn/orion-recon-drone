from pathlib import Path
import bpy,bmesh,json,sys,hashlib,math
P=Path(__file__).resolve().parents[1]
target=Path(sys.argv[sys.argv.index('--')+1]);bpy.ops.wm.open_mainfile(filepath=str(target))
reports=[]
if 'H_CARRIAGE_DIAGNOSTIC' not in bpy.data.scenes:
 objects=[o for o in bpy.data.collections['10_SOURCE'].all_objects if o.type=='MESH' and not o.hide_render]
else:
 bpy.context.window.scene=bpy.data.scenes['H_CARRIAGE_DIAGNOSTIC']
 objects=[o for o in bpy.data.collections['ASSEMBLY_COMPACT_VISUAL_PYLON'].all_objects if o.type=='MESH']
groups={}
for o in objects:
 assert o.data.uv_layers.get('UV_Asset'),o.name
 key=next(n.image.name for m in o.data.materials if m for n in m.node_tree.nodes if n.name=='I_BaseColor')
 groups.setdefault(key,[]).append(o)
for group,obs in groups.items():
 bpy.ops.object.select_all(action='DESELECT')
 for o in obs:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=obs[0]
 bpy.context.scene.tool_settings.use_uv_select_sync=False
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.select_all(action='DESELECT')
 bpy.ops.uv.select_overlap(extend=False)
 overlapping=0
 for o in obs:
  bm=bmesh.from_edit_mesh(o.data);layer=bm.loops.layers.uv.active
  overlapping+=sum(loop.uv_select_vert for face in bm.faces for loop in face.loops)
 bpy.ops.object.mode_set(mode='OBJECT')
 uv_area=0.;surface_area=0.
 for o in obs:
  uv=o.data.uv_layers.active.data
  for face in o.data.polygons:
   cs=[uv[i].uv for i in face.loop_indices]
   uv_area+=abs(sum(cs[i].x*cs[(i+1)%len(cs)].y-cs[(i+1)%len(cs)].x*cs[i].y for i in range(len(cs))))*.5
   surface_area+=face.area
 reports.append({'set':group,'uv_overlap_selected_loops':overlapping,'mesh_count':len(obs),'occupied_uv_area_fraction':uv_area,'base_surface_m2_local':surface_area,'approx_pixels_per_metre_at_4K':4096*math.sqrt(uv_area/surface_area) if surface_area else 0})
 # UV layout exported directly from saved base-mesh loops; no reference imagery.
 lines=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1600" viewBox="0 0 1600 1600"><rect width="1600" height="1600" fill="#162029"/><g fill="none" stroke="#9db6c5" stroke-width="0.45">']
 for o in obs:
  uv=o.data.uv_layers.active.data
  for face in o.data.polygons:
   pts=' '.join(f'{uv[i].uv.x*1600:.3f},{(1-uv[i].uv.y)*1600:.3f}' for i in face.loop_indices)
   lines.append('<polygon points="'+pts+'"/>')
 lines.append('</g></svg>')
 (P/'Previews'/('I_UV_'+group+'.svg')).write_text('\n'.join(lines))
missing=[i.name for i in bpy.data.images if i.source=='FILE' and not i.packed_file and not Path(bpy.path.abspath(i.filepath,library=i.library)).exists()]
result={'file':str(target),'sets':reports,'missing_images':missing,'all_texture_paths_resolve':not missing,'uv_overlap_check':'Blender select_overlap on each shared atlas, base mesh UVs only'}
print('I_UV_JSON '+json.dumps(result),flush=True)
