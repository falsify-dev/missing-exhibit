"""Figure 1 (written 14 Nov 2026): stage-2 outcome by branch, model and framing, with and without case D4."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
R = [json.loads(l) for l in open(os.path.join(HERE, "runs", "main.jsonl"))]
s2 = [r for r in R if r["stage"] == 2 and r["case"] != "D4"]
cells = [("claude-opus-5-5", False, "Opus\nplain"), ("claude-opus-5-5", True, "Opus\nlabel"),
         ("claude-sonnet-5-5", False, "Sonnet\nplain"), ("claude-sonnet-5-5", True, "Sonnet\nlabel")]
fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.8), sharey=True)
for ax, (br, want, title) in zip(axes, [("a", "SUPPORTED", "Supporting document (should flip to SUPPORTED)"),
                                         ("b", "REFUTED", "Refuting document (should flip to REFUTED)")]):
    xs = range(len(cells)); ok = []; und = []; oth = []
    for m, lab, _ in cells:
        rs = [r for r in s2 if r["model"] == m and r["label"] == lab and r["branch"] == br]
        n = len(rs)
        ok.append(sum(r["parsed"]["verdict"] == want for r in rs) / n)
        und.append(sum(r["parsed"]["verdict"] == "UNDETERMINED" for r in rs) / n)
        oth.append(1 - ok[-1] - und[-1])
    ax.bar(xs, ok, color="#2e8b57", label="correct update")
    ax.bar(xs, und, bottom=ok, color="#c9c9c9", label="still UNDETERMINED")
    ax.bar(xs, oth, bottom=[a + b for a, b in zip(ok, und)], color="#c0392b", label="opposite verdict")
    ax.set_xticks(list(xs)); ax.set_xticklabels([c[2] for c in cells], fontsize=8)
    ax.set_title(title, fontsize=8.5); ax.set_ylim(0, 1); ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    for i, v in enumerate(ok): ax.text(i, v / 2, f"{v:.0%}", ha="center", va="center", color="white", fontsize=8)
axes[0].legend(fontsize=7, loc="lower left")
fig.tight_layout()
os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
fig.savefig(os.path.join(HERE, "results", "figure1.png"), dpi=220)
# numbers for the text, excluding D4
for m, lab, name in cells:
    for br, want in (("a", "SUPPORTED"), ("b", "REFUTED")):
        rs = [r for r in s2 if r["model"] == m and r["label"] == lab and r["branch"] == br]
        print(name.replace("\n", " "), br, sum(r["parsed"]["verdict"] == want for r in rs), "/", len(rs))
