"""Static site generator: data/jobs.json -> dist/. Run: python3 build.py"""
import json, os, re, html, shutil, hashlib, datetime as dt
SITE_NAME = os.environ.get("SITE_NAME", "RemoteLedger")
SITE_URL = os.environ.get("SITE_URL", "https://getremoteledger.com").rstrip("/")
import config
L = {k: os.environ.get(k) or getattr(config, k) for k in ["SQUARE_LINK_STANDARD", "SQUARE_LINK_FEATURED", "SQUARE_LINK_SPONSOR", "SQUARE_LINK_DIGEST", "CONTACT_EMAIL", "DIGEST_FORM_ACTION"]}
OUT = "dist"; e = html.escape
slug = lambda s: re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:70]
today = dt.date.today()
jobs = [j for j in json.load(open("data/jobs.json")) if (today - dt.date.fromisoformat(j["date"])).days <= 30]
for j in jobs: j["slug"] = f'{slug(j["company"])}-{slug(j["title"])}-{hashlib.md5(j["url"].encode()).hexdigest()[:6]}'
roles = sorted({j["role"] for j in jobs})
CSS = """*{box-sizing:border-box}body{margin:0;font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:#1b2a22;background:#f4f7f5}a{color:#0a6b47}
header{background:#0c3b2e;color:#fff}header .w{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;padding:14px 18px}header a{color:#fff;text-decoration:none}
.brand{font-weight:700;font-size:1.15rem}nav a{margin-left:16px}.w{max-width:1000px;margin:0 auto;padding:0 18px}.hero{background:linear-gradient(135deg,#0c3b2e,#14614a);color:#fff;padding:34px 0}
.hero h1{margin:0 0 6px}.f{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0}.f input{flex:1 1 260px}.f input,.f select{padding:12px;border:1px solid #c5d3cc;border-radius:8px;font:inherit}
.job{display:flex;justify-content:space-between;gap:10px;background:#fff;border:1px solid #dfe8e3;border-radius:10px;padding:14px 16px;margin-bottom:10px;text-decoration:none;color:inherit}
.job:hover{border-color:#0a6b47}.job h3{margin:0;font-size:1.03rem;color:#0a3d2b}.m{font-size:.85rem;color:#5b6b63}.tag{display:inline-block;background:#e6f2ec;border-radius:99px;padding:1px 9px;font-size:.78rem;margin:4px 4px 0 0}
.d{white-space:nowrap;font-size:.8rem;color:#5b6b63}.page{background:#fff;border:1px solid #dfe8e3;border-radius:10px;padding:24px;margin:24px 0}.btn{display:inline-block;background:#0a6b47;color:#fff!important;padding:11px 20px;border-radius:8px;text-decoration:none;border:0;font:inherit;cursor:pointer}
.price{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}.price div{border:1px solid #dfe8e3;border-radius:10px;padding:16px}.price b{display:block;font-size:1.5rem}
.sp{background:#fff8e1;border:1px dashed #c99a00;border-radius:8px;padding:10px;text-align:center;margin:14px 0;font-size:.9rem}.desc{white-space:pre-line;font-size:.95rem}
footer{background:#0c3b2e;color:#b6c9bf;padding:22px 0;margin-top:24px;font-size:.85rem}footer a{color:#e3efe9}input[type=email]{padding:11px;border:1px solid #c5d3cc;border-radius:8px;width:100%;max-width:340px;font:inherit}
@media(max-width:600px){.job{flex-direction:column}nav a{margin:0 12px 0 0}}"""
def layout(title, desc, path, body, head=""):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)}</title>
<meta name="description" content="{e(desc)}"><link rel="canonical" href="{SITE_URL}/{path}"><link rel="stylesheet" href="/style.css">{head}</head><body>
<header><div class="w" style="max-width:1000px;margin:0 auto"><a class="brand" href="/">{e(SITE_NAME)}</a><nav><a href="/">Jobs</a><a href="/post-a-job/">Post a Job</a><a href="/digest/">Job Alerts</a></nav></div></header>
{body}<footer><div class="w">© {today.year} {e(SITE_NAME)} · Remote accounting, bookkeeping & finance jobs. Listings link to the employer's original posting. <a href="/post-a-job/">Post a job</a></div></footer>
<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}};</script>
<script defer src="/_vercel/insights/script.js"></script></body></html>"""
def row(j):
    return (f'<a class="job" href="/jobs/{j["slug"]}/" data-role="{e(j["role"])}" data-scope="{j["scope"]}" data-s="{e((j["title"]+" "+j["company"]+" "+j["location"]).lower())}">'
            f'<div><h3>{e(j["title"])}</h3><div class="m">{e(j["company"])} · {e(j["location"])}</div><span class="tag">{e(j["role"])}</span><span class="tag">{"US remote" if j["scope"]=="US" else "Global/Intl remote"}</span></div>'
            f'<div class="d">{j["date"]}</div></a>')
def write(p, c):
    fp = os.path.join(OUT, p) if p.endswith((".xml", ".txt", ".css")) else os.path.join(OUT, p, "index.html")
    os.makedirs(os.path.dirname(fp), exist_ok=True); open(fp, "w").write(c)
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT); write("style.css", CSS)
SP = f'<div class="sp">Sponsor slot available: put your firm in front of remote finance talent. <a href="/post-a-job/">$199/mo</a></div>'
JS = """<script>(function(){var q=document.getElementById('q'),r=document.getElementById('r'),s=document.getElementById('s'),c=document.getElementById('c'),js=document.querySelectorAll('.job');
function f(){var v=q.value.toLowerCase().trim(),n=0;js.forEach(function(j){var ok=(!r.value||j.dataset.role===r.value)&&(!s.value||(s.value==='US'?j.dataset.scope==='US':j.dataset.scope!=='US'))&&(!v||v.split(/\\s+/).every(function(w){return j.dataset.s.indexOf(w)>-1}));j.style.display=ok?'':'none';if(ok)n++});c.textContent=n+' jobs'}
[q,r,s].forEach(function(x){x.addEventListener('input',f)});f()})();</script>"""
home = (f'<section class="hero"><div class="w"><h1>Remote Accounting & Finance Jobs</h1><p>{len(jobs)} live remote roles in accounting, bookkeeping, tax, FP&A and audit, pulled from employers\' own career pages and updated daily. Nothing older than 30 days.</p></div></section>'
        f'<main class="w">{SP}<div class="f"><input id="q" type="search" placeholder="Search title or company" aria-label="Search">'
        f'<select id="r" aria-label="Role"><option value="">All roles</option>{"".join(f"<option>{e(x)}</option>" for x in roles)}</select>'
        f'<select id="s" aria-label="Region"><option value="">US & global remote</option><option value="US">US remote</option><option value="G">Global / international remote</option></select></div>'
        f'<div id="c" class="m"></div>{"".join(map(row, jobs))}<div class="page"><b>Get new remote finance jobs weekly.</b> <a href="/digest/">Join the job alert digest →</a></div></main>{JS}')
write("", layout(f"Remote Accounting & Finance Jobs ({len(jobs)} open) | {SITE_NAME}", "Live remote accounting, bookkeeping, tax, FP&A and finance jobs from real employer postings, updated daily.", "", home))
for j in jobs:
    ld = {"@context": "https://schema.org/", "@type": "JobPosting", "title": j["title"], "description": e(j["desc"][:5000]) or j["title"],
          "datePosted": j["date"], "validThrough": (dt.date.fromisoformat(j["date"]) + dt.timedelta(days=60)).isoformat() + "T00:00:00Z",
          "hiringOrganization": {"@type": "Organization", "name": j["company"]}, "jobLocationType": "TELECOMMUTE",
          "applicantLocationRequirements": {"@type": "Country", "name": "United States" if j["scope"] == "US" else "Worldwide"},
          "directApply": False, "url": j["url"]}
    body = (f'<main class="w"><div class="page"><p class="m"><a href="/">← All jobs</a></p><h1>{e(j["title"])}</h1>'
            f'<p class="m"><b>{e(j["company"])}</b> · {e(j["location"])} · {e(j["role"])}<br>Posted {j["date"]} · Source: {e(j["source"])} (employer job board) · Last checked {j["fetched"]}</p>'
            f'<p><a class="btn" href="{e(j["url"])}" rel="nofollow noopener" target="_blank">Apply on {e(j["company"])}\'s site</a></p>'
            f'<h2>About the role</h2><div class="desc">{e(j["desc"][:2500])}{"…" if len(j["desc"])>2500 else ""}</div>'
            f'<p><a class="btn" href="{e(j["url"])}" rel="nofollow noopener" target="_blank">Read the full posting and apply</a></p></div>{SP}</main>')
    write(f'jobs/{j["slug"]}', layout(f'{j["title"]} at {j["company"]} (Remote) | {SITE_NAME}', f'{j["company"]} is hiring a remote {j["title"]}. {j["location"]}. Posted {j["date"]}.',
          f'jobs/{j["slug"]}/', body, f'<script type="application/ld+json">{json.dumps(ld).replace("</", "<\\/")}</script>'))
post = f"""<main class="w"><div class="page"><h1>Post a Remote Finance Job</h1><p>Reach accountants, bookkeepers, controllers and FP&A pros looking specifically for remote work.</p>
<div class="price"><div><h3>Standard</h3><b>$49</b>30 days on the board.<br><a class="btn" href="{L['SQUARE_LINK_STANDARD']}" target="_blank" rel="noopener">Post a job</a></div>
<div><h3>Featured</h3><b>$79</b>30 days, highlighted and pinned to the top.<br><a class="btn" href="{L['SQUARE_LINK_FEATURED']}" target="_blank" rel="noopener">Post featured</a></div>
<div><h3>Sponsor slot</h3><b>$199/mo</b>Your brand in the banner on every page (one sponsor).<br><a class="btn" href="{L['SQUARE_LINK_SPONSOR']}" target="_blank" rel="noopener">Subscribe monthly</a><small style="display:block;margin-top:6px;font-size:.8rem;color:#5a6676">At checkout, choose 'Subscription' for automatic monthly billing.</small></div>
<div><h3>Digest ad</h3><b>$99</b>An ad in the weekly job-alert email.<br><a class="btn" href="{L['SQUARE_LINK_DIGEST']}" target="_blank" rel="noopener">Book digest ad</a></div></div>
<p>After paying, email the job title, link and location to <a href="mailto:{L['CONTACT_EMAIL']}">{L['CONTACT_EMAIL']}</a>. Roles must be genuinely remote and in accounting or finance.</p></div></main>"""
write("post-a-job", layout(f"Post a Remote Accounting Job | {SITE_NAME}", "Post remote accounting and finance jobs from $49. Featured $79, sponsor $199/mo, digest ad $99.", "post-a-job/", post))
SIGNUP = (f'<form action="{L["DIGEST_FORM_ACTION"]}" method="post"><input type="email" name="email" placeholder="Your email address" required> <button class="btn" type="submit">Subscribe</button></form>' if L["DIGEST_FORM_ACTION"] else f'<a class="btn" href="mailto:{L["CONTACT_EMAIL"]}?subject=Subscribe%20to%20weekly%20job%20alerts">Subscribe by email</a>')
dig = f"""<main class="w"><div class="page"><h1>Weekly Remote Finance Job Alerts</h1><p>One email a week with the newest remote accounting, bookkeeping and finance roles. Free; unsubscribe anytime.</p>
{SIGNUP}</div></main>"""
write("digest", layout(f"Remote Finance Job Alerts | {SITE_NAME}", "Free weekly email of new remote accounting and finance jobs.", "digest/", dig))
urls = ["", "post-a-job/", "digest/"] + [f'jobs/{j["slug"]}/' for j in jobs]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{SITE_URL}/{u}</loc></url>" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
print(f"Built {len(jobs)} job pages -> {OUT}/")
