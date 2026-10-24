# procedural PSX-style vegetation sprites (own work)
from PIL import Image, ImageDraw
import random, math
R=random.Random(7)
def leafy(im,cx,cy,rx,ry,cols,n=260,s=(2,4)):
  d=ImageDraw.Draw(im)
  for i in range(n):
    a=R.random()*6.283; r=math.sqrt(R.random())
    x=cx+math.cos(a)*rx*r; y=cy+math.sin(a)*ry*r
    shade=0 if y<cy-ry*0.3 else 1 if y<cy+ry*0.3 else 2
    shade=min(2,max(0,shade+(1 if math.cos(a)>0.3 else 0)-(1 if R.random()<.15 else 0)))
    k=R.randint(*s); d.ellipse((x-k/2,y-k/2,x+k/2,y+k/2),fill=cols[shade])
def outline(im):
  p=im.load(); w,h=im.size; o=im.copy(); q=o.load()
  for y in range(h):
    for x in range(w):
      if p[x,y][3]==0 and any(0<=x+dx<w and 0<=y+dy<h and p[x+dx,y+dy][3] for dx,dy in((1,0),(-1,0),(0,1),(0,-1))): q[x,y]=(18,30,12,255)
  return o
G=[(120,170,60,255),(78,128,44,255),(44,82,30,255)]
# 0 bush
b=Image.new('RGBA',(32,40),(0,0,0,0)); ImageDraw.Draw(b).ellipse((4,33,28,39),fill=(60,44,22,255))
leafy(b,16,27,13,10,G,320); leafy(b,11,22,7,6,G,80); leafy(b,21,21,7,7,G,80); b=outline(b)
# 1 papyrus
p=Image.new('RGBA',(32,40),(0,0,0,0)); d=ImageDraw.Draw(p)
for i in range(7):
  x0=8+i*2.6+R.uniform(-1,1); x1=x0+R.uniform(-6,6); y1=R.randint(4,14)
  d.line((x0,39,x1,y1),fill=(70,120,40,255),width=1)
  for k in range(10):
    a=-math.pi/2+R.uniform(-1.3,1.3); d.line((x1,y1,x1+math.cos(a)*5,y1+math.sin(a)*4+2),fill=G[k%2])
  d.ellipse((x1-1,y1-1,x1+1,y1+1),fill=(150,190,70,255))
p=outline(p)
# 2 flowering shrub (oleander)
f=Image.new('RGBA',(32,40),(0,0,0,0)); ImageDraw.Draw(f).ellipse((5,34,27,39),fill=(60,44,22,255))
leafy(f,16,26,12,11,[(96,150,58,255),(62,110,40,255),(36,72,28,255)],300)
d=ImageDraw.Draw(f)
for i in range(16):
  a=R.random()*6.283; r=math.sqrt(R.random()); x=16+math.cos(a)*11*r; y=24+math.sin(a)*9*r
  c=R.choice([(236,120,170,255),(250,210,230,255),(220,80,130,255)]); d.rectangle((x,y,x+1,y+1),fill=c)
f=outline(f)
# 3 young date palm / fern fan
m=Image.new('RGBA',(32,40),(0,0,0,0)); d=ImageDraw.Draw(m)
d.line((16,39,16,24),fill=(110,80,40,255),width=3)
for i in range(9):
  a=math.pi+i*math.pi/8; L=13+R.uniform(-2,2)
  pts=[(16+math.cos(a)*t*L,22+math.sin(a)*t*L*0.8+ (t*t*8)) for t in [k/6 for k in range(7)]]
  d.line(pts,fill=G[i%2],width=2)
  for (x,y) in pts[2:]: d.point((x,y+2),fill=G[2])
m=outline(m)
A=Image.new('RGBA',(128,40),(0,0,0,0))
for i,im in enumerate([b,p,f,m]): A.paste(im,(i*32,0))
A.save('veg_atlas.png')
# tufts 16x16 x2 (544,188) and flowers 16x16 x2 (544,204)
T=Image.new('RGBA',(32,24),(0,0,0,0)); d=ImageDraw.Draw(T)
for j,cols in enumerate([G,[(150,160,70,255),(110,120,50,255),(80,80,40,255)]]):
  for i in range(12):
    x0=j*16+3+i*0.9; d.line((x0,15,x0+R.uniform(-4,4),R.randint(4,11)),fill=cols[i%3])
for i in range(6):
  x=16+3+i*2; d.line((x,23,x+R.uniform(-2,2),18),fill=G[1]); d.rectangle((x,17,x+1,18),fill=R.choice([(240,220,90,255),(240,240,240,255),(230,110,60,255)]))
for i in range(6):
  x=3+i*2; d.line((x,23,x+R.uniform(-2,2),18),fill=G[1]); d.rectangle((x,17,x+1,18),fill=R.choice([(120,140,230,255),(240,240,240,255),(200,90,200,255)]))
T.save('veg_small.png')
big=Image.new('RGBA',(320,96),(200,180,140,255)); big.paste(A.resize((512,160),0),(0,0)) if False else None
prev=Image.new('RGBA',(160*2,40*4),(205,180,130,255)); prev.alpha_composite(A.resize((512,160),0).crop((0,0,320,160))); prev.save('veg_preview.png')
# far palm sprite 32x40 (544,212)
P=Image.new('RGBA',(32,40),(0,0,0,0)); d=ImageDraw.Draw(P)
pts=[(16+math.sin(t/12)*2.5,39-t) for t in range(0,27)]
for i,(x,y) in enumerate(pts): d.line((x-1.5+i*0.02,y,x+1.5,y),fill=(120,84,44,255) if (i//3)%2 else (92,62,32,255))
tx,ty=pts[-1]
for i in range(9):
  a=math.pi+0.15+i*(math.pi-0.3)/8; L=14+R.uniform(-2,1)
  q=[(tx+math.cos(a)*t*L, ty+math.sin(a)*t*L*0.75+t*t*9) for t in [k/7 for k in range(8)]]
  d.line(q,fill=G[i%2],width=3); d.line(q[3:],fill=G[2],width=1)
d.ellipse((tx-2,ty-1,tx+2,ty+3),fill=(110,60,30,255))
P=outline(P); P.save('veg_palm.png')
# better flowers: rebuild bottom half (16x8 x2) of veg_small
S=Image.open('veg_small.png'); d=ImageDraw.Draw(S); d.rectangle((0,16,31,23),fill=(0,0,0,0))
for j,pal in enumerate([[(240,220,90,255),(250,250,240,255)],[(220,90,170,255),(130,150,240,255)]]):
  for i in range(5):
    x=j*16+2+i*2.8; y=R.randint(17,19); d.line((x,23,x,y+1),fill=G[1]); d.rectangle((x-1,y-1,x+1,y+1),fill=pal[i%2]); d.point((x,y),fill=(250,240,120,255))
  d.line((j*16+1,23,j*16+14,23),fill=G[2])
S.save('veg_small.png')
