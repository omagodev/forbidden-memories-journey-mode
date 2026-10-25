import sys; sys.path.insert(0,'/workspace/study/fmrecomp/art_dk/chargen/tools')
import importlib
from PIL import Image
from rig import *; from preview import *
import body, outfits
def show(outfit, out, frames=range(5), pal_o=None):
    pal_b={1:(246,205,170),2:(92,60,38)}
    pal_o=pal_o or {1:(214,170,100),2:(170,40,40),3:pal_b[1],4:(112,84,50)}
    img=Image.new('RGBA',(48*5,62*3),(150,170,120,255))
    for r,d in enumerate(["down","left","up"]):
        for f in frames:
            b=body.body_cell(d,f); o=outfits.OUTFITS[outfit](d,f)
            rb=ring_of(b); ro=ring_of(o)&~b.solid
            a=render_cell([(b,pal_b,rb),(o,pal_o,ro)],None)
            img.alpha_composite(Image.fromarray(a,'RGBA'),(f*48,r*62))
    img.resize((img.width*4,img.height*4),Image.NEAREST).save(out)
if __name__=="__main__":
    show(sys.argv[1], sys.argv[2])
