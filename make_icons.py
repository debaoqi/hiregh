# Generates HireGH icons from logo-1024.png (panda logo). Usage: python3 make_icons.py www | android
import sys, glob, os
from PIL import Image, ImageDraw
BLUE=(147,190,238); BG=(237,232,220)
L=Image.open('logo-1024.png').convert('RGBA')
def full(sz):
    bg=Image.new('RGBA',L.size,BLUE+(255,)); bg.alpha_composite(L)
    return bg.resize((sz,sz),Image.LANCZOS)
def icon(sz,round_=False,fg=False):
    if fg:
        c=Image.new('RGBA',(sz,sz),(0,0,0,0)); s=int(sz*0.76); c.alpha_composite(full(s),((sz-s)//2,(sz-s)//2)); return c
    if round_:
        m=Image.new('L',(sz,sz),0); ImageDraw.Draw(m).ellipse((0,0,sz-1,sz-1),fill=255); f=full(sz); f.putalpha(m); return f
    return L.resize((sz,sz),Image.LANCZOS)

def paw(sz):
    S4=sz*4;im=Image.new('RGBA',(S4,S4),(0,0,0,0));d=ImageDraw.Draw(im);W=(255,255,255,255);u=S4/24
    d.ellipse((6.2*u,11.2*u,17.8*u,21.2*u),fill=W)
    for cx,cy,r in((4.6,9.6,2.3),(9.2,5.2,2.4),(14.8,5.2,2.4),(19.4,9.6,2.3)):d.ellipse(((cx-r)*u,(cy-r*1.2)*u,(cx+r)*u,(cy+r*1.2)*u),fill=W)
    return im.resize((sz,sz),Image.LANCZOS)
if sys.argv[1]=='www':
    for s in (192,512): icon(s).save(f'www/icon-{s}.png')
else:
    res='android/app/src/main/res'
    for f in glob.glob(res+'/mipmap-*/*.png'):
        n=os.path.basename(f); w=Image.open(f).size[0]
        icon(w,'round' in n,'foreground' in n).save(f)
    for f in glob.glob(res+'/drawable*/splash.png'):
        w,h=Image.open(f).size; im=Image.new('RGB',(w,h),BG); s=int(min(w,h)*0.30)
        im.paste(icon(s),((w-s)//2,(h-s)//2),icon(s)); im.save(f)
    for dn,sz in (('mdpi',24),('hdpi',36),('xhdpi',48),('xxhdpi',72),('xxxhdpi',96)):
        os.makedirs(res+'/drawable-'+dn,exist_ok=True);paw(sz).save(res+'/drawable-'+dn+'/ic_stat_jobpaw.png')
    p=res+'/values/ic_launcher_background.xml'
    if os.path.exists(p):
        x=open(p).read().replace('#FFFFFF','#93BEEE').replace('#CFE36B','#93BEEE')
        open(p,'w').write(x)
