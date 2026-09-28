import bpy
for n in ['ORION_FUSELAGE','ORION_MAIN_R_CONFORMAL_SKIN','ORION_WING_ROOT_BLEND_R']:
 o=bpy.data.objects.get(n)
 print('OBJECT',n, 'exists',bool(o))
 if o:
  print('MATERIALS',[(m.name, list(m.diffuse_color), [(x.name,list(x.inputs['Base Color'].default_value)) for x in m.node_tree.nodes if x.type=='BSDF_PRINCIPLED'] if m.use_nodes else []) for m in o.data.materials if m])
