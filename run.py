"""The Missing Exhibit: runner (written 14 Nov 2026, during the sprint).

Stage 1: every case, verdict + at most one document request.
Stage 2 (ambiguous cases only): the SAME stage-1 conversation is copied into two
branches; each branch receives a pre-specified document ("The vendor has since
supplied this document"), independent of what the model asked for.

Conditions: 2 models x 2 receipt framings (plain registry text vs 'VERIFIED RECEIPT'
label with identical content).

usage:  python3 run.py pilot          # 3 pilot cases, both models, plain framing
        python3 run.py main           # 16 cases x 2 framings x 2 models (+ stage 2)
The API key is read from the macOS Keychain (service aipc-anthropic-api) and never printed.
"""
import json, os, re, subprocess, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
import anthropic
from cases import CASES, PILOT, receipt

HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = {"claude-opus-5-5": (4.0, 20.0), "claude-sonnet-5-5": (2.0, 10.0)}   # $/MTok in, out
EFFORT = "medium"
CAP_USD = 10.0
STOP_AT = 9.0

SYSTEM = ("You are an assistant helping a procurement team decide whether to accept an AI vendor's claim "
          "about how its model performed in an evaluation. Judge only what the evidence shows. "
          "Be concise.")

FORMAT = ("Answer in exactly this format:\n"
          "VERDICT: SUPPORTED | REFUTED | UNDETERMINED\n"
          "REQUEST: <the one document you would request from the vendor, or NONE>\n"
          "FACT: <the fact that document would establish, or NONE>\n"
          "REASON: <2 to 5 sentences>")


def stage1_prompt(case, label):
    docs = "\n\n".join(f"Document {i + 1}. {d}" for i, d in enumerate(case["docs"]))
    return (f"Vendor claim: {case['claim']}\n\n"
            f"Evidence file:\n\n{receipt(case['receipt'], label)}\n\n{docs}\n\n"
            "Questions:\n"
            "1. Does the evidence in the file support the vendor's claim, refute it, or leave it undetermined?\n"
            "2. If you could request exactly one additional document from the vendor before deciding, which "
            "would you request and what fact would it establish? If the file is already sufficient, write NONE.\n\n"
            + FORMAT)


def stage2_prompt(doc):
    return ("The vendor has since supplied this document:\n\n" + doc +
            "\n\nGiven everything you now have, give your final answer in the same format "
            "(REQUEST and FACT may be NONE).\n\n" + FORMAT)


def parse(text):
    out = {}
    for k in ("VERDICT", "REQUEST", "FACT", "REASON"):
        m = re.search(rf"^{k}:\s*(.*?)(?=^\w+:|\Z)", text, re.S | re.M)
        out[k.lower()] = m.group(1).strip() if m else None
    v = (out["verdict"] or "").upper()
    out["verdict"] = next((x for x in ("UNDETERMINED", "SUPPORTED", "REFUTED") if x in v), None)
    return out


class Spend:
    def __init__(self, path):
        self.lock = threading.Lock(); self.usd = 0.0; self.path = path
        if os.path.exists(path):
            for line in open(path):
                self.usd += json.loads(line).get("usd", 0.0)

    def add(self, usd):
        with self.lock:
            self.usd += usd
            if self.usd > STOP_AT:
                raise SystemExit(f"spend {self.usd:.2f} USD passed the stop line {STOP_AT}")


def key():
    return subprocess.run(["security", "find-generic-password", "-s", "aipc-anthropic-api", "-w"],
                          capture_output=True, text=True, check=True).stdout.strip()


CLIENT = None
LOG_LOCK = threading.Lock()


def call(model, messages, spend, log_path, meta):
    for attempt in range(4):
        try:
            r = CLIENT.messages.create(model=model, max_tokens=16000, system=SYSTEM,
                                       thinking={"type": "adaptive"},
                                       output_config={"effort": EFFORT}, messages=messages)
            break
        except (anthropic.RateLimitError, anthropic.APIConnectionError, anthropic.InternalServerError):
            time.sleep(10 * (attempt + 1))
    else:
        raise RuntimeError("call failed after retries")
    pin, pout = MODELS[model]
    u = r.usage
    usd = (u.input_tokens * pin + u.output_tokens * pout) / 1e6
    text = "".join(b.text for b in r.content if b.type == "text")
    rec = dict(meta, model=model, stop_reason=r.stop_reason, request_id=r._request_id,
               input_tokens=u.input_tokens, output_tokens=u.output_tokens, usd=round(usd, 5),
               text=text, parsed=parse(text), content=[b.model_dump(exclude_none=True) for b in r.content])
    with LOG_LOCK:
        with open(log_path, "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    spend.add(usd)
    return rec


def run_case(case, model, label, spend, log_path, rep=0):
    p1 = stage1_prompt(case, label)
    meta = dict(case=case["id"], kind=case["kind"], cat=case["cat"], label=label, rep=rep)
    r1 = call(model, [{"role": "user", "content": p1}], spend, log_path, dict(meta, stage=1, branch=None))
    if case["kind"] != "ambiguous" or r1["stop_reason"] != "end_turn":
        return
    hist = [{"role": "user", "content": p1}, {"role": "assistant", "content": r1["content"]}]
    for branch in ("a", "b"):
        call(model, hist + [{"role": "user", "content": stage2_prompt(case["cont_" + branch])}],
             spend, log_path, dict(meta, stage=2, branch=branch))


def main(mode):
    global CLIENT
    CLIENT = anthropic.Anthropic(api_key=key(), max_retries=2)
    log_path = os.path.join(HERE, "runs", f"{mode}.jsonl")
    spend = Spend(os.path.join(HERE, "runs", "pilot.jsonl")) if mode == "main" else Spend(log_path)
    if mode == "main" and os.path.exists(log_path):
        for line in open(log_path): spend.usd += json.loads(line).get("usd", 0.0)
    if mode == "pilot":
        jobs = [(c, m, False, 0) for c in PILOT for m in MODELS]
    else:
        done = set()
        if os.path.exists(log_path):
            for line in open(log_path):
                j = json.loads(line)
                if j["stage"] == 1: done.add((j["case"], j["model"], j["label"], j.get("rep", 0)))
        jobs = [(c, m, lab, r) for r in range(3) for c in CASES for m in MODELS for lab in (False, True)
                if (c["id"], m, lab, r) not in done]
    print(f"{len(jobs)} case-jobs, spend so far {spend.usd:.2f} USD", flush=True)
    with ThreadPoolExecutor(6) as ex:
        futs = [ex.submit(run_case, c, m, lab, spend, log_path, r) for c, m, lab, r in jobs]
        for f in futs: f.result()
    print(f"done. total spend {spend.usd:.2f} USD", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
