import numpy as np, cv2
from palms_def import PALMS
bgr=cv2.imread('/workspace/study/fmrecomp/painted_work/bg_raw.jpg')
H,W=bgr.shape[:2]
hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV_FULL).astype(int)  # H 0..255
h=hsv[:,:,0]*360/255.0; s=hsv[:,:,1]/255.0; v=hsv[:,:,2]/255.0
def masks():
    out={}
    for n,(fr,tr,by) in PALMS.items():
        cx,cy,rx,ry=fr
        e=np.zeros((H,W),np.uint8); cv2.ellipse(e,(cx,cy),(rx,ry),0,0,360,255,-1)
        t=np.zeros((H,W),np.uint8); cv2.rectangle(t,(tr[0],tr[1]),(tr[2],tr[3]),255,-1)
        frond=(h>80)&(h<150)&(s>0.45)&(v>0.18)&(v<0.85)
        # grass is yellower and brighter: exclude bright yellow-green
        grass=(h<100)&(v>0.62)
        trunk=(h>8)&(h<42)&(s>0.45)&(v<0.64)
        m=((e>0)&frond&~grass)|((t>0)&trunk)
        m8=(m*255).astype(np.uint8)
        m8=cv2.morphologyEx(m8,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
        m8=cv2.morphologyEx(m8,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
        # keep the largest connected component
        nl,lab,st,_=cv2.connectedComponentsWithStats(m8)
        keep=np.zeros_like(m8)
        for k in range(1,nl):
            if st[k,cv2.CC_STAT_AREA]>=140: keep[lab==k]=255
        m8=keep
        # grow into the dark outline pixels next to the keyed ones (they are part of the palm)
        grow=cv2.dilate(m8,np.ones((5,5),np.uint8))>0
        dark=(v<0.36)
        m2=(m8>0)|(grow&dark)
        ee=cv2.dilate(e,np.ones((7,7),np.uint8))>0; tt=cv2.dilate(t,np.ones((7,7),np.uint8))>0
        out[n]=m2&(ee|tt)
    return out
if __name__=="__main__":
    ms=masks()
    ov=bgr.copy()
    for n,m in ms.items():
        ov[m]=(ov[m]*0.35+np.array([255,0,255])*0.65).astype(np.uint8)
        ys,xs=np.nonzero(m); print(n,m.sum(),xs.min(),xs.max(),ys.min(),ys.max(),"bbox",xs.max()-xs.min()+1,ys.max()-ys.min()+1)
    cv2.imwrite('palm_masks_overlay.png',ov)
