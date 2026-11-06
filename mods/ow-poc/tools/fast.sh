#!/bin/bash
# One command: regenerate the data (optional), validate it, build the mod object, deploy it into the game dir, and (optional) run scenarios.
#   mods/ow-poc/tools/fast.sh                      validate + build + deploy
#   mods/ow-poc/tools/fast.sh --convert            also re-run dk_to_journey.py first (the story JSON is generated from journey_content/)
#   mods/ow-poc/tools/fast.sh dk_part2_bench ...   then run those smoke scenarios
#   mods/ow-poc/tools/fast.sh --quick             critical-path suite only (gates, wagers, chapter jumps)
#   mods/ow-poc/tools/fast.sh all                 every scenario (slow)
# Environment: JM_GAME (game dir, default tmp/pc/game32), JM_CONTENT is read by the converter.  Run it from anywhere.
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"; MOD="$(dirname "$HERE")"; REPO="$(cd "$MOD/../.." && pwd)"
GAME="${JM_GAME:-$REPO/tmp/pc/game32}"
cd "$REPO"
t0=$(date +%s%N); lap() { t1=$(date +%s%N); printf '  %-9s %5d ms\n' "$1" $(( (t1 - t0) / 1000000 )); t0=$t1; }
if [ "$1" = "--convert" ]; then shift; python3 "$HERE/dk_to_journey.py" | tail -1; lap convert; fi
python3 "$HERE/validate_story.py" | tail -3; lap validate
python3 tools/pc/build_mod.py --target i386 mods/ow-poc 2>&1 | tail -1; lap build
D="$GAME/mods/ow-poc"; mkdir -p "$D"
cp "$MOD/ow-poc.o" "$MOD/mod.json" "$D/"
# only what changed (-u): the assets are big, a deploy of a script change takes a moment
cp -ru "$MOD/assets/." "$D/assets/" 2>/dev/null || { mkdir -p "$D/assets"; cp -ru "$MOD/assets/." "$D/assets/"; }
mkdir -p "$D/duelists"; cp -u "$MOD"/duelists/*.json "$D/duelists/" 2>/dev/null || true
lap deploy
if [ $# -gt 0 ]; then
  if [ "$1" = "all" ]; then python3 "$HERE/smoke/jm_smoke.py" all
  elif [ "$1" = "--quick" ] || [ "$1" = "quick" ]; then python3 "$HERE/smoke/jm_smoke.py" quick
  else python3 "$HERE/smoke/jm_smoke.py" run "$@"; fi
  lap smoke
fi
