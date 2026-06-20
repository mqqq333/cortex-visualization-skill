from pathlib import Path
from collections import OrderedDict
import csv, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

base=Path(r'E:\learn_pytorch\pythonProject\cortex-visualization-skill-project')
rows=list(csv.DictReader((base/'demo/cortex_dk_demo_plot_data.csv').open(encoding='utf-8')))

def group_features(rows):
    feats=OrderedDict(); xs=[]; ys=[]
    for r in rows:
        fid=r['.feature_id']; sub=r.get('subgroup') or '1'
        feats.setdefault(fid, {'fill':r.get('fill_hex') or '#ccc','rings':OrderedDict()})
        x=float(r['x']); y=float(r['y'])
        feats[fid]['rings'].setdefault(sub,[]).append((x,y)); xs.append(x); ys.append(y)
    return feats,xs,ys

def perpendicular_distance(p,a,b):
    ax,ay=a; bx,by=b; px,py=p
    dx=bx-ax; dy=by-ay
    if dx==0 and dy==0: return math.hypot(px-ax,py-ay)
    return abs(dy*px-dx*py+bx*ay-by*ax)/math.hypot(dx,dy)

def rdp_open(points, eps):
    if len(points)<=2: return points[:]
    a,b=points[0],points[-1]
    dmax=-1; idx=0
    for i,p in enumerate(points[1:-1],1):
        d=perpendicular_distance(p,a,b)
        if d>dmax: dmax=d; idx=i
    if dmax>eps:
        return rdp_open(points[:idx+1],eps)[:-1]+rdp_open(points[idx:],eps)
    return [a,b]

def simplify_closed(points, eps):
    pts=points[:]
    if len(pts)<4: return pts
    if pts[0]==pts[-1]: pts=pts[:-1]
    # cut at farthest pair to avoid same start/end degeneracy
    n=len(pts); best=(0,n//2,-1)
    for i in range(n):
        for j in range(i+1,n):
            d=(pts[i][0]-pts[j][0])**2+(pts[i][1]-pts[j][1])**2
            if d>best[2]: best=(i,j,d)
    i,j,_=best
    chain1=pts[i:j+1]
    chain2=pts[j:]+pts[:i+1]
    out=rdp_open(chain1,eps)[:-1]+rdp_open(chain2,eps)[:-1]
    return out

def chaikin(points, iterations=1, ratio=0.25):
    pts=points[:]
    if pts and pts[0]==pts[-1]: pts=pts[:-1]
    for _ in range(iterations):
        new=[]; n=len(pts)
        for i in range(n):
            p=pts[i]; q=pts[(i+1)%n]
            new.append(((1-ratio)*p[0]+ratio*q[0], (1-ratio)*p[1]+ratio*q[1]))
            new.append((ratio*p[0]+(1-ratio)*q[0], ratio*p[1]+(1-ratio)*q[1]))
        pts=new
    return pts

def catmull_rom(points, samples=8):
    pts=points[:]
    if pts and pts[0]==pts[-1]: pts=pts[:-1]
    n=len(pts)
    if n<4: return pts
    out=[]
    for i in range(n):
        p0=pts[(i-1)%n]; p1=pts[i]; p2=pts[(i+1)%n]; p3=pts[(i+2)%n]
        for s in range(samples):
            t=s/samples; t2=t*t; t3=t2*t
            x=0.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3)
            y=0.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)
            out.append((x,y))
    return out

def transform(points, mode):
    if mode=='original': return points
    if mode=='rdp2': return simplify_closed(points,2.0)
    if mode=='rdp4': return simplify_closed(points,4.0)
    if mode=='rdp4_catmull': return catmull_rom(simplify_closed(points,4.0), samples=8)
    if mode=='chaikin': return chaikin(points, iterations=1)
    return points

def draw(ax, mode):
    feats,xs,ys=group_features(rows)
    for item in feats.values():
        for pts in item['rings'].values():
            pts2=transform(pts, mode)
            if len(pts2)<3: continue
            ax.add_patch(Polygon(pts2, closed=True, facecolor=item['fill'], edgecolor='#2E2E2E', linewidth=0.55, joinstyle='round'))
    pad_x=(max(xs)-min(xs))*0.04; pad_y=(max(ys)-min(ys))*0.04
    ax.set_xlim(min(xs)-pad_x,max(xs)+pad_x); ax.set_ylim(min(ys)-pad_y,max(ys)+pad_y)
    ax.set_aspect('equal'); ax.axis('off'); ax.set_title(mode, fontsize=16, color='#2E2E2E')

modes=['original','rdp2','rdp4','rdp4_catmull','chaikin']
fig,axes=plt.subplots(1,len(modes),figsize=(24,5),facecolor='white')
for ax,m in zip(axes,modes): draw(ax,m)
fig.tight_layout()
out=base/'demo/SMOOTHING_EXPERIMENT_cortex_boundaries.png'
fig.savefig(out,dpi=180,bbox_inches='tight',facecolor='white')
print(out)
