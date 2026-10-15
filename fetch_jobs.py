"""Pull real postings from public ATS APIs (Greenhouse, Lever, Ashby) for companies in companies.json,
keep remote accounting/bookkeeping/finance roles posted in the last 30 days, write data/jobs.json."""
import json, re, html, datetime as dt, urllib.request, concurrent.futures as cf, sys
UA = {"User-Agent": "Mozilla/5.0 (jobs-board fetcher)", "Accept": "application/json"}
import os
MAX_AGE = int(os.environ.get("MAX_AGE", 30))
now = dt.datetime.now(dt.timezone.utc)
ROLE = [  # (label, regex on title)
 ("Accounting", r"\baccount(ant|ing)\b|\bcontroller\b|\bcomptroller\b|\bcpa\b|revenue accountant|general ledger|\bgl\b|close manager"),
 ("Bookkeeping", r"bookkeep"),
 ("Tax", r"\btax\b"),
 ("Accounts Payable/Receivable", r"accounts? (payable|receivable)|\bbilling (specialist|analyst|operations)|\bcollections\b|\bpayroll\b"),
 ("FP&A / Finance", r"fp&a|financial (planning|analyst|reporting)|\bfinance (manager|analyst|lead|director|associate|operations|business partner)|\btreasury\b|\bcfo\b|chief financial|vp,? finance|head of finance|\bfinance\b"),
 ("Audit", r"\baudit(or)?\b|internal controls|\bsox\b"),
]
EXCLUDE = r"analytics|product owner|full stack|partner|representative|consultant|customer|success|relationship|channel|engineer|developer|software|sales|account executive|account manager|designer|recruit|marketing|product manager|scientist|counsel|attorney"
def role_of(title):
    t = title.lower()
    if re.search(EXCLUDE, t): return None
    for lab, rx in ROLE:
        if re.search(rx, t): return lab
def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25))
def clean(h, n=None):
    s = re.sub(r"<[^>]+>", " ", html.unescape(h or "")); s = re.sub(r"\s+", " ", s).strip()
    return s[:n] if n else s
def remote_scope(loc, flag=False):
    l = (loc or "").lower()
    if not (flag or "remote" in l or "anywhere" in l or "distributed" in l): return None
    ST = "al|ak|az|ar|ca|co|ct|de|fl|ga|hi|id|il|in|ia|ks|ky|la|me|md|ma|mi|mn|ms|mo|mt|ne|nv|nh|nj|nm|ny|nc|nd|oh|ok|or|pa|ri|sc|sd|tn|tx|ut|vt|va|wa|wv|wi|wy|dc"
    if re.search(r"remote\s*[-,–(]\s*(" + ST + r")\b\)?\s*$", l) or re.search(r",\s*(" + ST + r")\s*(\(remote\))?$", l): return "US"
    if re.search(r"\bus\b|u\.s\.|united states|usa|americas|north america|\b(ny|ca|tx|fl|wa|il|co|ma)\b|new york|san francisco|chicago|austin", l): return "US"
    return "Global" if re.search(r"anywhere|global|worldwide", l) or l.strip() in ("remote", "") else "International"
def gh(co):
    out = []
    for j in get(f"https://boards-api.greenhouse.io/v1/boards/{co}/jobs?content=true")["jobs"]:
        out.append(dict(title=j["title"], company=j.get("company_name") or co, location=(j.get("location") or {}).get("name", ""),
             url=j["absolute_url"], date=j.get("first_published") or j.get("updated_at"), source="Greenhouse", desc=clean(j.get("content"))))
    return out
def lever(co):
    out = []
    for j in get(f"https://api.lever.co/v0/postings/{co}?mode=json"):
        c = j.get("categories", {}); wt = j.get("workplaceType", "")
        out.append(dict(title=j["text"], company=co.title(), location=c.get("location", ""), remote_flag=wt == "remote",
             url=j["hostedUrl"], date=dt.datetime.fromtimestamp(j["createdAt"]/1000, dt.timezone.utc).isoformat(), source="Lever",
             desc=clean(j.get("descriptionPlain") or j.get("description"))))
    return out
def ashby(co):
    out = []
    d = get(f"https://api.ashbyhq.com/posting-api/job-board/{co}")
    for j in d["jobs"]:
        locs = [j.get("location", "")] + [s.get("location", "") for s in j.get("secondaryLocations", [])]
        out.append(dict(title=j["title"].strip(), company=co.title(), location=" / ".join(filter(None, locs)), remote_flag=(j.get("workplaceType") or "").lower()=="remote" or (j.get("isRemote") and not j.get("workplaceType")),
             url=j.get("jobUrl"), date=j.get("publishedAt"), source="Ashby", desc=clean(j.get("descriptionPlain") or j.get("descriptionHtml"))))
    return out
F = {"greenhouse": gh, "lever": lever, "ashby": ashby}
def run(a):
    p, co = a
    try: return F[p](co), None
    except Exception as e: return [], f"{p}/{co}: {e}"
cos = json.load(open("companies.json"))
pairs = [(p, c) for p in cos for c in cos[p]]
jobs, errs, seen = [], [], set()
with cf.ThreadPoolExecutor(24) as ex:
    for js, err in ex.map(run, pairs):
        if err: errs.append(err)
        for j in js:
            r = role_of(j["title"]); sc = remote_scope(j["location"], j.pop("remote_flag", False))
            if not (r and sc and j.get("url") and j.get("date")): continue
            d = dt.datetime.fromisoformat(j["date"].replace("Z", "+00:00"))
            if (now - d).days > MAX_AGE or j["url"] in seen: continue
            seen.add(j["url"]); j.update(role=r, scope=sc, date=d.date().isoformat(), fetched=now.date().isoformat())
            jobs.append(j)
jobs.sort(key=lambda j: j["date"], reverse=True)
import os; os.makedirs("data", exist_ok=True)
json.dump(jobs, open("data/jobs.json", "w"), indent=1, ensure_ascii=False)
print(f"{len(jobs)} remote finance/accounting jobs (<= {MAX_AGE} days) from {len({j['company'] for j in jobs})} companies; {len(errs)} source errors")
for e in errs: print("  ERR", e, file=sys.stderr)
