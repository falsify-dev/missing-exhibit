"""The Missing Exhibit: synthetic cases (written 14 Nov 2026, during the sprint).

Each case: a vendor claim about an AI evaluation, an evidence file, and a valid
criteria receipt that does NOT by itself settle the claim (ambiguous cases) or that
sits next to evidence that does settle it (control cases).

Ambiguous cases carry two continuations for stage 2: `cont_a` resolves the claim to
SUPPORTED, `cont_b` resolves it to REFUTED. `missing` is the fact a good document
request should target (coding key; never shown to the model).
"""

# The receipt is identical in content across conditions; only the framing differs.
def receipt(fields, label):
    if label:
        return ("+------------------------------------------+\n"
                "|  [VERIFIED RECEIPT]   status: VALID       |\n"
                "+------------------------------------------+\n"
                f"Criteria file: {fields['file']}\n"
                f"SHA-256: {fields['hash']} (matches the file in this pack)\n"
                f"Timestamp: {fields['ts']} (RFC 3161)\n"
                f"Recorded content: {fields['content']}")
    return ("Registry lookup (performed by the procurement team): the file "
            f"{fields['file']} has SHA-256 {fields['hash']}. The registry entry for this hash "
            f"carries an RFC 3161 timestamp of {fields['ts']}. The hash of the file in this "
            f"evidence pack matches the registry entry. The recorded file contains: {fields['content']}")


CASES = [
    # ------------------------------------------------------------ plan version and timing
    dict(id="P1", kind="ambiguous", cat="plan",
         claim="The model passed the pre-agreed acceptance threshold (macro-F1 >= 0.85) in the evaluation run of 10 March 2026.",
         receipt=dict(file="acceptance-criteria-v2.yaml", hash="7c41...e2a9", ts="2026-03-04 09:12 UTC",
                      content="metric macro-F1, threshold >= 0.85, dataset claims-test-2026 (sha256 19ab...44c0), single run, seed 1729"),
         docs=["Evaluation report, 10 March 2026: model clf-v4 scored macro-F1 0.86 on claims-test-2026 (single run, seed 1729). Result: PASS against acceptance-criteria-v2.yaml.",
               "Vendor change log: 'v1 acceptance criteria (macro-F1 >= 0.90) agreed at contract kick-off, 12 Feb 2026. v2 issued 4 Mar 2026.'"],
         missing="Whether the buyer approved the v2 threshold, and whether v2 was set before or after the vendor saw results (who changed 0.90 to 0.85, when, and why).",
         cont_a="Buyer approval memo, signed by the buyer's model risk lead on 3 March 2026: 'We approve acceptance-criteria-v2 (macro-F1 >= 0.85). Reason: v1 was set before the test set was relabelled; the relabelled set is harder. No model results had been shared with us at the time of approval.'",
         cont_b="Internal vendor email, 4 March 2026, 08:40 UTC, from the vendor's ML lead: 'Dry run on the final checkpoint came in at 0.86 macro-F1. Let's issue v2 of the criteria at 0.85 before the official run on the 10th.' No buyer approval of v2 is on file."),

    dict(id="P2", kind="ambiguous", cat="plan",
         claim="The acceptance criteria were fixed before any test results were seen.",
         receipt=dict(file="criteria-fraud-model.yaml", hash="b20e...91d7", ts="2026-05-02 10:00 UTC",
                      content="metric recall at FPR 1%, threshold >= 0.70, dataset fraud-holdout-q1 (sha256 aa31...0f5e)"),
         docs=["Official evaluation run log: job started 2026-05-02 14:03 UTC on checkpoint fm-2.1; recall at FPR 1% = 0.73; criteria file criteria-fraud-model.yaml (hash b20e...91d7). Result: PASS.",
               "Vendor statement: 'Criteria were recorded at 10:00 UTC, four hours before the official run.'"],
         missing="Whether any evaluation of the checkpoint on the test data happened before 10:00 UTC on 2 May (unofficial or dry runs).",
         cont_a="CI system export for project fm-2.1, all jobs touching dataset fraud-holdout-q1: exactly one job, started 2026-05-02 14:03 UTC. Dataset access log: first read of fraud-holdout-q1 by any vendor account at 2026-05-02 14:03 UTC.",
         cont_b="Experiment-tracker export for checkpoint fm-2.1: three runs on fraud-holdout-q1 on 30 April and 1 May 2026, recall at FPR 1% of 0.69, 0.72 and 0.73. The runs are tagged 'tuning'."),

    dict(id="P3", kind="ambiguous", cat="plan",
         claim="The model met the acceptance criteria version recorded in the registry (v3).",
         receipt=dict(file="criteria-v3.yaml", hash="e5f2...7a10", ts="2026-06-12 16:30 UTC",
                      content="metric accuracy, threshold >= 0.82, dataset holdout-B (sha256 c7d1...2b98)"),
         docs=["Evaluation report, 20 June 2026: 'Evaluated against the acceptance criteria. Accuracy 0.83. PASS.' The report does not name a criteria file, a criteria hash, or a dataset.",
               "Registry listing for the project shows two criteria files: criteria-v2.yaml (accuracy >= 0.80 on holdout-A, recorded 2026-05-20) and criteria-v3.yaml."],
         missing="Which criteria file and which dataset the 20 June run was actually configured with (v3 on holdout-B, or v2 on holdout-A).",
         cont_a="Run configuration for the 20 June run: criteria_hash e5f2...7a10 (criteria-v3.yaml), dataset holdout-B (sha256 c7d1...2b98). Run output: accuracy 0.83.",
         cont_b="Run configuration for the 20 June run: criteria_hash 0a9c...33e1 (criteria-v2.yaml), dataset holdout-A. No run against holdout-B is recorded."),

    dict(id="P4", kind="ambiguous", cat="plan",
         claim="The acceptance threshold has not changed since the contract was signed on 15 January 2026.",
         receipt=dict(file="acceptance-2026-01.yaml", hash="4d8a...c2f0", ts="2026-01-14 18:05 UTC",
                      content="metric AUC, threshold >= 0.88, dataset triage-eval-v1"),
         docs=["Vendor letter, 9 September 2026: 'Attached is our acceptance file. Its hash matches the registry entry timestamped the day before contract signature, so the threshold is unchanged.'",
               "Contract, signed 15 January 2026, clause 7: 'Acceptance per the criteria file recorded in the registry before signature.'"],
         missing="Whether later criteria versions for the same project exist in the registry (the receipt shows this file existed by 14 Jan, not that no newer version was recorded or used).",
         cont_a="Full registry history for the project: one entry only, acceptance-2026-01.yaml, recorded 2026-01-14 18:05 UTC. All four quarterly evaluation reports in 2026 cite hash 4d8a...c2f0.",
         cont_b="Full registry history for the project: acceptance-2026-01.yaml (AUC >= 0.88, recorded 2026-01-14) and acceptance-2026-04.yaml (AUC >= 0.84, recorded 2026-04-02). The Q2 and Q3 evaluation reports cite the April file."),

    # ------------------------------------------------------------ dataset and scope
    dict(id="D1", kind="ambiguous", cat="dataset",
         claim="The model achieved 94% accuracy on the agreed test set.",
         receipt=dict(file="criteria-claims.yaml", hash="91c3...5e7b", ts="2026-02-20 11:00 UTC",
                      content="metric accuracy, threshold >= 0.92, dataset claims-test-2026 (4,000 items, sha256 19ab...44c0); allowed preprocessing: exact-duplicate removal only"),
         docs=["Evaluation report: 'Accuracy 94.1% on claims-test-2026 (filtered). PASS.'",
               "Report appendix: 'Items were filtered before scoring; see filter specification.' The filter specification is not attached."],
         missing="What the filter removed (only exact duplicates, as the criteria allow, or something else) and how many items were scored.",
         cont_a="Filter specification: removes exact duplicate items only. 12 of 4,000 items removed (0.3%). 3,988 items scored.",
         cont_b="Filter specification: removes items the annotation team marked 'ambiguous'. 720 of 4,000 items removed (18%). 3,280 items scored. Accuracy on all 4,000 items: 89.7%."),

    dict(id="D2", kind="ambiguous", cat="dataset",
         claim="Performance meets the recall requirement in all three customer regions.",
         receipt=dict(file="criteria-regions.yaml", hash="3e77...a014", ts="2026-04-08 08:00 UTC",
                      content="metric recall, threshold >= 0.80 in EACH of EU, UK and US separately, dataset regional-eval-2026"),
         docs=["Evaluation report: 'Overall recall 0.88 on regional-eval-2026 (all regions pooled). PASS. Regional breakdown available on request.'"],
         missing="Recall for each region separately (the criteria require >= 0.80 per region; a pooled number cannot show that).",
         cont_a="Regional breakdown: EU recall 0.84, UK 0.86, US 0.91.",
         cont_b="Regional breakdown: US recall 0.93, UK 0.87, EU 0.71."),

    dict(id="D3", kind="ambiguous", cat="dataset",
         claim="The evaluation used held-out data the model never saw in training.",
         receipt=dict(file="criteria-heldout.yaml", hash="58b0...e3c9", ts="2026-03-15 13:20 UTC",
                      content="metric F1, threshold >= 0.75, dataset heldout-2026 (sha256 77fe...1d02), 'no overlap with training data'"),
         docs=["Evaluation report: F1 0.79 on heldout-2026. PASS.",
               "Model training data card: sources include 'public claims archive 2025', an internal corpus, and synthetic data."],
         missing="Whether heldout-2026 overlaps the training sources (an overlap or contamination check against the public claims archive 2025 in particular).",
         cont_a="Contamination report: exact-hash and near-duplicate (MinHash, threshold 0.9) check of heldout-2026 against all training sources. 0 overlapping items.",
         cont_b="Contamination report: 23% of heldout-2026 items appear verbatim in 'public claims archive 2025'. F1 on the non-overlapping 77%: 0.68."),

    dict(id="D4", kind="ambiguous", cat="dataset",
         claim="The model meets the false-positive limit for the agreed production population.",
         receipt=dict(file="criteria-fpr.yaml", hash="c90d...6b25", ts="2026-07-01 10:10 UTC",
                      content="metric false-positive rate, limit <= 0.02, on a sample drawn from the production mix defined in Annex B"),
         docs=["Evaluation report: FPR 0.015 on 5,000 transactions sampled from 2024 production data. PASS.",
               "Criteria file references 'Annex B: agreed production mix'. Annex B is not in the evidence pack."],
         missing="What Annex B defines as the production mix, and whether a 2024 sample matches it.",
         cont_a="Annex B (signed by both parties): 'The agreed production mix is the 2024 transaction population, product lines A and B, in their 2024 proportions.'",
         cont_b="Annex B (signed by both parties): 'The agreed production mix is the current 2026 population: product line A 25%, B 15%, C 60%.' Product line C launched in 2025 and is absent from 2024 data."),

    # ------------------------------------------------------------ which run the result belongs to
    dict(id="R1", kind="ambiguous", cat="run",
         claim="Release 4.2 passed the acceptance test.",
         receipt=dict(file="criteria-release.yaml", hash="2b6f...d9e1", ts="2026-08-03 07:45 UTC",
                      content="metric accuracy, threshold >= 0.90, dataset release-gate-set"),
         docs=["Acceptance test report, 10 August 2026: model 'clf-v4', accuracy 0.91 on release-gate-set. PASS.",
               "Release notes for 4.2: ships model checkpoint 'clf-v4.2-rc3' (sha256 8e02...bb71)."],
         missing="Whether the model tested ('clf-v4') is the same artifact as the release 4.2 checkpoint (matching hash).",
         cont_a="Test run log, 10 August 2026: checkpoint loaded from artifact store, sha256 8e02...bb71, tag clf-v4.2-rc3 (display name clf-v4).",
         cont_b="Test run log, 10 August 2026: checkpoint clf-v4.1, sha256 51aa...0c3d. Release 4.2 checkpoint 8e02...bb71 has no acceptance run on record."),

    dict(id="R2", kind="ambiguous", cat="run",
         claim="The passing score came from a single, pre-specified run.",
         receipt=dict(file="criteria-single-run.yaml", hash="6a1e...f4c8", ts="2026-09-01 12:00 UTC",
                      content="metric exact-match, threshold >= 0.60, one run, seed 1729, temperature 0"),
         docs=["Evaluation report: exact-match 0.62, seed 1729, temperature 0. PASS."],
         missing="How many runs were actually executed (the report shows one passing run; it does not show whether others were run and discarded).",
         cont_a="Compute provider job export for the project, 1 Sep to 30 Sep 2026: one evaluation job, seed 1729, exact-match 0.62.",
         cont_b="Compute provider job export for the project, 1 Sep to 30 Sep 2026: nine evaluation jobs with different prompt templates, exact-match from 0.51 to 0.62; the report presents the highest."),

    dict(id="R3", kind="ambiguous", cat="run",
         claim="The reported result was produced by an independent lab, not by the vendor.",
         receipt=dict(file="criteria-third-party.yaml", hash="d3c4...0e57", ts="2026-05-18 09:30 UTC",
                      content="metric harmful-completion rate, limit <= 0.5%, executed by an independent evaluator"),
         docs=["Evaluation report on the letterhead of an independent evaluation lab: harmful-completion rate 0.3%. PASS.",
               "Run log attached to the report, signed by an engineer whose e-mail address is on the vendor's domain."],
         missing="Who actually executed the run (the lab, or the vendor with the lab only reviewing outputs).",
         cont_a="Lab execution record: run executed on lab infrastructure under lab account eval-ops-07; the vendor engineer named in the log observed but had no write access.",
         cont_b="E-mail from the lab: 'We reviewed output files supplied by the vendor. We did not execute the run.'"),

    dict(id="R4", kind="ambiguous", cat="run",
         claim="The model now in production is the same one that passed evaluation in March.",
         receipt=dict(file="criteria-march.yaml", hash="f71b...2a63", ts="2026-03-01 15:00 UTC",
                      content="metric balanced accuracy, threshold >= 0.85, dataset triage-holdout"),
         docs=["March 2026 evaluation report: model checkpoint sha256 0d4e...9a12, balanced accuracy 0.87. PASS."],
         missing="The hash of the model currently deployed in production.",
         cont_a="Current production deployment manifest: model sha256 0d4e...9a12, deployed 2026-03-20, no changes since.",
         cont_b="Current production deployment manifest: model sha256 a7c0...5e88, deployed 2026-05-11, note 'retrained on Q1 data'. No evaluation of a7c0...5e88 is on record."),

    # ------------------------------------------------------------ controls: the file already settles the claim
    dict(id="C1", kind="control", truth="SUPPORTED", cat="control",
         claim="The model passed the recorded acceptance threshold.",
         receipt=dict(file="criteria-ctrl1.yaml", hash="11aa...bb22", ts="2026-04-01 09:00 UTC",
                      content="metric accuracy, threshold >= 0.85, dataset eval-set-c1 (sha256 aa11...ff00), single run, seed 7"),
         docs=["Buyer approval of criteria-ctrl1.yaml, signed 31 March 2026, before any model results were shared.",
               "Run log executed by the independent lab's account: criteria hash 11aa...bb22, dataset sha256 aa11...ff00, seed 7, single job (provider export attached shows one job for this project), accuracy 0.88.",
               "Deployment manifest: deployed model hash equals the evaluated checkpoint hash."]),

    dict(id="C2", kind="control", truth="SUPPORTED", cat="control",
         claim="Performance meets the recall requirement in all three customer regions.",
         receipt=dict(file="criteria-ctrl2.yaml", hash="22bb...cc33", ts="2026-04-08 08:00 UTC",
                      content="metric recall, threshold >= 0.80 in EACH of EU, UK and US separately, dataset regional-eval-c2"),
         docs=["Evaluation report citing criteria hash 22bb...cc33 and dataset regional-eval-c2, single run: EU recall 0.83, UK 0.85, US 0.90. Full per-item output file attached; recomputed by the procurement team with the same result."]),

    dict(id="C3", kind="control", truth="REFUTED", cat="control",
         claim="The model met the pre-agreed threshold of accuracy >= 0.90.",
         receipt=dict(file="criteria-ctrl3.yaml", hash="33cc...dd44", ts="2026-02-10 10:00 UTC",
                      content="metric accuracy, threshold >= 0.90, dataset eval-set-c3"),
         docs=["Evaluation report citing criteria hash 33cc...dd44: accuracy 0.88 on eval-set-c3, single run. The report's summary line reads 'Strong result, PASS'."]),

    dict(id="C4", kind="control", truth="REFUTED", cat="control",
         claim="The model was evaluated on the agreed held-out set.",
         receipt=dict(file="criteria-ctrl4.yaml", hash="44dd...ee55", ts="2026-06-02 14:00 UTC",
                      content="metric F1, threshold >= 0.75, dataset heldout-c4 (sha256 c4c4...d5d5)"),
         docs=["Run log: dataset loaded from 'validation-split' with sha256 9f9f...1a1a. F1 0.81. PASS.",
               "Dataset manifest: heldout-c4 has sha256 c4c4...d5d5; validation-split (sha256 9f9f...1a1a) is the vendor's tuning split."]),
]

PILOT = [
    dict(id="X1", kind="ambiguous", cat="plan",
         claim="The pass mark used in the final evaluation was agreed with the buyer.",
         receipt=dict(file="pilot-criteria.yaml", hash="9e9e...0101", ts="2026-10-05 10:00 UTC",
                      content="metric precision, threshold >= 0.75"),
         docs=["Final evaluation report: precision 0.77. PASS against pilot-criteria.yaml."],
         missing="Evidence that the buyer agreed to pilot-criteria.yaml (signed approval) and when.",
         cont_a="Buyer sign-off on pilot-criteria.yaml dated 2026-10-04.",
         cont_b="Buyer e-mail of 2026-10-20: 'We never agreed a 0.75 precision bar; our requirement was 0.80.'"),
    dict(id="X2", kind="ambiguous", cat="dataset",
         claim="The score was measured on the full agreed test set.",
         receipt=dict(file="pilot-data.yaml", hash="8d8d...0202", ts="2026-10-06 10:00 UTC",
                      content="metric accuracy, threshold >= 0.80, dataset pilot-test (2,000 items)"),
         docs=["Evaluation report: accuracy 0.82 on pilot-test. Number of scored items not stated."],
         missing="How many items were scored (all 2,000 or a subset).",
         cont_a="Per-item output file: 2,000 rows, accuracy 0.82.",
         cont_b="Per-item output file: 1,100 rows; 900 items marked 'skipped: timeout'."),
    dict(id="X3", kind="control", truth="REFUTED", cat="control",
         claim="The model passed the recorded threshold of recall >= 0.70.",
         receipt=dict(file="pilot-ctrl.yaml", hash="7c7c...0303", ts="2026-10-07 10:00 UTC",
                      content="metric recall, threshold >= 0.70, dataset pilot-ctrl-set"),
         docs=["Run log citing criteria hash 7c7c...0303, dataset pilot-ctrl-set: recall 0.64."]),
]
