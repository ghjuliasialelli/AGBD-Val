import json, os, time, urllib.request, urllib.error, subprocess

UA = "AGBD-Val/1.0 (gsialelli@ethz.ch)"
API = "https://data.neonscience.org/api/v0"

def api_get(url, retries=6):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 403:
                time.sleep(2 + i * 2)
                # try basic package variant
                if "?" not in url:
                    url2 = url + "?package=basic"
                    try:
                        req = urllib.request.Request(url2, headers={"User-Agent": UA})
                        with urllib.request.urlopen(req, timeout=60) as r:
                            return json.load(r)
                    except Exception as e2:
                        last = e2
                continue
            time.sleep(1 + i)
        except Exception as e:
            last = e
            time.sleep(1 + i)
    raise last

def list_files(product, site, month):
    d = api_get(f"{API}/data/{product}/{site}/{month}")
    return d["data"]["files"]

def wget(url, dest, log):
    # resumable, skip if exists with size>0
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return "skip"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    cmd = ["wget", "-c", "-q", "--tries=4", "--timeout=120",
           "-U", UA, "-O", dest, url]
    r = subprocess.run(cmd, stdout=log, stderr=log)
    if r.returncode != 0 or not (os.path.exists(dest) and os.path.getsize(dest) > 0):
        if os.path.exists(dest) and os.path.getsize(dest) == 0:
            os.remove(dest)
        return "fail"
    return "ok"
