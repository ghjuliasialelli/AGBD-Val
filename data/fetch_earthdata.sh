#!/usr/bin/env bash
# Resumable Earthdata (URS) downloader with sha256 verification.
# Manifest TSV: id \t data_url \t dest \t sha256_url(optional, "-" if none)
# Needs `machine urs.earthdata.nasa.gov login .. password ..` in ~/.netrc.
set -u
cd "$(dirname "$0")" || exit 2
MANIFEST="${1:?usage: fetch_earthdata.sh manifest.tsv}"
CJ=/tmp/urs_cookies
AUTH=(-L -n -c "$CJ" -b "$CJ" --retry 3 --retry-delay 5 --max-time 1800 -C -)
n_ok=0; n_skip=0; n_fail=0; n_badsum=0
while IFS=$'\t' read -r id url dest sha || [ -n "$id" ]; do
  [ -z "$id" ] && continue; case "$id" in \#*) continue;; esac
  mkdir -p "$(dirname "$dest")"
  if [ -f "$dest" ] && [ "$(stat -c%s "$dest" 2>/dev/null||echo 0)" -gt 0 ]; then
    echo "[skip] $dest exists"; n_skip=$((n_skip+1)); continue
  fi
  echo "[get ] $id -> $dest"
  code=$(curl -sS "${AUTH[@]}" -o "$dest" -w '%{http_code}' "$url")
  if [ "$code" != "200" ] && [ "$code" != "206" ]; then
    echo "[FAIL] $id HTTP=$code $url"; n_fail=$((n_fail+1)); continue
  fi
  if [ "${sha:--}" != "-" ]; then
    exp=$(curl -sS "${AUTH[@]}" "$sha" | awk '{print $1}')
    got=$(sha256sum "$dest" | awk '{print $1}')
    if [ -n "$exp" ] && [ "$exp" != "$got" ]; then
      echo "[BADSUM] $dest exp=$exp got=$got"; n_badsum=$((n_badsum+1)); continue
    fi
    echo "[ok   ] $dest sha256 verified"
  fi
  n_ok=$((n_ok+1))
done < "$MANIFEST"
echo "=== summary: ok=$n_ok skip=$n_skip fail=$n_fail badsum=$n_badsum ==="
[ "$n_fail" -eq 0 ] && [ "$n_badsum" -eq 0 ]
