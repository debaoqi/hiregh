# Generates HireGH icons. Usage: python3 make_icons.py www | android
import sys, glob, os
from PIL import Image, ImageDraw, ImageFont
LIME=(207,227,107); INK=(22,22,22); RED=(238,90,71); BG=(237,232,220)
FONTS=glob.glob('/usr/share/fonts/**/DejaVuSans-Bold.ttf',recursive=True)+glob.glob('/usr/share/fonts/**/*Bold*.ttf',recursive=True)
def font(px):
    return ImageFont.truetype(FONTS[0],px) if FONTS else ImageFont.load_default(px)
def icon(sz,round_=False,fg=False):
    im=Image.new('RGBA',(sz,sz),(0,0,0,0) if (round_ or fg) else LIME+(255,)); d=ImageDraw.Draw(im)
    if round_: d.ellipse((0,0,sz-1,sz-1),fill=LIME)
    d.text((sz/2,sz/2),'H',fill=INK,font=font(int(sz*(0.42 if fg else 0.58))),anchor='mm')
    o=0.62 if fg else 0.68; r=sz*(0.05 if fg else 0.065)
    d.ellipse((sz*o,sz*(1-o)-r*0.5,sz*o+2*r,sz*(1-o)+1.5*r),fill=RED)
    return im
if sys.argv[1]=='www':
    for s in (192,512): icon(s).convert('RGB').save(f'www/icon-{s}.png')
else:
    res='android/app/src/main/res'
    for f in glob.glob(res+'/mipmap-*/*.png'):
        n=os.path.basename(f); w=Image.open(f).size[0]
        icon(w,'round' in n,'foreground' in n).save(f)
    for f in glob.glob(res+'/drawable*/splash.png'):
        w,h=Image.open(f).size; im=Image.new('RGB',(w,h),BG); s=int(min(w,h)*0.28)
        m=Image.new('L',(s,s),0); ImageDraw.Draw(m).rounded_rectangle((0,0,s-1,s-1),radius=s//4,fill=255)
        im.paste(icon(s),((w-s)//2,(h-s)//2),m); im.save(f)
    p=res+'/values/ic_launcher_background.xml'
    if os.path.exists(p): open(p,'w').write(open(p).read().replace('#FFFFFF','#CFE36B'))
