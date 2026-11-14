# The Missing Exhibit

AI x Epistemics Research Sprint (Apart Research), 13 to 15 November 2026. Track 2: Trust Infrastructure.

**Question:** when an AI agent reviews a vendor's evaluation claim, does it notice the evidence that is missing, ask for the document that would settle the claim, and update correctly once that document arrives? And does a "verified receipt" label on a valid but non-decisive record make it more willing to accept the claim?

## What is new and what is preexisting

| Item | Status |
|---|---|
| Study design note (5 Nov 2026, not in this repository) | **Preexisting.** Written before the sprint; no cases, prompts or code. |
| PRML specification and the falsify tools by the same author | **Preexisting**, and **not used** by this study. The cases are synthetic and do not need PRML. |
| `cases.py`, `run.py`, `analyze.py`, all prompts, all results | **New**, written during the sprint (14 Nov 2026). |

## Reproduce

```
pip install anthropic
export ANTHROPIC_API_KEY=...      # run.py reads the key from the macOS Keychain; replace key() to use the env var
python3 run.py pilot            # 3 pilot cases
python3 run.py main             # 16 cases x 2 framings x 2 models x 3 repetitions, with stage 2
python3 analyze.py              # tables -> results/tables.txt, blind coding sheet -> coding/sheet.tsv
```

Models: `claude-opus-5-5` and `claude-sonnet-5-5`, adaptive thinking, effort `medium` for both, no sampling parameters. Raw responses with request IDs and token counts are in `runs/`.

## Files

- `cases.py`: the 16 cases (12 ambiguous, 4 control) and 3 pilot cases, with missing-fact keys and follow-up documents.
- `run.py`: stage 1 and stage 2 runner. `runs/main.jsonl` holds every response with request ID, token counts and cost.
- `analyze.py`, `figure.py`: tables (`results/tables.txt`) and Figure 1.
- `code_ai.py`, `code_ai_sonnet.py`: the two AI coders of document requests. `coding/sheet.tsv` is the blind sheet; `coding/key.json` maps items to model and framing. No human coding was done.
- `report/MissingExhibit.pdf`: the sprint report.

## Conflict of interest

The author maintains PRML, an open specification for evaluation records, and Falsify OÜ offers paid services for preparing and reviewing them. The study uses synthetic cases, does not require PRML to reproduce, and measures how agents interpret evidence, not whether anyone should adopt a particular tool.
