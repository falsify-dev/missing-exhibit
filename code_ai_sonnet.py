"""AI coder 2 (Sonnet 5.5) for document requests; same rubric, blind (written 14 Nov 2026). Blind to model and framing.
Scores each stage-1 request against the case's missing fact: 2 targets it, 1 partly, 0 no."""
import csv, json, os, re
import anthropic
from run import key

HERE = os.path.dirname(os.path.abspath(__file__))
RUBRIC = ("You are coding a research dataset. For each item you see the fact that a reviewer is missing "
          "(the key) and the document a reviewer asked for, with the fact it would establish. Score:\n"
          "2 = the requested document would establish the missing fact (a different document that provides the "
          "same information also counts),\n1 = it would partly establish it, or only for part of the claim,\n"
          "0 = it would not establish it.\nReply with the score digit only.")
client = anthropic.Anthropic(api_key=key())
rows = list(csv.reader(open(os.path.join(HERE, "coding", "sheet.tsv")), delimiter="\t"))[1:]
out = []
usd = 0.0
for item, case, miss, req, fact, _ in rows:
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=2000, system=RUBRIC,
                               thinking={"type": "adaptive"}, output_config={"effort": "medium"},
                               messages=[{"role": "user", "content": f"Missing fact (key): {miss}\n\nRequested document: {req}\nFact it would establish: {fact}"}])
    t = "".join(b.text for b in r.content if b.type == "text")
    m = re.search(r"[012]", t)
    usd += (r.usage.input_tokens * 2 + r.usage.output_tokens * 10) / 1e6
    out.append(dict(item=int(item), case=case, ai_code=int(m.group()) if m else None))
json.dump(out, open(os.path.join(HERE, "coding", "ai-codes-sonnet.json"), "w"), indent=1)
print(len(out), "coded, spend", round(usd, 3), "USD")
