# SPECTRA Defense Questions Template

Use this document to prepare concise answers supported by repository
evidence.

## Answer Framework

For each question:

1. Answer directly in one sentence.
2. Explain the engineering reason.
3. Cite implementation or validation evidence.
4. State the applicable limitation.

## Project Scope

### Q1. What engineering problem does SPECTRA solve?

**Short answer:**

**Evidence:**

**Limitation:**

### Q2. Why is SPECTRA receive only?

**Short answer:**

**Evidence:**

**Limitation:**

### Q3. Is SPECTRA a cognitive radio?

**Short answer:**

**Evidence:**

**Limitation:**

Recommended distinction: SPECTRA provides deterministic RF survey and
decision support; it does not autonomously access spectrum or transmit.

## SDR and DSP

### Q4. Why did you choose RTL-SDR?

**Short answer:**

**Tradeoff:**

### Q5. Why apply a Hann window?

**Short answer:**

**Validation evidence:**

### Q6. What do the displayed power values mean?

**Short answer:**

**Limitation:**

### Q7. How is the frequency axis calculated?

**Short answer:**

**Evidence:**

### Q8. What does spectral-bin occupancy represent?

**Short answer:**

**What it does not represent:**

## Detection

### Q9. How does the Adaptive Detector work?

**Short answer:**

**Evidence:**

**Limitation:**

### Q10. Why was OS-CFAR not selected for production?

**Short answer:**

**Evidence:**

**Limitation:**

### Q11. Why do detector reports often contain three peaks?

**Short answer:**

**Metric limitation:**

### Q12. Can you state detector accuracy or probability of detection?

**Short answer:**

**Required future experiment:**

## Survey and SMART

### Q13. How do you ensure a measurement uses the correct tuned frequency?

**Short answer:**

**Implementation evidence:**

### Q14. What makes SMART explainable?

**Short answer:**

**Evidence:**

### Q15. Is SMART artificial intelligence?

**Short answer:**

Recommended answer: No. SMART is deterministic weighted heuristic scoring
with visible component scores and ranking.

### Q16. What does score separation mean?

**Short answer:**

**What it does not mean:**

### Q17. Why can the recommendation change between surveys?

**Short answer:**

**Evidence:**

## Validation

### Q18. Why use immutable IQ replay?

**Short answer:**

**Evidence:**

### Q19. What did the nine REAL-RF datasets prove?

**Short answer:**

**What they did not prove:**

### Q20. How did you prevent the detector comparison from being biased?

**Short answer:**

**Evidence:**

### Q21. Why are synthetic and hardware validation both necessary?

**Short answer:**

**Tradeoff:**

## Architecture and Reliability

### Q22. Why is SDR acquisition in a worker thread?

**Short answer:**

**Evidence:**

### Q23. What is the weakest architectural area?

**Short answer:**

**Why it was not refactored before release:**

### Q24. How is clean shutdown handled?

**Short answer:**

**Evidence:**

### Q25. How reproducible is the software environment?

**Short answer:**

**Evidence:**

## Limitations and Future Work

### Q26. What is the most important limitation?

**Short answer:**

**Mitigation:**

### Q27. What single experiment would add the most engineering value?

**Short answer:**

**Expected evidence:**

### Q28. What would you change with another semester?

**Short answer:**

**Priority justification:**

## Evidence Quick Reference

| Topic | Primary evidence |
|---|---|
| Requirements | `docs/REQUIREMENTS_TRACEABILITY_MATRIX.md` |
| Validation claims | `docs/VALIDATION_EVIDENCE_INDEX.md` |
| REAL-RF campaign | `docs/REAL_RF_VALIDATION_CAMPAIGN_REPORT.md` |
| Detector decision | `docs/detection_engine_final_assessment.md` |
| Release verification | `docs/RELEASE_CANDIDATE_VERIFICATION_REPORT.md` |
| Limitations | `SPECTRA_RELEASE/documentation/LIMITATIONS.md` |

## Additional Committee Questions

| Question | One-sentence answer | Evidence | Limitation |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
