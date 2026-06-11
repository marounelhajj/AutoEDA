# AutoEDA

A Streamlit-based platform for automated exploratory data analysis and data preprocessing.

## Features

- **Dataset Overview** — shape, data types, missing values, and descriptive statistics at a glance
- **Data Exploration & Visualization** — distributions, scatter plots, categorical analysis, and correlation heatmaps
- **Feature Stability Analysis** — stability scoring for tabular data plus time-series drift detection
- **Data Preprocessing** — drop columns, handle missing values, encode categoricals, scale features, and manage outliers

## Getting Started

### Option 1 — Docker (recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop).

```bash
git clone https://github.com/marounelhajj/AutoEDA.git
cd AutoEDA
docker compose up --build
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

### Option 2 — Local Python

Requires Python 3.9+.

```bash
git clone https://github.com/marounelhajj/AutoEDA.git
cd AutoEDA
pip install -r requirements.txt
python -m streamlit run main.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage

1. Upload a CSV or Excel file via the sidebar, or enable **Use Example Titanic Dataset**.
2. Navigate between tabs using the top menu:
   - **Home** — project overview and quick-start button
   - **Data Exploration** — three sub-tabs: Dataset Overview, Exploration & Visualization, and Feature Stability
   - **Data Preprocessing** — interactive cleaning and transformation pipeline with a downloadable result

## Feature Stability

Each feature receives a stability score (0–100).

### Tabular Stability

| Label    | Score Range |
|----------|-------------|
| Stable   | > 80        |
| Moderate | 60 – 80     |
| Unstable | < 60        |

Numerical features are scored using missing rate, coefficient of variation, skewness, kurtosis, and outlier rate. Categorical features are scored using missing rate, entropy, cardinality, and mode frequency.

### Time-Series Stability

Detects data drift across sliding windows of the dataset. A time column can be selected, or rows are processed in order.

**Numerical drift** is measured with the KS statistic (vs. previous window) and PSI (vs. reference window):

| Label      | KS Range    |
|------------|-------------|
| Stable     | < 0.05      |
| Moderate   | 0.05 – 0.09 |
| Drifting   | 0.10 – 0.19 |
| High Drift | ≥ 0.20      |

**Categorical drift** is measured with Jensen–Shannon divergence:

| Label      | JS Range    |
|------------|-------------|
| Stable     | < 0.05      |
| Moderate   | 0.05 – 0.14 |
| Drifting   | 0.15 – 0.29 |
| High Drift | ≥ 0.30      |

## Project Structure

```
main.py                        # Streamlit entry point
home_page.py                   # Landing page content and CSS
data_analysis_functions.py     # Exploration and visualization logic
data_preprocessing_function.py # Preprocessing transformations
feature_stability_functions.py # Stability scoring and drift metrics
docs/                          # Sphinx documentation source
example_dataset/               # Bundled Titanic dataset
```

## Documentation

Full documentation is available in the `docs/` directory and can be built with Sphinx:

```bash
cd docs
make html
```

The rendered HTML lives in `_build/html/index.html`.

## File Size Limit

The uploader accepts files up to **1 GB**.
