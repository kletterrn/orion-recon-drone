"""Run a separately packed test or clean addon and retain engine evidence."""
import argparse
import json
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser()
p.add_argument('--build', required=True)
p.add_argument('--seconds', type=int, default=60)
p.add_argument('--fps', type=int, default=60)
p.add_argument('--headless', action='store_true')
p.add_argument('--width', type=int, default=1920)
p.add_argument('--height', type=int, default=1080)
a = p.parse_args()
cfg = json.loads((root/'local.build.json').read_text())
build = Path(a.build).resolve()
profile = build / f'game-{a.fps}-{a.width}x{a.height}'
if profile.exists():
    raise SystemExit('Use a fresh build/profile for each evidence run')
exe = Path(cfg['game'])/'ArmaReforgerSteamDiag.exe'
cmd = [str(exe), '-gproj', (build/'packed/ReconDrones.gproj').as_posix(),
       '-addons','9B5D39DA127A49B5','-addonsDir',cfg['addons'],'-profile',profile.as_posix(),
       '-server','Worlds/ORD/ORD_Runway.ent','-noFocus','-forceUpdate','-maxFPS',str(a.fps)]
if a.headless: cmd += ['-headless']
else: cmd += ['-window','-screenWidth',str(a.width),'-screenHeight',str(a.height)]
startup=subprocess.STARTUPINFO();startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
process=subprocess.Popen(cmd,cwd=cfg['game'],startupinfo=startup,stdout=subprocess.DEVNULL,stderr=subprocess.STDOUT)
deadline=time.monotonic()+a.seconds
try:
    while process.poll() is None and time.monotonic()<deadline: time.sleep(1)
finally:
    if process.poll() is None: process.terminate()
    process.wait(timeout=15)
logs=list(profile.rglob('console.log'))
content='\n'.join(x.read_text(errors='replace') for x in logs)
(build/'game.log').write_text(content,encoding='utf-8')
result={'enteredGame':'Entered online game state.' in content,
        'scriptErrors':[x for x in content.splitlines() if 'SCRIPT    (E)' in x or 'Exception' in x],
        'observations':[x for x in content.splitlines() if 'ORD_TEST_' in x],
        'fpsLimit':a.fps,'resolution':[a.width,a.height],'durationSeconds':a.seconds}
(build/'game-results.json').write_text(json.dumps(result,indent=2))
(profile/'game-results.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
if not result['enteredGame'] or result['scriptErrors'] or 'ORD_TEST_FAIL' in content: raise SystemExit(1)

