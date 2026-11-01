"""Layout engine: runs in the browser through Pyodide (Python compiled to WebAssembly).
Every integer seed produces a different, valid website layout -> effectively infinite layouts."""
import json
import random

MOODS = {
    "any": dict(dark=None, radius=(4, 28), fonts=None),
    "clean": dict(dark=False, radius=(6, 14), fonts=[1, 2]),
    "bold": dict(dark=True, radius=(0, 8), fonts=[4, 2]),
    "elegant": dict(dark=False, radius=(0, 6), fonts=[0]),
    "playful": dict(dark=None, radius=(18, 32), fonts=[1, 3]),
}
HEADING_FONTS = [
    "Georgia, 'Times New Roman', serif",
    "'Trebuchet MS', 'Segoe UI', sans-serif",
    "system-ui, -apple-system, 'Segoe UI', sans-serif",
    "'Courier New', ui-monospace, monospace",
    "Impact, 'Arial Narrow Bold', sans-serif",
]
PREFIX = ["Nova", "Lumi", "Terra", "Pixel", "Aero", "Verd", "Orbit", "Kine", "Mono", "Flux", "Atlas", "Zen"]
SUFFIX = ["ly", "ware", "hub", "forge", "scape", "labs", "wise", "ify", "base", "craft"]
HEADLINES = [
    "{t}, made simple", "Better {t} starts here", "The calmer way to run {t}",
    "{t} that works while you sleep", "Build your {t} in minutes", "Meet the new standard for {t}",
]
SUBS = [
    "Everything you need in one place, without the clutter.",
    "Trusted by thousands of teams who want results, not setup.",
    "Start free today and scale whenever you are ready.",
]
FEATURES = [
    ("⚡", "Fast by default", "Pages load quickly on every device and connection."),
    ("🔒", "Secure", "Your data stays protected with sensible defaults."),
    ("🎯", "Focused", "Only the tools you actually use, nothing in the way."),
    ("🔧", "Flexible", "Adapt every part to match how you work."),
    ("📈", "Insightful", "Clear reports that show what is working."),
    ("🤝", "Collaborative", "Invite your team and work together in real time."),
    ("🌍", "Global", "Reach customers anywhere with built-in localization."),
    ("💬", "Supportive", "Real people answer when you need help."),
]
QUOTES = [
    ("It cut our setup time in half.", "Priya S., Founder"),
    ("Finally a tool the whole team uses.", "Marcus L., Operations"),
    ("Simple, quick, and reliable.", "Aiko T., Designer"),
]


def _palette(r, dark):
    h = r.randint(0, 359)
    if dark is None:
        dark = r.random() < 0.4
    h2 = (h + r.choice([30, 150, 180, 210])) % 360
    if dark:
        return dict(bg=f"hsl({h},30%,8%)", surface=f"hsl({h},25%,14%)", text=f"hsl({h},20%,94%)",
                    muted=f"hsl({h},12%,66%)", a=f"hsl({h},80%,62%)", b=f"hsl({h2},80%,62%)",
                    on_a=f"hsl({h},40%,8%)", line=f"hsl({h},20%,22%)")
    return dict(bg=f"hsl({h},40%,97%)", surface="#ffffff", text=f"hsl({h},40%,12%)",
                muted=f"hsl({h},12%,38%)", a=f"hsl({h},72%,40%)", b=f"hsl({h2},78%,52%)",
                on_a="#ffffff", line=f"hsl({h},25%,86%)")


def _hero(r, topic, brand):
    v = r.choice(["center", "split", "left"])
    h = r.choice(HEADLINES).format(t=topic)
    sub = r.choice(SUBS)
    cta = '<div class="row"><a class="btn" href="#contact">Start free</a><a class="btn ghost" href="#features">See how it works</a></div>'
    if v == "split":
        return (f'<section class="hero hero-split" id="top"><div class="wrap two"><div><h1>{h}</h1><p class="lead">{sub}</p>{cta}</div>'
                f'<div class="visual" aria-hidden="true"><span></span><span></span><span></span></div></div></section>')
    return (f'<section class="hero hero-{v}" id="top"><div class="wrap"><h1>{h}</h1><p class="lead">{sub}</p>{cta}</div></section>')


def _features(r):
    n = r.choice([3, 4, 6])
    items = r.sample(FEATURES, n)
    layout = r.choice(["grid", "list"])
    cards = "".join(f'<article class="card"><div class="ico">{i}</div><h3>{t}</h3><p>{d}</p></article>' for i, t, d in items)
    return f'<section class="sec feat feat-{layout} n{n}" id="features"><div class="wrap"><h2>Why people choose us</h2><div class="grid">{cards}</div></div></section>'


def _stats(r):
    vals = [("12k+", "active users"), ("99.9%", "uptime"), ("4.8/5", "average rating"), ("40+", "countries")]
    cells = "".join(f'<div><strong>{a}</strong><span>{b}</span></div>' for a, b in r.sample(vals, 3))
    return f'<section class="sec stats"><div class="wrap statrow">{cells}</div></section>'


def _gallery(r):
    cells = "".join(f'<div class="tile t{r.randint(1, 3)}" style="--k:{r.randint(0, 360)}"></div>' for _ in range(r.choice([6, 8, 9])))
    return f'<section class="sec"><div class="wrap"><h2>Recent work</h2><div class="gal">{cells}</div></div></section>'


def _testimonials(r):
    q = "".join(f'<blockquote class="card"><p>{a}</p><footer>{b}</footer></blockquote>' for a, b in r.sample(QUOTES, r.choice([2, 3])))
    return f'<section class="sec"><div class="wrap"><h2>What customers say</h2><div class="grid q">{q}</div></div></section>'


def _pricing(r):
    tiers = [("Starter", "$0", ["1 project", "Community help"]), ("Pro", "$19", ["Unlimited projects", "Priority support", "Analytics"]),
             ("Team", "$49", ["Everything in Pro", "Roles and permissions", "Shared workspace"])]
    hot = r.randint(0, 2)
    cards = "".join(
        f'<article class="card price{" hot" if i == hot else ""}"><h3>{n}</h3><p class="amt">{p}<small>/mo</small></p>'
        f'<ul>{"".join(f"<li>{x}</li>" for x in f)}</ul><a class="btn{"" if i == hot else " ghost"}" href="#contact">Choose {n}</a></article>'
        for i, (n, p, f) in enumerate(tiers))
    return f'<section class="sec" id="pricing"><div class="wrap"><h2>Simple pricing</h2><div class="grid p3">{cards}</div></div></section>'


def _cta():
    return ('<section class="sec" id="contact"><div class="wrap cta"><h2>Ready to get started?</h2>'
            '<p>Create your free account in under a minute.</p><a class="btn alt" href="#top">Create account</a></div></section>')


def _css(r, p, mood, js):
    lo, hi = mood["radius"]
    rad = r.randint(lo, hi)
    width = r.choice([1040, 1120, 1200])
    pad = r.choice([64, 88, 112])
    if mood["fonts"] is not None:
        hf = HEADING_FONTS[r.choice(mood["fonts"])]
    else:
        hf = r.choice(HEADING_FONTS)
    hero_bg = r.choice([
        f"linear-gradient(135deg,{p['a']},{p['b']})",
        f"radial-gradient(circle at 80% 0%,{p['b']}33,transparent 55%),{p['bg']}",
        p["surface"]])
    hero_on_grad = hero_bg.startswith("linear")
    hero_text = p["on_a"] if hero_on_grad else p["text"]
    css = f""":root{{--bg:{p['bg']};--surface:{p['surface']};--text:{p['text']};--muted:{p['muted']};--a:{p['a']};--b:{p['b']};--on-a:{p['on_a']};--line:{p['line']};--r:{rad}px;--w:{width}px;--pad:{pad}px}}
*{{box-sizing:border-box;margin:0}}
body{{background:var(--bg);color:var(--text);font:16px/1.6 system-ui,-apple-system,'Segoe UI',sans-serif}}
h1,h2,h3,.brand{{font-family:{hf};line-height:1.15}}
.wrap{{max-width:var(--w);margin:auto;padding:0 24px}}
a{{color:inherit}}
:focus-visible{{outline:3px solid var(--b);outline-offset:3px}}
.btn{{display:inline-block;padding:12px 22px;border-radius:var(--r);background:var(--a);color:var(--on-a);text-decoration:none;font-weight:600;border:2px solid var(--a)}}
.btn.ghost{{background:transparent;color:inherit;border-color:currentColor}}
.btn.alt{{background:var(--bg);color:var(--text);border-color:var(--bg)}}
.btn.small{{padding:8px 16px}}
.row{{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}}
.nav{{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line)}}
.nav-in{{display:flex;align-items:center;justify-content:space-between;min-height:68px;gap:16px}}
.nav-center .nav-in{{flex-direction:column;padding-top:10px;padding-bottom:10px}}
.brand{{font-size:1.4rem;font-weight:700;text-decoration:none}}
.links{{display:flex;align-items:center;gap:22px;flex-wrap:wrap}}
.links a:not(.btn){{text-decoration:none;color:var(--muted)}}
.menu-btn{{display:none;background:none;border:1px solid var(--line);color:inherit;font-size:1.3rem;padding:4px 12px;border-radius:var(--r)}}
.hero{{padding:calc(var(--pad)*1.3) 0;background:{hero_bg};color:{hero_text}}}
.hero h1{{font-size:clamp(2.2rem,5vw,4rem);max-width:16ch}}
.hero-center{{text-align:center}}.hero-center h1{{margin:auto}}.hero-center .row{{justify-content:center}}
.lead{{font-size:1.2rem;max-width:46ch;margin-top:18px;opacity:.85}}.hero-center .lead{{margin-inline:auto}}
.hero .btn{{background:{p['on_a'] if hero_on_grad else p['a']};color:{p['a'] if hero_on_grad else p['on_a']};border-color:transparent}}
.hero .btn.ghost{{background:transparent;color:inherit;border-color:currentColor}}
.two{{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:center}}
.visual{{aspect-ratio:1;position:relative}}
.visual span{{position:absolute;border-radius:var(--r);background:var(--surface);border:1px solid var(--line);box-shadow:0 20px 40px #0002}}
.visual span:nth-child(1){{inset:0 25% 35% 0;background:var(--a)}}
.visual span:nth-child(2){{inset:30% 0 0 30%;background:var(--b)}}
.visual span:nth-child(3){{inset:55% 55% 5% 5%}}
.sec{{padding:var(--pad) 0}}
h2{{font-size:clamp(1.7rem,3vw,2.5rem);margin-bottom:36px}}
.grid{{display:grid;gap:22px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}}
.feat-list .grid{{grid-template-columns:1fr}}
.feat-list .card{{display:grid;grid-template-columns:56px 1fr;column-gap:18px}}.feat-list .card h3,.feat-list .card p{{grid-column:2}}.feat-list .ico{{grid-row:span 2}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:26px}}
.card h3{{margin-bottom:8px}}.card p,.card li{{color:var(--muted)}}
.ico{{font-size:1.8rem;margin-bottom:10px}}
.stats{{background:var(--surface);padding:48px 0}}
.statrow{{display:flex;justify-content:space-around;gap:24px;flex-wrap:wrap;text-align:center}}
.statrow strong{{display:block;font-size:2.4rem;font-family:{hf};color:var(--a)}}.statrow span{{color:var(--muted)}}
.gal{{display:grid;grid-template-columns:repeat(4,1fr);grid-auto-rows:120px;gap:14px}}
.tile{{border-radius:var(--r);background:linear-gradient(135deg,hsl(var(--k),70%,55%),hsl(calc(var(--k) + 50),70%,45%))}}
.t2{{grid-row:span 2}}.t3{{grid-column:span 2}}
.price .amt{{font-size:2.6rem;font-family:{hf};color:var(--text);margin:8px 0 14px}}.price small{{font-size:1rem;color:var(--muted)}}
.price ul{{list-style:none;padding:0;margin-bottom:22px;display:grid;gap:6px}}
.price.hot{{border:2px solid var(--a);transform:translateY(-8px)}}
blockquote p{{color:var(--text);font-size:1.15rem}}blockquote footer{{margin-top:12px;color:var(--muted)}}
.cta{{background:linear-gradient(135deg,var(--a),var(--b));color:var(--on-a);border-radius:var(--r);padding:56px 28px;text-align:center}}
.cta h2{{margin-bottom:10px}}.cta p{{margin-bottom:24px}}
.foot{{border-top:1px solid var(--line);padding:36px 0;color:var(--muted)}}
.frow{{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap;align-items:center}}.frow nav{{display:flex;gap:18px}}
@media(max-width:760px){{.two{{grid-template-columns:1fr}}.visual{{max-height:260px}}.gal{{grid-template-columns:repeat(2,1fr)}}.price.hot{{transform:none}}}}
"""
    if js:
        css += """@media(max-width:760px){.menu-btn{display:block}.links{display:none;width:100%;flex-direction:column;align-items:flex-start;padding-bottom:14px}.nav.open .links{display:flex}.nav-in{flex-wrap:wrap}}
.js .reveal{opacity:0;transform:translateY(16px);transition:opacity .6s,transform .6s}.js .reveal.in{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){.js .reveal{opacity:1;transform:none;transition:none}}
"""
    return css


PAGES = {
    "home": ("Home", ["hero", "features", "stats", "testimonials", "gallery", "pricing", "cta"]),
    "about": ("About", ["head", "story", "stats", "team", "testimonials", "cta"]),
    "services": ("Services", ["head", "features", "process", "pricing", "faq", "cta"]),
    "pricing": ("Pricing", ["head", "pricing", "faq", "cta"]),
    "gallery": ("Gallery", ["head", "gallery", "testimonials", "cta"]),
    "blog": ("Blog", ["head", "blog", "cta"]),
    "contact": ("Contact", ["head", "contact", "faq"]),
    "faq": ("FAQ", ["head", "faq", "cta"]),
}
LEVELS = {"easy": 2, "medium": 3, "hard": 99}  # sections kept per page; medium and easy still end with a call to action
HEADS = {
    "about": ("About us", "Who we are and why we do this work."),
    "services": ("What we do", "Practical help, from the first call to launch day."),
    "pricing": ("Pricing", "Pick a plan now and change it whenever you like."),
    "gallery": ("Our work", "A look at recent projects."),
    "blog": ("Latest from the blog", "Guides, news and stories from our team."),
    "contact": ("Get in touch", "Send a message and we will reply within one working day."),
    "faq": ("Questions, answered", "Quick answers to what people ask most."),
}
NAMES = [("Ana Rivera", "Founder"), ("Dev Patel", "Engineering"), ("Mia Chen", "Design"), ("Leo Brandt", "Support")]
FAQS = [("How do I get started?", "Create a free account and follow the short setup guide."),
        ("Can I cancel any time?", "Yes. There are no contracts and no cancellation fees."),
        ("Do you offer support?", "Every plan includes email support, and Pro adds priority replies."),
        ("Is my data safe?", "Data is encrypted in transit and at rest, and you always own it.")]
POSTS = ["5 ways to save time every week", "What we learned this year", "A beginner's guide to getting started",
         "Behind the scenes with our team", "Customer story: from idea to launch", "Small changes, big results"]


def _pick(key, level):
    secs = PAGES[key][1]
    out = secs[:LEVELS.get(level, 3)]
    if level != "hard" and secs[-1] == "cta" and "cta" not in out:
        out.append("cta")
    return out


def _nav(r, brand, js, keys, cur, fname):
    style = r.choice(["split", "center"])
    links = "".join(f'<a href="{fname(k)}"' + (' class="on" aria-current="page"' if k == cur else "") + f'>{PAGES[k][0]}</a>' for k in keys)
    btn = '<button class="menu-btn" aria-label="Menu" aria-expanded="false">☰</button>' if js else ""
    return (f'<header class="nav nav-{style}"><div class="wrap nav-in"><a class="brand" href="{fname("home")}">{brand}</a>'
            f'<nav class="links">{links}<a class="btn small" href="#contact">Get started</a></nav>{btn}</div></header>')


def _footer(brand, keys, fname):
    links = "".join(f'<a href="{fname(k)}">{PAGES[k][0]}</a>' for k in keys)
    return (f'<footer class="foot"><div class="wrap frow"><strong>{brand}</strong><nav>{links}</nav>'
            f'<small>© 2026 {brand}. All rights reserved.</small></div></footer>')


def _head(key):
    t, s = HEADS[key]
    return f'<section class="pagehead"><div class="wrap"><h1>{t}</h1><p class="lead">{s}</p></div></section>'


def _story(r, topic, brand):
    return (f'<section class="sec"><div class="wrap two"><div><h2>Our story</h2><p>{brand} started in {r.randint(2009, 2022)} with one idea: '
            f'{topic} should be easier for everyone. We kept the team small, listened closely and built only what people asked for.</p></div>'
            '<div class="card"><h3>What we value</h3><ul class="vals"><li>Clear communication</li><li>Fair prices</li><li>Work that lasts</li></ul></div></div></section>')


def _team(r):
    c = "".join(f'<article class="card"><div class="avatar" style="--k:{r.randint(0, 360)}"></div><h3>{n}</h3><p>{t}</p></article>'
                for n, t in r.sample(NAMES, r.choice([3, 4])))
    return f'<section class="sec"><div class="wrap"><h2>The team</h2><div class="grid team">{c}</div></div></section>'


def _process():
    steps = [("Tell us your goals", "A short call to understand what you need."), ("We plan and build", "You see progress at every stage."),
             ("Launch and support", "We stay with you after go-live.")]
    li = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in steps)
    return f'<section class="sec"><div class="wrap"><h2>How it works</h2><ol class="steps">{li}</ol></div></section>'


def _faq(r):
    d = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in r.sample(FAQS, r.choice([3, 4])))
    return f'<section class="sec"><div class="wrap narrow"><h2>Common questions</h2>{d}</div></section>'


def _blog(r):
    c = "".join(f'<article class="card post"><div class="tile" style="--k:{r.randint(0, 360)}"></div><h3>{t}</h3><p>{r.randint(3, 9)} min read</p></article>'
                for t in r.sample(POSTS, r.choice([3, 4, 6])))
    return f'<section class="sec"><div class="wrap"><h2>Recent posts</h2><div class="grid">{c}</div></div></section>'


def _contact(brand):
    return ('<section class="sec"><div class="wrap two"><form class="contact-form card" novalidate action="mailto:hello@example.com" method="post" enctype="text/plain">'
            '<label>Name<input name="name" required></label><label>Email<input type="email" name="email" required></label>'
            '<label>Message<textarea name="message" rows="5" required></textarea></label>'
            '<button class="btn" type="submit">Send message</button><p class="note" role="status"></p></form>'
            f'<div><h3>Visit or call</h3><p>12 Market Street<br>hello@example.com<br>+1 555 0100</p><p>Open Monday to Friday, 9am to 5pm.</p></div></div></section>')


EXTRA_CSS = """.links a.on{color:var(--text);font-weight:600}
.pagehead{padding:calc(var(--pad)*.7) 0 40px;background:var(--surface);border-bottom:1px solid var(--line)}.pagehead h1{font-size:clamp(2rem,4vw,3.2rem)}
.narrow{max-width:760px}details{border:1px solid var(--line);border-radius:var(--r);padding:14px 18px;margin-bottom:10px;background:var(--surface)}
summary{cursor:pointer;font-weight:600}details p{margin-top:8px;color:var(--muted)}
.avatar{width:72px;height:72px;border-radius:50%;margin:0 auto 12px;background:linear-gradient(135deg,hsl(var(--k),65%,55%),hsl(calc(var(--k) + 50),65%,42%))}.team .card{text-align:center}
.steps{list-style:none;padding:0;counter-reset:s;display:grid;gap:18px}.steps li{counter-increment:s;display:grid;grid-template-columns:48px 1fr;column-gap:16px}
.steps li::before{content:counter(s);grid-row:span 2;width:44px;height:44px;border-radius:50%;background:var(--a);color:var(--on-a);display:grid;place-items:center;font-weight:700}.steps p{color:var(--muted)}
.post .tile{height:140px;margin-bottom:14px}.vals{padding-left:18px;color:var(--muted)}
.contact-form{display:grid;gap:14px}.contact-form label{display:grid;gap:4px;font-weight:600}
.contact-form input,.contact-form textarea{padding:11px;border:1px solid var(--line);border-radius:var(--r);background:var(--bg);color:var(--text);font:inherit}
.note{min-height:1.5em}.top-btn{position:fixed;right:18px;bottom:18px;width:46px;height:46px;border-radius:50%;border:0;background:var(--a);color:var(--on-a);font-size:1.2rem;cursor:pointer}
.theme-btn{background:none;border:1px solid var(--line);color:inherit;border-radius:var(--r);padding:4px 10px;cursor:pointer}
html.inv{filter:invert(1) hue-rotate(180deg)}
"""

JS_BASE = """document.documentElement.classList.add('js');
const nav=document.querySelector('.nav'),btn=document.querySelector('.menu-btn');
if(btn)btn.addEventListener('click',()=>{const o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o)});
"""
JS_MID = """document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',e=>{
  const t=document.querySelector(a.getAttribute('href'));
  if(t){e.preventDefault();t.scrollIntoView({behavior:'smooth'});nav&&nav.classList.remove('open')}}));
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.15});
document.querySelectorAll('.sec .card, .gal, .statrow').forEach(el=>{el.classList.add('reveal');io.observe(el)});
"""
JS_HARD = """const tb=document.createElement('button');tb.className='top-btn';tb.textContent='↑';tb.setAttribute('aria-label','Back to top');tb.hidden=true;document.body.append(tb);
tb.onclick=()=>scrollTo({top:0,behavior:'smooth'});addEventListener('scroll',()=>{tb.hidden=scrollY<500});
document.querySelectorAll('.contact-form').forEach(f=>f.addEventListener('submit',e=>{
  const note=f.querySelector('.note');
  const bad=[...f.querySelectorAll('[required]')].filter(i=>!i.value.trim()||(i.type==='email'&&!/^\\S+@\\S+\\.\\S+$/.test(i.value)));
  e.preventDefault();
  if(bad.length){note.textContent='Please check: '+bad.map(i=>i.name).join(', ')+'.';bad[0].focus()}
  else{note.textContent='Thanks! Connect this form to your email service to receive messages.';f.reset()}}));
const tg=document.createElement('button');tg.className='theme-btn';tg.textContent='◐';tg.setAttribute('aria-label','Switch light and dark colors');
const lk=document.querySelector('.links');if(lk)lk.append(tg);
try{if(localStorage.inv==='1')document.documentElement.classList.add('inv')}catch(e){}
tg.onclick=()=>{const on=document.documentElement.classList.toggle('inv');try{localStorage.inv=on?'1':'0'}catch(e){}};
"""


def _js(level):
    return JS_BASE + (JS_MID if level != "easy" else "") + (JS_HARD if level == "hard" else "")


def generate(seed, topic="your business", mood="any", level="medium", pages=None, js=True):
    """Returns JSON with every page of a multi-page site (files = real files, previews = single-file versions)."""
    seed = int(seed)
    r = random.Random(seed)
    topic = (topic or "your business").strip()
    m = MOODS.get(mood, MOODS["any"])
    keys = ["home"] + [k for k in PAGES if k != "home" and k in (pages or [])]
    fname = lambda k: "index.html" if k == "home" else k + ".html"
    brand = (r.choice(PREFIX) + r.choice(SUFFIX)).capitalize()
    css = _css(r, _palette(r, m["dark"]), m, js) + EXTRA_CSS
    script = _js(level) if js else ""
    contact = fname("contact") if "contact" in keys else fname("pricing") if "pricing" in keys else "index.html"
    build = dict(hero=lambda: _hero(r, topic, brand), features=lambda: _features(r), stats=lambda: _stats(r),
                 gallery=lambda: _gallery(r), testimonials=lambda: _testimonials(r), pricing=lambda: _pricing(r),
                 cta=_cta, head=lambda: _head(k), story=lambda: _story(r, topic, brand), team=lambda: _team(r),
                 process=_process, faq=lambda: _faq(r), blog=lambda: _blog(r), contact=lambda: _contact(brand))
    files, previews = {}, {}
    for k in keys:
        secs = _pick(k, level)
        if k == "home":  # home gets a different section order per seed
            tail = ["cta"] if secs[-1] == "cta" else []
            mid = secs[1:len(secs) - len(tail)]
            r.shuffle(mid)
            secs = secs[:1] + mid + tail
        body = "\n".join([_nav(r, brand, js, keys, k, fname)] + [build[s]() for s in secs] + [_footer(brand, keys, fname)])
        body = body.replace('href="#contact"', f'href="{contact}"').replace('class="btn alt" href="#top"', f'class="btn alt" href="{contact}"')
        if "services" in keys:
            body = body.replace('href="#features"', 'href="services.html"')
        link, tag = '<link rel="stylesheet" href="style.css">', '<script src="script.js"></script>'
        page = (f'<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
                f'<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>{PAGES[k][0]} – {brand}</title>\n{link}\n</head>\n'
                f'<body>\n{body}\n' + (tag + "\n" if js else "") + '</body>\n</html>\n')
        files[fname(k)] = page
        previews[fname(k)] = page.replace(link, f"<style>{css}</style>").replace(tag, f"<script>{script}</script>")
    files["style.css"] = css
    if js:
        files["script.js"] = script
    return json.dumps(dict(seed=seed, brand=brand, pages=[fname(k) for k in keys], files=files, previews=previews))
