"""The Missing Exhibit: analysis (written 14 Nov 2026). Reads runs/main.jsonl, writes results/*.
Counts are reported with denominators; with 12 ambiguous cases no significance claims are made."""
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results"); os.makedirs(OUT, exist_ok=True)
R = [json.loads(l) for l in open(os.path.join(HERE, "runs", "main.jsonl"))]
M = {"claude-opus-5-5": "Opus 5.5", "claude-sonnet-5-5": "Sonnet 5.5"}
L = {False: "plain", True: "label"}
cells = [(m, lab) for m in M for lab in (False, True)]
lines = []


def P(s=""):
    lines.append(s); print(s)


def frac(a, b):
    return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "0/0"


s1 = [r for r in R if r["stage"] == 1]
s2 = [r for r in R if r["stage"] == 2]
P(f"calls: {len(R)} (stage 1: {len(s1)}, stage 2: {len(s2)}); spend {sum(r['usd'] for r in R):.2f} USD")
P(f"stop reasons: {dict(collections.Counter(r['stop_reason'] for r in R))}")
P(f"unparsed verdicts: {sum(1 for r in R if not r['parsed']['verdict'])}")
P()

P("Table 1. Stage 1 on AMBIGUOUS cases (12 cases x 3 repetitions per cell)")
P("cell                 SUPPORTED (error)   REFUTED (over-commit)   UNDETERMINED (correct)   asked for a document")
t1 = {}
for m, lab in cells:
    rs = [r for r in s1 if r["kind"] == "ambiguous" and r["model"] == m and r["label"] == lab]
    c = collections.Counter(r["parsed"]["verdict"] for r in rs)
    ask = sum(1 for r in rs if (r["parsed"]["request"] or "NONE").strip().upper() != "NONE")
    t1[(m, lab)] = (c, len(rs), ask)
    P(f"{M[m]:10} {L[lab]:6}   {frac(c['SUPPORTED'], len(rs)):18}  {frac(c['REFUTED'], len(rs)):22}  {frac(c['UNDETERMINED'], len(rs)):23}  {frac(ask, len(rs))}")
P()

P("Table 2. Stage 1 on CONTROL cases (4 cases x 3 repetitions per cell; correct = the verdict the file settles)")
truth = {"C1": "SUPPORTED", "C2": "SUPPORTED", "C3": "REFUTED", "C4": "REFUTED"}
for m, lab in cells:
    rs = [r for r in s1 if r["kind"] == "control" and r["model"] == m and r["label"] == lab]
    ok = sum(1 for r in rs if r["parsed"]["verdict"] == truth[r["case"]])
    und = sum(1 for r in rs if r["parsed"]["verdict"] == "UNDETERMINED")
    P(f"{M[m]:10} {L[lab]:6}   correct {frac(ok, len(rs)):14}  needless UNDETERMINED {frac(und, len(rs))}")
P()

P("Table 3. Stage 2 update after a pre-specified document (branch a should give SUPPORTED, b REFUTED)")
for m, lab in cells:
    out = []
    for br, want in (("a", "SUPPORTED"), ("b", "REFUTED")):
        rs = [r for r in s2 if r["model"] == m and r["label"] == lab and r["branch"] == br]
        ok = sum(1 for r in rs if r["parsed"]["verdict"] == want)
        und = sum(1 for r in rs if r["parsed"]["verdict"] == "UNDETERMINED")
        out.append(f"{br}: correct {frac(ok, len(rs))}, still UNDETERMINED {und}")
    P(f"{M[m]:10} {L[lab]:6}   " + " | ".join(out))
P()

P("Table 4. Stage 1 ambiguous verdicts by case (all cells and repetitions pooled; S/R/U counts out of 12)")
for cid in sorted({r["case"] for r in s1 if r["kind"] == "ambiguous"}):
    rs = [r for r in s1 if r["case"] == cid]
    c = collections.Counter(r["parsed"]["verdict"] for r in rs)
    P(f"{cid}: S {c['SUPPORTED']:2}  R {c['REFUTED']:2}  U {c['UNDETERMINED']:2}")
P()

P("Stability: share of (case, model, framing) cells whose stage-1 verdict was identical in all 3 repetitions")
g = collections.defaultdict(list)
for r in s1: g[(r["case"], r["model"], r["label"])].append(r["parsed"]["verdict"])
same = sum(1 for v in g.values() if len(set(v)) == 1)
P(frac(same, len(g)))
P()

P("Tokens: mean output tokens per stage-1 call")
for m in M:
    rs = [r for r in s1 if r["model"] == m]
    P(f"{M[m]}: {sum(r['output_tokens'] for r in rs) / len(rs):.0f}")

open(os.path.join(OUT, "tables.txt"), "w").write("\n".join(lines) + "\n")

# coding sheet: stage-1 ambiguous requests, blind (no model, no framing), shuffled deterministically
import random
from cases import CASES
miss = {c["id"]: c["missing"] for c in CASES if c["kind"] == "ambiguous"}
rows = [r for r in s1 if r["kind"] == "ambiguous"]
random.Random(1729).shuffle(rows)
key = []
with open(os.path.join(HERE, "coding", "sheet.tsv"), "w") as f:
    f.write("item\tcase\tmissing_fact (key)\tREQUEST\tFACT\tcode (2 = targets the missing fact, 1 = partly, 0 = no)\n")
    for i, r in enumerate(rows):
        f.write(f"{i + 1}\t{r['case']}\t{miss[r['case']]}\t{(r['parsed']['request'] or '').replace(chr(9), ' ').replace(chr(10), ' ')}\t{(r['parsed']['fact'] or '').replace(chr(9), ' ').replace(chr(10), ' ')}\t\n")
        key.append(dict(item=i + 1, case=r["case"], model=r["model"], label=r["label"], rep=r["rep"]))
json.dump(key, open(os.path.join(HERE, "coding", "key.json"), "w"), indent=1)
print("coding sheet:", len(rows), "items")
