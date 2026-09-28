"""Use the minimum practical offset under each curved bay edge, retaining v005 motion."""
from pathlib import Path
code=Path(__file__).with_name('build_motion_v006.py').read_text()
code=code.replace('v006','v008')
code=code.replace('hinge.location.z=-.415','hinge_z=-.390 if "NOSE_" in hinge.name else -.375;hinge.location.z=hinge_z')
code=code.replace('M.translation.z=-.415','M.translation.z=hinge_z')
exec(compile(code,str(Path(__file__).with_name('build_motion_v006.py')),'exec'))
