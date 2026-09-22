# MiroSense — Research Methodology & Mathematical Foundations

This document provides the formal mathematical definitions, algorithms, and analytical methodologies implemented in **MiroSense**.

---

## 1. Interaction Graph & Topological Centrality

The interaction network is modeled as a directed Multi-Graph $G = (V, E, W)$, where:
- $V = \{a_1, a_2, \dots, a_N\}$ represents simulated stakeholder agents.
- $E \subseteq V \times V$ represents directed social interactions (replies, reposts, likes, disagreements, endorsements).
- $W: E \to \mathbb{R}^+$ assigns interaction weights based on frequency and interaction types.

### Density & Reciprocity
- **Network Density ($D$):**
  $$D = \frac{|E|}{|V|(|V| - 1)}$$
- **Reciprocity ($R$):**
  $$R = \frac{\sum_{u \neq v} \min(w_{uv}, w_{vu})}{\sum_{u \neq v} w_{uv}}$$

### Centrality Metrics
- **PageRank:**
  $$PR(u) = \frac{1 - d}{|V|} + d \sum_{v \in \mathcal{N}_{\text{in}}(u)} \frac{PR(v)}{\text{deg}_{\text{out}}(v)}$$
  where $d = 0.85$ is the damping factor.
- **Betweenness Centrality:**
  $$C_B(u) = \sum_{s \neq u \neq t} \frac{\sigma_{st}(u)}{\sigma_{st}}$$

---

## 2. Community Detection & Modularity Optimization

Communities $\mathcal{C} = \{C_1, C_2, \dots, C_K\}$ are detected deterministically using the Louvain modularity maximization algorithm with a fixed seed:

### Newman-Girvan Modularity ($Q$):
$$Q = \frac{1}{2m} \sum_{i,j} \left[ A_{ij} - \frac{k_i k_j}{2m} \right] \delta(c_i, c_j)$$
where:
- $A_{ij}$ is the adjacency weight between agents $i$ and $j$.
- $k_i = \sum_j A_{ij}$ is the degree of agent $i$.
- $m = \frac{1}{2} \sum_{ij} A_{ij}$ is the total edge weight.
- $\delta(c_i, c_j) = 1$ if agents $i$ and $j$ belong to the same community, $0$ otherwise.

### Cross-Community Interaction Ratio:
$$\text{CCIR} = \frac{\sum_{i, j \text{ s.t. } c_i \neq c_j} A_{ij}}{\sum_{i, j} A_{ij}}$$

---

## 3. Opinion Dynamics & Stance Dispersion

Each agent action $e_k$ is mapped to a continuous policy stance $s(e_k) \in [-1.0, +1.0]$:
- $+1.0$: Strong support for the proposed policy.
- $0.0$: Neutral, undecided, or purely informational.
- $-1.0$: Strong opposition or criticism.

### Metrics:
- **Mean Stance ($\mu_s$):**
  $$\mu_s = \frac{1}{|E_{\text{eval}}|} \sum_{e \in E_{\text{eval}}} s(e)$$
- **Stance Standard Deviation ($\sigma_s$):**
  $$\sigma_s = \sqrt{\frac{1}{|E_{\text{eval}}| - 1} \sum_{e \in E_{\text{eval}}} (s(e) - \mu_s)^2}$$
- **Simulated Policy Acceptance ($A$):**
  $$A = 0.60 \times \left( \frac{\mu_s + 1}{2} \right) + 0.40 \times \frac{|\{e \mid s(e) > 0.10\}|}{|E_{\text{eval}}|}$$
- **Cohesion / Agreement ($C$):**
  $$C = 1.0 - \min(1.0, \sigma_s)$$

---

## 4. Tri-Part Polarization Model

Polarization is evaluated as a composite across continuous opinion variance, graph topological modularity, and cross-group interaction contestation:

$$P_{\text{total}} = w_{\text{opinion}} P_{\text{opinion}} + w_{\text{network}} P_{\text{network}} + w_{\text{interaction}} P_{\text{interaction}}$$

Default weights: $w_{\text{opinion}} = 0.40$, $w_{\text{network}} = 0.30$, $w_{\text{interaction}} = 0.30$.

1. **Opinion Polarization ($P_{\text{opinion}}$):**
   $$P_{\text{opinion}} = \min(1.0, \sigma_s)$$
2. **Network Polarization ($P_{\text{network}}$):**
   $$P_{\text{network}} = \max(0.0, \min(1.0, Q))$$
3. **Interaction Polarization ($P_{\text{interaction}}$):**
   $$P_{\text{interaction}} = 1.0 - \text{CCIR}$$

---

## 5. Statistical Effect Size (Cohen's $d$ & Hedges' $g$)

When comparing candidate scenario $B$ against baseline scenario $A$:

### Cohen's $d$:
$$d = \frac{\bar{x}_B - \bar{x}_A}{s_{\text{pooled}}}$$
$$s_{\text{pooled}} = \sqrt{\frac{(n_A - 1)s_A^2 + (n_B - 1)s_B^2}{n_A + n_B - 2}}$$

### Effect Size Interpretation:
- $|d| < 0.20$: Negligible
- $0.20 \le |d| < 0.50$: Small
- $0.50 \le |d| < 0.80$: Medium
- $|d| \ge 0.80$: Large

---

## 6. Uncertainty Quantification (Student-$t$ 95% Confidence Interval)

For $N$ stochastic simulation trials with sample mean $\bar{x}$ and sample standard deviation $s$:

$$\text{CI}_{95\%} = \left[ \bar{x} - t_{0.975, N-1} \cdot \frac{s}{\sqrt{N}}, \quad \bar{x} + t_{0.975, N-1} \cdot \frac{s}{\sqrt{N}} \right]$$

where $t_{0.975, \nu}$ is the exact Student-$t$ critical value with $\nu = N - 1$ degrees of freedom.
