"""Generate the Naren profile's SVG panels and README from profile.json.

Original vector artwork; static SVGs with outlined open-source type.
No visitor tracking, external widgets, API tokens, or fabricated activity.
"""
from pathlib import Path
import html
import json
import math

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FONTS = ROOT / 'scripts' / 'fonts'
P = json.loads((ROOT / 'profile.json').read_text(encoding='utf-8'))
BG = '#101722'
PANEL = '#151E2C'
INK = '#F1F5FC'
MUTED = '#ADBBD0'
QUIET = '#8498B5'
LINE = '#2B3A50'
BLUE = '#8DAAFF'
CYAN = '#C4DAFF'


def get_font(name):
    return TTFont(FONTS / name)


grotesk = get_font('SpaceGrotesk.ttf')
mono = get_font('IBMPlexMono.ttf')
FACES = {
    'regular': instantiateVariableFont(grotesk, {'wght': 450}, inplace=False),
    'bold': instantiateVariableFont(grotesk, {'wght': 700}, inplace=False),
    'mono': mono,
}


def width(s, size, face='regular', tracking=0):
    f = FACES[face]
    cmap = f.getBestCmap()
    return sum(f['hmtx'][cmap.get(ord(c), '.notdef')][0] for c in s) * size / f['head'].unitsPerEm + max(0, len(s)-1) * tracking


def text(s, x, y, size=22, color=INK, face='regular', tracking=0, opacity=1):
    f = FACES[face]
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    pen = SVGPathPen(gs, ntos=lambda n: f'{n:.3f}'.rstrip('0').rstrip('.'))
    at = 0
    factor = size / f['head'].unitsPerEm
    for c in str(s):
        g = cmap.get(ord(c), '.notdef')
        gs[g].draw(TransformPen(pen, (factor, 0, 0, -factor, x + at, y)))
        at += f['hmtx'][g][0] * factor + tracking
    return f'<path d="{pen.getCommands()}" fill="{color}" opacity="{opacity}"/>'


def wrap(s, maxwidth, size=22, face='regular'):
    lines, current = [], ''
    for word in s.split():
        trial = (current + ' ' + word).strip()
        if current and width(trial, size, face) > maxwidth:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def paragraph(s, x, y, maxwidth, size=22, leading=31, color=MUTED, face='regular'):
    lines = wrap(s, maxwidth, size, face)
    return ''.join(text(line, x, y+i*leading, size, color, face) for i, line in enumerate(lines))


def line(x1, y1, x2, y2, color=LINE, sw=1, opacity=1):
    return f'<path d="M{x1:g} {y1:g}L{x2:g} {y2:g}" stroke="{color}" stroke-width="{sw}" opacity="{opacity}"/>'


def rect(x, y, w, h, fill=PANEL, stroke=None, r=0, opacity=1):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r:g}" fill="{fill}" opacity="{opacity}"' + (f' stroke="{stroke}"' if stroke else '') + '/>'


def circle(x, y, r, fill=BLUE, stroke=None, sw=1, opacity=1):
    return f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}" opacity="{opacity}"' + (f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '') + '/>'


def path(d, color=BLUE, sw=1, fill='none', opacity=1):
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity}"/>'


def arrow(x, y, size=23, color=INK, sw=2):
    return path(f'M{x:g} {y+size:g}L{x+size:g} {y:g}M{x:g} {y:g}H{x+size:g}V{y+size:g}', color, sw)


def cross(x, y, size=5, color=QUIET):
    return line(x-size, y, x+size, y, color) + line(x, y-size, x, y+size, color)


def svg(name, w, h, content, title, desc='', bg=BG, motion=''):
    ASSETS.mkdir(exist_ok=True)
    style = f'<style>@media (prefers-reduced-motion: no-preference) {{\n{motion}\n}}</style>\n' if motion else ''
    out = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img" aria-labelledby="title desc">
<title id="title">{html.escape(title)}</title><desc id="desc">{html.escape(desc)}</desc>
{style}{rect(0, 0, w, h, bg)}
{content}
</svg>
'''
    (ASSETS / f'{name}.svg').write_text(out, encoding='utf-8', newline='\n')


SIGNAL_MOTION = '''
.signal-trace { animation: signal-flow 5.2s linear infinite; }
@keyframes signal-flow { to { stroke-dashoffset: -100; } }
'''


def signal_trace(d, width=3, delay=0):
    return (f'<path class="signal-trace" d="{d}" pathLength="100" '
            f'stroke="{CYAN}" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-dasharray="11 89" opacity=".8" style="animation-delay:{delay}s"/>')


HERO_MOTION = SIGNAL_MOTION + '''
.wire-sculpture { animation: wire-sway 9s ease-in-out infinite; }
@keyframes wire-sway {
    0%, 50%, 100% { transform: rotate(0deg); }
    25% { transform: translateY(-9px) rotate(11deg) scale(1.035); }
    75% { transform: translateY(6px) rotate(-9deg) scale(.97); }
}
'''


def orbit(cx, cy, scale=1):
    # Project a family of three-dimensional ribbon curves. Every point is
    # computed locally; this is an abstract illustration, not a data plot.
    out = []
    trace = ''
    for j in range(25):
        t = j / 24
        points = []
        for i in range(181):
            a = 2 * math.pi * i / 180
            u = a + t * 0.85
            radius = 130 + 32 * math.cos(3*u + t*2.4)
            x = radius * math.cos(u)
            y = radius * math.sin(u)
            z = 92 * math.sin(2*u + t*1.9) + (t-.5) * 42
            px = .83*x + .4*y
            py = -.17*x + .49*y + .73*z
            points.append((cx + px*scale, cy + py*scale))
        d = 'M' + 'L'.join(f'{x:.2f} {y:.2f}' for x,y in points)
        out.append(path(d, BLUE if j%4 else CYAN, .8*scale, opacity=.26+.45*t))
        if j == 12:
            trace = signal_trace(d, width=2.1*scale)
    return (f'<g class="wire-sculpture" style="transform-origin:{cx}px {cy}px">'
            + ''.join(out) + trace + '</g>')


def hero(mobile=False):
    if mobile:
        w,h = 640,510
        c = text('n.', 32, 57, 37, INK, 'bold') + line(95, 32, 95, 62)
        c += text('NAREN214', 116, 51, 19, MUTED, 'mono', 1.6)
        c += text('NAREN', 25, 214, 142, INK, 'bold', -7)
        c += text('K S', 26, 353, 142, INK, 'bold', -7)
        c += orbit(493,296,.61)
        c += text('Software. Applied AI. The web.', 32, 418, 28, MUTED)
        c += line(32,451,608,451)
        c += text('VIT CHENNAI / COMPUTER SCIENCE', 32,484,18,QUIET,'mono')
    else:
        w,h = 960,472
        c = text('n.',40,64,40,INK,'bold') + line(107,33,107,68)
        c += text('NAREN214',130,57,17,MUTED,'mono',1.5)
        c += text('SOFTWARE / APPLIED AI / WEB',610,57,15,QUIET,'mono',.7)
        c += text('NAREN',28,235,170,INK,'bold',-8)
        c += text('K S',28,393,170,INK,'bold',-8)
        c += text('Software.',338,315,27,MUTED)
        c += text('Applied AI.',338,351,27,MUTED)
        c += text('The web.',338,387,27,MUTED)
        c += orbit(756,268,1.08)
        c += line(40,429,920,429)
        c += text('NAREN K S',40,456,14,QUIET,'mono',1)
        c += text('VIT CHENNAI / COMPUTER SCIENCE',582,456,14,QUIET,'mono',.4)
    svg('hero-mobile' if mobile else 'hero',w,h,c,'Naren K S — Software, applied AI, and the web',
        'An original technical folio with oversized typography and a generative wire sculpture.', motion=HERO_MOTION)


def section(kind, mobile=False):
    w = 640 if mobile else 960
    title = 'Selected work' if kind=='work' else 'Focus + toolkit'
    n = '01' if kind=='work' else '02'
    c = text(n,32 if mobile else 40,58,20,BLUE,'mono')
    c += text(title,92 if mobile else 100,61,36 if mobile else 40,INK,'bold',-1)
    if not mobile:
        caption = 'FOUR PROJECTS / FOUR DIFFERENT PROBLEMS' if kind=='work' else 'CURRENT DIRECTION / WORKING TOOLS'
        c += text(caption,100,89,12,QUIET,'mono',.8)
    c += line(32 if mobile else 40,108,w-32 if mobile else w-40,108)
    svg(f'section-{kind}'+('-mobile' if mobile else ''),w,124,c,title)


AUDIO_MOTION = '''
.audio-meter { transform-box: fill-box; transform-origin: center bottom; animation: audio-level 2.4s ease-in-out infinite; }
.audio-playhead { animation: audio-sweep 5.4s linear infinite; }
@keyframes audio-level {
    0%, 100% { transform: scaleY(.48); }
    38% { transform: scaleY(1.25); }
    72% { transform: scaleY(.72); }
}
@keyframes audio-sweep {
    0% { transform: translateX(0); opacity: 0; }
    8%, 92% { opacity: .82; }
    100% { transform: translateX(244px); opacity: 0; }
}
'''


def art_unheard():
    c = rect(5,19,280,187,BG,LINE,10)
    for i in range(1,8):
        c += line(18,35+i*20,272,35+i*20,LINE,.6)
    for i in range(1,12):
        c += line(18+i*22,34,18+i*22,190,LINE,.6)
    pts=[]
    for i in range(121):
        x = 22+i*2.1
        y = 114 + 34*math.sin(i*.07)*math.cos(i*.025)
        pts.append((x,y))
    c += path('M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in pts),CYAN,2.5)
    for idx in (10,38,70,104):
        x,y=pts[idx]
        c+=circle(x,y,5,BG,BLUE,1.5)+circle(x,y,2,BLUE)
    for i in range(40):
        ht=5+abs(math.sin(i*.38)*math.cos(i*.12))*22
        delay = -(i*.11 + .21*math.sin(i*.4))
        c += (f'<g class="audio-meter" style="animation-delay:{delay:.2f}s">'
              + rect(25+i*6,235-ht,2.5,ht,BLUE,opacity=.35+.6*i/40) + '</g>')
    c += ('<g class="audio-playhead" opacity="0">'
          + line(23,37,23,188,BLUE,1.4) + circle(23,37,3,CYAN) + '</g>')
    c+=circle(277,19,9,BLUE)+circle(277,19,3,BG)
    return c


def art_gdg():
    c = rect(8,31,113,151,BG,LINE,8)
    c += rect(20,46,89,14,LINE,r=3)
    for y in (79,101,123):
        c += rect(21,y,57 if y!=101 else 76,5,QUIET,r=2,opacity=.65)
        c += rect(21,y+10,77 if y!=101 else 48,3,LINE,r=1)
    c += rect(20,151,54,17,BLUE,r=3)
    c += path('M121 107H154V55H179M154 107H179M154 107V159H179',BLUE,1.5)
    for route, delay in [('M121 107H154V55H179',0), ('M121 107H179',-1.7), ('M121 107H154V159H179',-3.4)]:
        c += signal_trace(route, delay=delay)
    for y in (36,88,140):
        c+=rect(179,y,106,38,BG,LINE,6)
        c+=circle(195,y+19,5,'none',BLUE)
        c+=path(f'M192 {y+19}L194 {y+21}L198 {y+16}',CYAN,1.2)
        c+=rect(207,y+12,60,4,QUIET,r=1)
        c+=rect(207,y+22,37,3,LINE,r=1)
    c+=circle(154,107,5,BLUE)
    c+=text('VALIDATE / COMMIT',39,221,15,QUIET,'mono',.5)
    return c


MAP_MOTION = '''
.map-scan { animation: map-sweep 6.8s ease-in-out infinite; }
.map-ping { transform-box: fill-box; transform-origin: center; animation: map-pulse 3.4s ease-out infinite; }
@keyframes map-sweep {
    0% { transform: translateY(0); opacity: 0; }
    14%, 85% { opacity: .82; }
    100% { transform: translateY(187px); opacity: 0; }
}
@keyframes map-pulse {
    0% { transform: scale(.68); opacity: .7; }
    80%, 100% { transform: scale(1.6); opacity: 0; }
}
'''


def art_drone():
    c = rect(8,18,278,220,BG,LINE,9)
    for k in range(11):
        pts=[]
        for i in range(61):
            x=10+i*4.55
            y=32+k*19+13*math.sin(i*.1+k*.33)+7*math.cos(i*.19-k*.4)
            pts.append((x,y))
        c+=path('M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in pts),LINE,1)
    c+=path('M44 192L85 161L120 175L160 113L206 137L253 66',BLUE,1.7)
    for x,y in ((44,192),(120,175),(206,137)):
        c+=circle(x,y,4,BLUE)
    c+=circle(160,113,23,'none',BLUE,1.2)+cross(160,113,31,BLUE)+circle(160,113,6,CYAN)
    c += '<g class="map-ping" opacity="0">' + circle(160,113,23,'none',BLUE,1.5) + '</g>'
    c += (f'<defs><linearGradient id="scan-band" x1="0" y1="0" x2="0" y2="1">'
          f'<stop stop-color="{BLUE}" stop-opacity="0"/><stop offset="1" stop-color="{BLUE}" stop-opacity=".24"/>'
          '</linearGradient></defs>')
    c += ('<g class="map-scan" opacity="0">' + rect(14,24,266,16,'url(#scan-band)')
          + line(14,40,280,40,CYAN,1.5) + '</g>')
    c+=rect(199,180,73,40,PANEL,LINE,4)+text('EXIF',209,205,15,BLUE,'mono')
    return c


TERMINAL_MOTION = '''
.terminal-row { animation: terminal-refresh 3.8s ease-in-out infinite; }
.terminal-cursor { animation: cursor-breathe 2.2s ease-in-out infinite; }
@keyframes terminal-refresh {
    0%, 100% { opacity: .58; }
    27% { opacity: 1; }
    63% { opacity: .72; }
}
@keyframes cursor-breathe { 0%, 100% { opacity: .4; } 50% { opacity: 1; } }
'''


def art_terminal():
    c=rect(7,22,281,211,BG,LINE,10)+line(7,54,288,54)
    for x in (23,36,49):
        c+=circle(x,38,3,QUIET)
    ramp='.:+*#'
    for r in range(12):
        row = []
        for col in range(28):
            xx=(col-13.5)/13.5
            yy=(r-5.5)/5.5
            val=math.sin(xx*3+yy*2)+math.cos(yy*4-xx*2)
            if abs(xx)*.8+abs(yy)*.3 < .9:
                ch=ramp[int(abs(val)*2.3)%5]
                row.append(text(ch,28+col*8.4,78+r*10.5,9.5,BLUE if val>0 else QUIET,'mono',opacity=.5+.2*abs(val)))
        c += f'<g class="terminal-row" style="animation-delay:{-.24*r:.2f}s">' + ''.join(row) + '</g>'
    c += path('M30 215L38 220L30 225',CYAN,1.5)
    c += '<g class="terminal-cursor">' + line(46,225,66,225,CYAN,1.5) + '</g>'
    c+=text('FRAME 024 / RGB',102,220,11,QUIET,'mono')
    return c


ART = {
    'unheard': (art_unheard, AUDIO_MOTION),
    'gdg': (art_gdg, SIGNAL_MOTION),
    'drone': (art_drone, MAP_MOTION),
    'termvision': (art_terminal, TERMINAL_MOTION),
}


def tags(items,x,y,size=14,pad=12,gap=9):
    c=''
    for s in items:
        ww=width(s,size,'mono')+2*pad
        c+=rect(x,y-size-7,ww,size+18,BG,LINE,4)+text(s,x+pad,y,size,MUTED,'mono')
        x+=ww+gap
    return c


def project(p,mobile=False):
    artwork, motion = ART[p['id']]
    if mobile:
        w,h=640,640
        c=line(32,1,608,1)+text(p['number']+' / '+p['eyebrow'],32,41,18,BLUE,'mono',.3)
        c+=arrow(584,24,20,BLUE,2)
        c+=text(p['name'],29,107,46,INK,'bold',-1.8)
        c+=paragraph(p['brief'],32,154,570,28,36,INK)
        c+=paragraph(p['detail'],32,231,564,28,37,MUTED)
        for i,tag in enumerate(p['tags']):
            c+=tags([tag],32,438+i*49,21,12)
        c+=f'<g transform="translate(322 390) scale(.95)">{artwork()}</g>'
    else:
        w,h=960,320
        c=line(40,1,920,1)+text(p['number']+' / '+p['eyebrow'],40,42,14,BLUE,'mono',.5)
        c+=arrow(892,26,20,BLUE,1.7)
        c+=text(p['name'],37,111,46,INK,'bold',-1.8)
        c+=text(p['brief'],40,155,20,INK)
        c+=paragraph(p['detail'],40,195,538,18,27,MUTED)
        c+=tags(p['tags'],40,286,13,10)
        c+=f'<g transform="translate(624 59) scale(.96)">{artwork()}</g>'
    desc=f'{p["brief"]} {p["detail"]} Built with {", ".join(p["tags"])}. Open repository.'
    svg('project-'+p['id']+('-mobile' if mobile else ''),w,h,c,p['name'],desc,PANEL,motion)


def focus(mobile=False):
    if mobile:
        w,h=640,390
        c=text('CURRENT EXPLORATION',32,41,18,BLUE,'mono',.4)
        c+=text(P['focus']['title'],29,112,49,INK,'bold',-1.8)
        c+=paragraph(P['focus']['brief'],32,166,564,28,37,MUTED)
        c+=paragraph(P['focus']['detail'],32,298,564,24,32,QUIET)
    else:
        w,h=960,246
        c=text('CURRENT EXPLORATION',40,43,14,BLUE,'mono',.8)
        c+=text('LLM',36,123,76,INK,'bold',-3)
        c+=text('reliability',36,197,76,INK,'bold',-3)
        c+=line(440,45,440,207)
        c+=paragraph(P['focus']['brief'],484,83,426,22,31,MUTED)
        c+=paragraph(P['focus']['detail'],484,181,426,17,24,QUIET)
    svg('focus'+('-mobile' if mobile else ''),w,h,c,'Current focus: LLM reliability',P['focus']['brief']+' '+P['focus']['detail'])


def toolkit(mobile=False):
    if mobile:
        w,h=640,560
        c=''
        for i,g in enumerate(P['toolkit']):
            yy=34+i*134
            c+=line(32,yy,608,yy)+text(g['label'],32,yy+34,18,BLUE,'mono',.8)
            c+=paragraph(' / '.join(g['items']),32,yy+77,564,26,34,MUTED)
    else:
        w,h=960,306
        c=line(40,12,920,12)+line(480,38,480,278)
        for i,g in enumerate(P['toolkit']):
            x=40 if i%2==0 else 524
            y=52+(i//2)*144
            c+=text(g['label'],x,y,14,BLUE,'mono',.9)
            c+=paragraph(' / '.join(g['items']),x,y+42,382,23,33,MUTED)
    svg('toolkit'+('-mobile' if mobile else ''),w,h,c,'Working toolkit','; '.join(g['label']+': '+', '.join(g['items']) for g in P['toolkit']))


def contact(mobile=False):
    w,h=(640,316) if mobile else (960,242)
    x=32 if mobile else 40
    c=text('SOFTWARE / AI / COLLABORATION',x,42,17 if mobile else 14,BG,'mono',.6)
    if mobile:
        c+=text('Start a',x-3,121,62,BG,'bold',-2)
        c+=text('conversation.',x-3,185,62,BG,'bold',-2)
        c+=text(P['contact']['email'],x,270,23,BG,'mono')
        c+=arrow(553,227,36,BG,3)
    else:
        c+=text('Start a conversation.',x-4,133,65,BG,'bold',-2.5)
        c+=text(P['contact']['email'],x,199,21,BG,'mono')
        c+=arrow(847,133,48,BG,3)
    svg('contact'+('-mobile' if mobile else ''),w,h,c,'Start a conversation',P['contact']['email']+'. Open to software and AI project collaborations.',BLUE)


def picture(name,alt,href=None):
    revision = '?v=motion1' if name == 'hero' or name.startswith('project-') else ''
    block=f'''<picture>
  <source media="(max-width: 600px)" srcset="assets/{name}-mobile.svg{revision}">
  <img src="assets/{name}.svg{revision}" width="100%" alt="{html.escape(alt,quote=True)}">
</picture>'''
    return f'<a href="{href}">\n{block}\n</a>' if href else block


def readme():
    c=P['contact']
    out=['<!-- Generated by scripts/build.py from profile.json. Edit those sources. -->',picture('hero','Naren K S — Software, applied AI, and the web'),'']
    out += [f"I'm **{P['identity']['name']}**, a second-year Computer Science student at **VIT Chennai**. {P['identity']['intro']}",f'[Portfolio ↗]({c["portfolio"]}) &nbsp; / &nbsp; [LinkedIn ↗]({c["linkedin"]}) &nbsp; / &nbsp; [Email ↗](mailto:{c["email"]})','<br>',picture('section-work','01 — Selected work'),'']
    for p in P['projects']:
        out += [picture('project-'+p['id'],p['name']+' — '+p['brief']+' '+p['detail'],p['repo']),'']
    out += ['[Explore all repositories ↗](https://github.com/naren214?tab=repositories)','<br>',picture('section-focus','02 — Focus and toolkit'),picture('focus','Current focus: '+P['focus']['brief']),picture('toolkit','Working toolkit: '+'; '.join(g['label']+': '+', '.join(g['items']) for g in P['toolkit'])),'<br>',picture('contact','Start a conversation — '+c['email'],'mailto:'+c['email']),f'[Portfolio]({c["portfolio"]}) &nbsp; / &nbsp; [LinkedIn]({c["linkedin"]}) &nbsp; / &nbsp; [Email](mailto:{c["email"]})','<br>','<details>','<summary>Project index &amp; text overview</summary>','']
    for p in P['projects']:
        out += [f'### [{p["name"]}]({p["repo"]})',p['brief']+' '+p['detail'],' · '.join(p['tags']),'']
    out += ['### Current focus',P['focus']['brief']+' '+P['focus']['detail'],'','### Working toolkit','']
    for g in P['toolkit']:
        out += ['- **'+g['label'].title()+':** '+', '.join(g['items'])]
    out += ['','</details>','']
    (ROOT/'README.md').write_text('\n\n'.join(out).rstrip()+'\n',encoding='utf-8',newline='\n')


def main():
    for mobile in (False,True):
        hero(mobile)
        section('work',mobile)
        for p in P['projects']:
            project(p,mobile)
        section('focus',mobile)
        focus(mobile)
        toolkit(mobile)
        contact(mobile)
    readme()
    print('Generated 20 SVG panels and README from profile.json.')


if __name__=='__main__':
    main()
