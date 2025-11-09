# DevOps Probes v1.4

## OPTIONS smoke (candidacies)
API=https://api.papsasinc.com/api
EID=$(curl -sS "$API/elections/current" | python -c "import sys,json; d=json.load(sys.stdin); print(d.get('id',''))")
curl -i -sS -X OPTIONS "$API/elections/$EID/candidacies" | sed -n '1,12p'

## Analytics read probe
curl -i -sS -H "Authorization: Bearer $OFFICER" "$API/elections/$EID/analytics" | head -n 12
