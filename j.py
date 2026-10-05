python - <<'PY'
import json

with open("response.json", encoding="utf-8-sig") as f:
    initiatives = json.load(f)

if not isinstance(initiatives, list):
    raise SystemExit("Expected the complete JSON array: [...]")

print(f"TOTAL RETURNED: {len(initiatives)}")
print(f"{'ID':<8} {'CREATOR':<9} {'ACTIVE':<7} TEAM_IDS")

for i in sorted(initiatives, key=lambda x: str(x.get("id", ""))):
    teams = i.get("teams")
    if isinstance(teams, list):
        team_ids = ",".join(sorted({
            str(t["team_id"])
            for t in teams
            if t.get("team_id") is not None
        })) or "-"
    else:
        team_ids = "MISSING"

    print(
        f"{str(i.get('id', '?')):<8} "
        f"{str(i.get('created_by_id', '?')):<9} "
        f"{str(i.get('is_active', '?')):<7} "
        f"{team_ids}"
    )
PY