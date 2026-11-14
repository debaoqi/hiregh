# JobPaw 管理后台 APK 图标：熊猫 logo + 深色底 + 绿色盾牌徽章。用法：python3 native/admin_icons.py android
import glob, os
from PIL import Image, ImageDraw
DARK=(22,22,22); LIME=(199,230,90)
L=Image.open('logo-1024.png').convert('RGBA')
def badge(sz):
    S=sz*4; im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse((0,0,S-1,S-1),fill=LIME+(255,))
    u=S/24
    d.polygon([(12*u,4.5*u),(18.5*u,7*u),(18.5*u,12*u),(12*u,19.5*u),(5.5*u,12*u),(5.5*u,7*u)],fill=DARK+(255,))
    d.line([(8.8*u,11.6*u),(11.2*u,14*u),(15.4*u,9.4*u)],fill=LIME+(255,),width=int(1.9*u),joint='curve')
    return im.resize((sz,sz),Image.LANCZOS)
def full(sz):
    bg=Image.new('RGBA',L.size,(147,190,238,255)); bg.alpha_composite(L); bg=bg.resize((1024,1024),Image.LANCZOS)
    b=400; bg.alpha_composite(badge(b),(1024-b-70,1024-b-70))
    return bg.resize((sz,sz),Image.LANCZOS)
def icon(sz,round_=False,fg=False):
    if fg:
        c=Image.new('RGBA',(sz,sz),(0,0,0,0)); s=int(sz*0.72); c.alpha_composite(full(s),((sz-s)//2,(sz-s)//2)); return c
    f=full(sz); m=Image.new('L',(sz,sz),0)
    if round_: ImageDraw.Draw(m).ellipse((0,0,sz-1,sz-1),fill=255)
    else: ImageDraw.Draw(m).rounded_rectangle((0,0,sz-1,sz-1),radius=int(sz*0.22),fill=255)
    f.putalpha(m); return f
if __name__=='__main__':
    res='android/app/src/main/res'
    for f in glob.glob(res+'/mipmap-*/*.png'):
        n=os.path.basename(f); w=Image.open(f).size[0]
        icon(w,'round' in n,'foreground' in n).save(f)
    for f in glob.glob(res+'/drawable*/splash.png'):
        w,h=Image.open(f).size; im=Image.new('RGB',(w,h),DARK); s=int(min(w,h)*0.30)
        ic=icon(s); im.paste(ic,((w-s)//2,(h-s)//2),ic); im.save(f)
    p=res+'/values/ic_launcher_background.xml'
    if os.path.exists(p):
        import re; x=open(p).read(); x=re.sub(r'#[0-9A-Fa-f]{6}','#93BEEE',x); open(p,'w').write(x)
