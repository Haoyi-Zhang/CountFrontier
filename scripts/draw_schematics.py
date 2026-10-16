"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)

NAMES=('lattice','frontiers')
def draw_all(out):
    out.mkdir(parents=True,exist_ok=True)
    d=Drawing((-.1,-.6,8.1,5.05))
    nodes=[('e',4,0,r'$\varnothing$',0),('a',1,1.4,r'$\{1\}$',0),('b',4,1.4,r'$\{2\}$',0),('c',7,1.4,r'$\{3\}$',2),('ab',1,2.8,r'$\{1,2\}$',2),('ac',4,2.8,r'$\{1,3\}$',1),('bc',7,2.8,r'$\{2,3\}$',1),('abc',4,4.2,r'$\{1,2,3\}$',1)]
    for name,x,y,label,ok in nodes:
        w=1.5 if name=='abc' else 1.2
        if ok:
            d.box(name,x,y,w,.58,label)
            if ok==2:d.ax.patches[-1].set_linewidth(1.2)
        else:d.nodes[name]=(x,y,w,.58,'rect');d.text(x,y,label)
    for a,b in [('e','a'),('e','b'),('e','c'),('a','ab'),('a','ac'),('b','ab'),('b','bc'),('c','ac'),('c','bc'),('ab','abc'),('ac','abc'),('bc','abc')]:d.edge(a,b,'n','s')
    d.save(out,'lattice')
    d=Drawing((-1.65,-1.65,6.25,3.75))
    d.text(3,3.35,r'$D_{24}=\{22,23\}$');d.arrow((3,3.1),(3,2.75))
    d.text(3,2.5,r'$(F_0,F_1)=(11,11)$ or $(12,11)$')
    for y,source,cuts in [(1.3,'source 0',[11,12]),(-.05,'source 1',[11])]:
        d.text(-.18,y,source,ha='right');d.ax.add_patch(Rectangle((0,y-.4),6,.8,fill=False,edgecolor='black',linewidth=.55))
        for r in cuts:d.line([(.25*r,y-.4),(.25*r,y+.4)])
    d.text(1.375,1.3,'11 positions');d.text(4.5,1.3,'12 positions')
    d.text(1.375,-.05,'11 positions');d.text(4.375,-.05,'13 positions')
    d.line([(2.75,1.77),(2.75,1.92),(3,1.92),(3,1.77)]);d.text(2.875,2.07,'1')
    for x,label in [(0,'0'),(2.75,'11'),(6,'24')]:d.text(x,-.7,label)
    d.text(3,-1.3,'One class histogram per outlined block');d.save(out,'frontiers')

def main():
    import tempfile
    ap=argparse.ArgumentParser(description='Direct Python vector drawings of the manuscript relationships.')
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'figures');ap.add_argument('--check',action='store_true');a=ap.parse_args()
    if a.check:
        with tempfile.TemporaryDirectory() as td:
            out=Path(td);draw_all(out)
            for name in NAMES:
                p=a.output/(name+'.pdf')
                if not p.is_file() or p.read_bytes()!=(out/(name+'.pdf')).read_bytes():raise SystemExit('Missing/stale schematic: '+name)
        print('All schematics reproduce byte-for-byte.')
    else:draw_all(a.output)
if __name__=='__main__':main()

