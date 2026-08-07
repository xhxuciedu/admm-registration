#!/usr/bin/env bash
set -euo pipefail
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
download_dir="$repo_dir/data/downloads"
raw_dir="$repo_dir/data/raw/fire"
mkdir -p "$download_dir" "$raw_dir"
# The official server currently presents an incomplete TLS chain; -k is scoped
# to this documented official URL. The SHA256 is recorded after download.
curl -k -L --fail --retry 20 --retry-all-errors --retry-delay 5 -C - \
  -o "$download_dir/FIRE.7z" "https://projects.ics.forth.gr/cvrl/fire/FIRE.7z"
# A completed HTTP transfer is not sufficient: reject corrupt range resumes.
7z t "$download_dir/FIRE.7z"
sha256sum "$download_dir/FIRE.7z" > "$download_dir/FIRE.7z.sha256"
7z x -y -o"$raw_dir" "$download_dir/FIRE.7z"
find "$raw_dir" -maxdepth 3 -type f | sort > "$download_dir/FIRE.files.txt"
