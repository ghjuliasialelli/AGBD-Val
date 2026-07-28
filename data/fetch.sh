#!/usr/bin/env bash
# Serial, resumable downloader for the AGB reference data (playbook: serialise heavy jobs,
# resume, skip-if-valid, loud on failure). Reads a TSV manifest: id \t url \t dest \t expected_bytes
# Usage: fetch.sh <manifest.tsv>   [env: NETRC=1 to pass --netrc for Earthdata-gated URLs]
set -u
cd "$(dirname "$0")" || exit 2
MANIFEST="${1:?usage: fetch.sh manifest.tsv}"
LOG="download_$(basename "$MANIFEST" .tsv).log"
WGET_AUTH=""
[ "${NETRC:-0}" = "1" ] && WGET_AUTH="--netrc"

# read line-by-line WITHOUT the last-line-skip trap: append a newline via `|| [ -n "$line" ]`
n_ok=0; n_skip=0; n_fail=0
while IFS=$'\t' read -r id url dest exp || [ -n "$id" ]; do
  [ -z "$id" ] && continue
  case "$id" in \#*) continue;; esac
  mkdir -p "$(dirname "$dest")"
  # skip-if-valid: exists and (no expected size OR within 1% of expected)
  if [ -f "$dest" ]; then
    have=$(stat -c%s "$dest" 2>/dev/null || echo 0)
    if [ "${exp:-0}" -eq 0 ] 2>/dev/null; then
      if [ "$have" -gt 0 ]; then echo "[skip] $dest ($have B, exists)"; n_skip=$((n_skip+1)); continue; fi
    else
      lo=$(( exp * 99 / 100 ))
      if [ "$have" -ge "$lo" ]; then echo "[skip] $dest ($have B >= ${lo} B)"; n_skip=$((n_skip+1)); continue; fi
    fi
  fi
  echo "[get ] $id -> $dest  (expect ~${exp} B)"
  if wget $WGET_AUTH -c -q --show-progress --tries=3 --timeout=60 -O "$dest" "$url"; then
    have=$(stat -c%s "$dest" 2>/dev/null || echo 0)
    echo "[done] $dest ($have B)"; n_ok=$((n_ok+1))
  else
    echo "[FAIL] $id $url (exit $?)"; n_fail=$((n_fail+1))
  fi
done < "$MANIFEST"
echo "=== summary: ok=$n_ok skip=$n_skip fail=$n_fail ==="
[ "$n_fail" -eq 0 ]
