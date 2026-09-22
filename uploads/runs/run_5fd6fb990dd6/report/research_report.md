# MiroSense Research Report: demo_transit_policy

**Run ID:** `run_5fd6fb990dd6`  
**Created At:** 2026-09-03T15:47:54.470984  
**Requirement / Policy Query:** Predict how citizens and taxpayers will react to the fare-free weekend bus policy  

## 1. Executive Summary
- **Simulated Policy Acceptance:** `0.575`
- **Composite Polarization ($P_{total}$):** `0.683`
- **Network Modularity ($Q$):** `0.0`
- **Contestation / Conflict Rate:** `0.25`

## 2. Experimental Configuration & Evidence Grounding
- **Source Evidence Files:** 1 files ingested
  - `demo_transit_policy.md`
- **Total Simulation Rounds:** N/A
- **Simulated Agents:** 4

## 3. Opinion & Stance Dynamics
- **Mean Stance:** `+0.2500` (Range $[-1.0, 1.0]$)
- **Stance Standard Deviation:** `0.8292`
- **Support Ratio (> 0.1):** `50.00%`
- **Opposition Ratio (< -0.1):** `25.00%`
- **Neutral / Undecided Ratio:** `25.00%`

## 4. Community Structure & Modularity
- **Detected Sub-Communities:** `4`
- **Newman-Girvan Modularity ($Q$):** `0.0000`
- **Cross-Community Interaction Ratio:** `0.00%`

| Community ID | Size | Mean Stance | Internal Edges | External Edges |
| :--- | :---: | :---: | :---: | :---: |
| `comm_0` | 1 | `+0.00` | 0 | 0 |
| `comm_1` | 1 | `+1.00` | 0 | 0 |
| `comm_2` | 1 | `+1.00` | 0 | 0 |
| `comm_3` | 1 | `-1.00` | 0 | 0 |

## 5. Polarization Decomposition
Polarization is decomposed into three orthogonal structural and behavioral components:
$$P_{\text{total}} = w_{\text{opinion}} P_{\text{opinion}} + w_{\text{network}} P_{\text{network}} + w_{\text{interaction}} P_{\text{interaction}}$$

- **$P_{\text{total}}$ Composite:** `0.6830` (Moderate Polarization (Noticeable Factional Divergence))
- **$P_{\text{opinion}}$ (Stance Dispersion):** `0.9574`
- **$P_{\text{network}}$ (Graph Modularity):** `0.0000`
- **$P_{\text{interaction}}$ (Cross-Group Contestation):** `1.0000`

## 6. Simulated Network Influence (Top Agents)
- **Gini Inequality Index:** `0.0000`

| Agent ID | Role / Name | PageRank | In-Degree | Betweenness | Influence Rank |
| :--- | :--- | :---: | :---: | :---: | :---: |

## 7. Research Methodology & Scientific Limitations
- **Simulation Environment:** Agent interactions reflect OASIS simulated discourse conditioned on ingested documentation.
- **No Normative Optimality Claim:** Behavioral comparisons reflect simulated social responses, not absolute real-world truth.
- **Reproducibility:** All metrics are derived deterministically from canonical simulation events.
