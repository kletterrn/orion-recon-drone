"""Search illustrative presentation joints against evaluated exterior surfaces."""
from pathlib import Path
import heapq,itertools,time
# Reuse the read-only collision setup; do not execute the older 2D sweep.
exec(Path(__file__).with_name('probe_gear_paths.py').read_text().split('\nreport=',1)[0])
cache={};start=(0,0,0);goal=(20,20,0);serial=itertools.count();queue=[(0,next(serial),start)];cost={start:0};prev={start:None};began=time.time()
def collision(node):
 if node not in cache:
  x,z,b=node;q=Quaternion((1,0,0),ax*x/20)@Quaternion((0,0,1),az*z/20)@Quaternion((0,1,0),math.radians(-5*b))
  hits=check(q);cache[node]=[h for h in hits if 'ATTACHMENT_' not in h[1] and 'OPENING_LIP' not in h[1]]
 return bool(cache[node])
seen=set()
while queue and len(cache)<20000:
 _,_,n=heapq.heappop(queue)
 if n in seen:continue
 seen.add(n)
 if n==goal:break
 for delta in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1),(1,1,0),(1,0,-1),(0,1,-1)]:
  m=tuple(n[i]+delta[i] for i in range(3))
  if not (-10<=m[0]<=20 and -10<=m[1]<=20 and -3<=m[2]<=12):continue
  c=cost[n]+math.sqrt(sum(v*v for v in delta))
  if c>=cost.get(m,1e9) or collision(m):continue
  if any(collision(tuple(n[i]+(m[i]-n[i])*f for i in range(3))) for f in [.25,.5,.75]):continue
  cost[m]=c;prev[m]=n;h=math.sqrt((20-m[0])**2+(20-m[1])**2+m[2]**2)
  heapq.heappush(queue,(c+1.25*h,next(serial),m))
 if len(seen)%50==0:print('SEARCH',len(seen),'evaluations',len(cache),'seconds',round(time.time()-began),flush=True)
path=[]
if goal in prev:
 n=goal
 while n is not None:path.append(n);n=prev[n]
 path.reverse()
(W/'Integration/RC8/Reports/main_three_axis_doors_v010_search.json').write_text(json.dumps({'path':path,'step_pitch':ax/20,'step_yaw':az/20,'step_bank':math.radians(-5),'states_evaluated':len(cache),'seconds':time.time()-began,'clearance_scope':'v010 hidden-pivot candidate; deployed payload, fuselage, bay walls and offset doors; connected fork/axle motion; edges sampled at quarter steps; pin/lip interfaces require inspection'},indent=2))
print('MAIN_3AXIS_RESULT',path,'evaluations',len(cache),flush=True)
