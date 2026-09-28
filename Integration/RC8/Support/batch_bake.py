from pathlib import Path
p=Path('Integration/RC8/Support/build_game_assets.py');s=p.read_text(encoding='utf-8-sig');s=s.replace("groups.setdefault(group,[]).append(q)","vg=q.vertex_groups.new(name='RC8_SRC_'+o.name.removesuffix('_RC8_SKIN'));vg.add(list(range(len(q.data.vertices))),1,'REPLACE')\n groups.setdefault(group,[]).append(q)")
s=s.replace("base=sum(tris(o) for objs in groups.values() for o in objs)","for group,objs in groups.items():\n active_only(objs,objs[0]);bpy.ops.object.join();joined=bpy.context.object;joined.name=group+'_HIGH';groups[group]=[joined]\nbase=sum(tris(o) for objs in groups.values() for o in objs)")
p.write_text(s)
