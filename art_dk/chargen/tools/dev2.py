import sys; sys.path.insert(0,'/workspace/study/fmrecomp/art_dk/chargen/tools')
from PIL import Image
from rig import *; from preview import *
import body, outfits, hair
def full(outfit, hairn, d, f, pal_b, pal_o, pal_h):
    b=body.body_cell(d,f); o=outfits.OUTFITS[outfit](d,f); h=hair.HAIRS[hairn](d,f)
    rb=ring_of(b); ro=ring_of(o)&~b.solid; rh=ring_of(h)&~b.solid
    return render_cell([(b,pal_b,rb),(o,pal_o,ro),(h,pal_h,rh)],None)
def sheet(combos, out, frames=(0,1,3), zoom=5):
    bgc=(150,170,120,255)
    rows_=[]
    img=Image.new('RGBA',(48*len(combos)*3, 62*4),bgc)
    for i,(outfit,hairn,pb,po,ph) in enumerate(combos):
        for r,d in enumerate(["down","left","up"]):
            for j,f in enumerate(frames):
                a=full(outfit,hairn,d,f,pb,po,ph)
                img.alpha_composite(Image.fromarray(a,'RGBA'),((i*3+j)*48,r*62))
    img.resize((img.width*zoom,img.height*zoom),Image.NEAREST).save(out)
