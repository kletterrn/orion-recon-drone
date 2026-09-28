from pathlib import Path
s=Path('Integration/RC8/Support/build_game_assets_v002.py').read_text();s=s[:s.index('def tris(o):')]
s+='\nfor grp,os in groups.items():\n for ob in os:\n  for bn in ["BDL_Wing_L","BDL_Wing_R"]:\n   g=ob.vertex_groups.get(bn)\n   if not g:continue\n   p=[]\n   for v in ob.data.vertices:\n    try:g.weight(v.index);p.append(ob.matrix_world@v.co)\n    except RuntimeError:pass\n   print("AT_PRE_JOIN",grp,bn,len(p),[min(v[k] for v in p) for k in range(3)],[max(v[k] for v in p) for k in range(3)],flush=True)\n'
Path('Integration/RC8/Support/debug_game_prep.py').write_text(s)
