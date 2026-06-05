# INFO-H512-LLMX_RAG: Forensic Workflows for Explainability Fidelity

This repository contains the software implementation for the **INFO-H512 - Current Trends in Artificial Intelligence** project. 

The project demonstrates a forensic workflow integrating the **FACILE** (Factorized Context Interactions for LLM Explainability) framework to shift the evaluation paradigm of Retrieval-Augmented Generation (RAG) systems from raw operational precision to **Explainability Fidelity (LLMX)**.

## Repository Structure

- `LLMX_AutoRAG.ipynb`: Contains the automated dual-LLM pipeline (Auditor and Judge) used for exhaustive anomaly detection and forensic verification across the document dataset.
- `LLMX_FACILE_EVAL.ipynb`: Contains the implementation of the FACILE arbitrator. It uses Weakly Supervised Shapley (WSS) sampling and a Factorization Machine (FM) surrogate to extract the mathematical interaction matrix ($F_{ij}$) and compute the causal attribution scores of the detected anomalies.

## Reproducibility Instructions

To reproduce the results discussed in the report, follow these steps:

### 1. Prerequisites
Ensure you have Python 3.10+ installed. You will need Jupyter Notebook or JupyterLab to run the `.ipynb` files.
You will also need an active API key for the LLMs used in the notebooks (e.g., OpenAI API key) if you intend to re-run the inference.

### 2. Environment Setup
Clone this repository and install the necessary dependencies:

```bash
git clone https://github.com/symoh27/INFO-H512-LLMX_RAG.git
cd INFO-H512-LLMX_RAG
pip install jupyter pandas numpy scikit-learn matplotlib seaborn
```
*Note: This implementation utilizes the `SHapRAG` package logic as outlined in the methodology.*

### 3. Step-by-Step Execution

#### Phase 1: Anomaly Detection and Verification
1. Open and run `LLMX_AutoRAG.ipynb`.
2. This notebook will ingest the target documents, run the exhaustive **Auditor LLM**, and filter out false positives using the **Judge LLM**.
3. The output of this notebook is a set of mathematically and logically sound alerts (`REAL_ANOMALY`).

#### Phase 2: Explainability Fidelity Evaluation (FACILE)
1. Open and run `LLMX_FACILE_EVAL.ipynb`.
2. This notebook loads the verified alerts from Phase 1.
3. It performs the `bf_kernelshap` sampling strategy and fits the Factorization Machine surrogate model to extract the Shapley values and the interaction matrix ($F_{ij}$).
4. The notebook generates the visualizations (such as the F-Matrix Heatmaps and the Global Attribution Score Distribution) directly proving the synergistic contradictions.

## License
MIT License