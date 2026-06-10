import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats


def _outlier_rate_iqr(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    n_outliers = ((series < lower) | (series > upper)).sum()
    return round((n_outliers / len(series)) * 100, 2)


def _stability_score_numerical(missing_rate, cv, skewness, kurtosis, outlier_rate):
    score = 100.0
    score -= min(missing_rate * 0.5, 30)          # up to -30
    if not (np.isnan(cv) or np.isinf(cv)):
        score -= min(abs(cv) * 10, 25)            # up to -25
    else:
        score -= 25
    score -= min(abs(skewness) * 5, 20)           # up to -20
    score -= min(abs(kurtosis) * 1.5, 15)         # up to -15
    score -= min(outlier_rate * 0.5, 10)          # up to -10
    return round(max(0.0, score), 1)


def _stability_score_categorical(missing_rate, cardinality, mode_freq, normalized_entropy):
    score = 100.0
    score -= min(missing_rate * 0.5, 30)
    score -= min(cardinality * 0.3, 30)
    if mode_freq > 80:
        score -= min((mode_freq - 80) * 1.0, 20)
    score -= min((1 - normalized_entropy) * 20, 20)
    return round(max(0.0, score), 1)


def _stability_label(score):
    if score >= 80:
        return "Stable"
    elif score >= 60:
        return "Moderate"
    elif score >= 40:
        return "Unstable"
    else:
        return "Highly Unstable"


@st.cache_data
def compute_numerical_stability(df, num_columns):
    """Compute stability metrics for all numerical columns.

    For each column the following statistics are calculated: missing rate,
    coefficient of variation, skewness, excess kurtosis, and IQR-based
    outlier rate. These feed into a composite **Stability Score** (0–100)
    and a categorical **Stability** label.

    Scoring penalties (max deductions):

    * Missing rate  → up to −30 pts
    * Coeff. of variation → up to −25 pts
    * Skewness → up to −20 pts
    * Kurtosis → up to −15 pts
    * Outlier rate → up to −10 pts

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset to analyse.
    num_columns : list of str
        Numerical column names to include.

    Returns
    -------
    pandas.DataFrame
        One row per column with the columns: ``Feature``,
        ``Missing Rate (%)``, ``Coeff. of Variation``, ``Skewness``,
        ``Kurtosis (excess)``, ``Outlier Rate (%)``, ``Stability Score``,
        ``Stability``. Sorted by ``Stability Score`` descending.
    """
    rows = []
    for col in num_columns:
        series = df[col].dropna()
        if not pd.api.types.is_numeric_dtype(df[col]) or len(series) == 0:
            continue
        missing_rate = round((df[col].isnull().sum() / len(df[col])) * 100, 2)
        mean = series.mean()
        std = series.std()
        cv = std / mean if mean != 0 else np.nan
        skewness = round(float(series.skew()), 3)
        kurtosis = round(float(series.kurtosis()), 3)
        outlier_rate = _outlier_rate_iqr(series)
        score = _stability_score_numerical(missing_rate, cv, skewness, kurtosis, outlier_rate)
        rows.append({
            "Feature": col,
            "Missing Rate (%)": missing_rate,
            "Coeff. of Variation": round(float(cv), 3) if not (np.isnan(cv) or np.isinf(cv)) else "N/A",
            "Skewness": skewness,
            "Kurtosis (excess)": kurtosis,
            "Outlier Rate (%)": outlier_rate,
            "Stability Score": score,
            "Stability": _stability_label(score),
        })
    return pd.DataFrame(rows).sort_values("Stability Score", ascending=False).reset_index(drop=True)


@st.cache_data
def compute_categorical_stability(df, cat_columns):
    """Compute stability metrics for all categorical (non-numeric) columns.

    For each column the following statistics are calculated: missing rate,
    cardinality, mode frequency, and normalised Shannon entropy. These feed
    into a composite **Stability Score** (0–100) and a categorical
    **Stability** label.

    Scoring penalties (max deductions):

    * Missing rate → up to −30 pts
    * Cardinality  → up to −30 pts
    * Mode dominance (> 80 %) → up to −20 pts
    * Low entropy → up to −20 pts

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset to analyse.
    cat_columns : list of str
        Column names to consider. Numeric columns in this list are skipped.

    Returns
    -------
    pandas.DataFrame
        One row per column with the columns: ``Feature``,
        ``Missing Rate (%)``, ``Unique Values``, ``Cardinality (%)``,
        ``Entropy (bits)``, ``Mode Frequency (%)``, ``Stability Score``,
        ``Stability``. Sorted by ``Stability Score`` descending.
    """
    rows = []
    obj_cols = [c for c in cat_columns if not pd.api.types.is_numeric_dtype(df[c])]
    for col in obj_cols:
        series = df[col].dropna()
        n_total = len(df[col])
        if len(series) == 0:
            continue
        missing_rate = round((df[col].isnull().sum() / n_total) * 100, 2)
        n_unique = series.nunique()
        cardinality = round((n_unique / n_total) * 100, 2)
        value_probs = series.value_counts(normalize=True)
        entropy = round(float(stats.entropy(value_probs, base=2)), 3)
        max_entropy = np.log2(n_unique) if n_unique > 1 else 1.0
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        mode_freq = round(float(value_probs.iloc[0]) * 100, 2)
        score = _stability_score_categorical(missing_rate, cardinality, mode_freq, normalized_entropy)
        rows.append({
            "Feature": col,
            "Missing Rate (%)": missing_rate,
            "Unique Values": n_unique,
            "Cardinality (%)": cardinality,
            "Entropy (bits)": entropy,
            "Mode Frequency (%)": mode_freq,
            "Stability Score": score,
            "Stability": _stability_label(score),
        })
    return pd.DataFrame(rows).sort_values("Stability Score", ascending=False).reset_index(drop=True)


def _color_stability(val):
    palette = {
        "Stable":           "background-color: #d4edda; color: #155724",
        "Moderate":         "background-color: #fff3cd; color: #856404",
        "Unstable":         "background-color: #ffe0b2; color: #e65100",
        "Highly Unstable":  "background-color: #f8d7da; color: #721c24",
    }
    return palette.get(val, "")


def _color_score(val):
    if not isinstance(val, (int, float)):
        return ""
    if val >= 80:
        return "color: #155724; font-weight: bold"
    elif val >= 60:
        return "color: #856404; font-weight: bold"
    elif val >= 40:
        return "color: #e65100; font-weight: bold"
    return "color: #721c24; font-weight: bold"


_SCORE_COLORS = {
    "Stable":          "#28a745",
    "Moderate":        "#ffc107",
    "Unstable":        "#fd7e14",
    "Highly Unstable": "#dc3545",
}


def _bar_chart(report, title):
    fig = px.bar(
        report,
        x="Feature",
        y="Stability Score",
        color="Stability",
        color_discrete_map=_SCORE_COLORS,
        title=title,
        range_y=[0, 100],
    )
    fig.add_hline(y=80, line_dash="dot", line_color="green",  annotation_text="Stable ≥ 80")
    fig.add_hline(y=60, line_dash="dot", line_color="orange", annotation_text="Moderate ≥ 60")
    return fig


def _radar_chart(df, feature, num_report):
    row = num_report[num_report["Feature"] == feature].iloc[0]
    missing_rate = row["Missing Rate (%)"]
    cv_raw = row["Coeff. of Variation"]
    cv_val = float(cv_raw) if cv_raw != "N/A" else 2.0
    skew_val = abs(row["Skewness"])
    kurt_val = abs(row["Kurtosis (excess)"])
    outlier_val = row["Outlier Rate (%)"]

    sub_scores = {
        "Completeness":    max(0, 100 - missing_rate * 2),
        "Low Variability": max(0, 100 - min(abs(cv_val) * 40, 100)),
        "Symmetry":        max(0, 100 - min(skew_val * 20, 100)),
        "Light Tails":     max(0, 100 - min(kurt_val * 6, 100)),
        "Low Outliers":    max(0, 100 - min(outlier_val * 4, 100)),
    }

    cats = list(sub_scores.keys()) + [list(sub_scores.keys())[0]]
    vals = list(sub_scores.values()) + [list(sub_scores.values())[0]]

    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(160, 112, 236, 0.3)",
        line_color="#a070ec",
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        title=f"Stability Profile: {feature}",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Stability Score", f"{row['Stability Score']}/100")
    c2.metric("Missing Rate",    f"{missing_rate}%")
    c3.metric("Outlier Rate",    f"{outlier_val}%")
    c4.metric("Skewness",        row["Skewness"])
    c5.metric("Kurtosis",        row["Kurtosis (excess)"])


def display_stability_report(df, num_columns, cat_columns):
    """Render the full Feature Stability Analysis section in the Streamlit app.

    Displays:

    * A colour-coded stability table for numerical features (via
      :func:`compute_numerical_stability`).
    * A bar chart of numerical stability scores.
    * A radar chart and key metrics for a user-selected numerical feature.
    * A colour-coded stability table for categorical features (via
      :func:`compute_categorical_stability`).
    * A bar chart of categorical stability scores.

    Stability labels and their score thresholds:

    ==================  =============
    Label               Score range
    ==================  =============
    Stable              ≥ 80
    Moderate            60 – 79
    Unstable            40 – 59
    Highly Unstable     < 40
    ==================  =============

    Parameters
    ----------
    df : pandas.DataFrame
        The dataset to analyse.
    num_columns : list of str
        Numerical column names.
    cat_columns : list of str
        Categorical column names.
    """
    st.markdown(
        "Each feature receives a **Stability Score (0–100)** based on missing data, "
        "variability, distribution shape, and outlier prevalence. "
        "Higher scores indicate cleaner, more reliable features."
    )

    has_numerical = bool(num_columns) and any(
        pd.api.types.is_numeric_dtype(df[c]) for c in num_columns
    )
    has_categorical = bool(cat_columns) and any(
        not pd.api.types.is_numeric_dtype(df[c]) for c in cat_columns
    )

    if has_numerical:
        st.subheader("Numerical Features")
        num_report = compute_numerical_stability(df, num_columns)
        if not num_report.empty:
            styled = (
                num_report.style
                .map(_color_stability, subset=["Stability"])
                .map(_color_score,     subset=["Stability Score"])
            )
            st.dataframe(styled, use_container_width=True)
            st.plotly_chart(_bar_chart(num_report, "Numerical Feature Stability Scores"), use_container_width=True)

            st.subheader("Feature Deep Dive")
            valid_cols = num_report["Feature"].tolist()
            selected = st.selectbox("Select a numerical feature to inspect:", valid_cols, key="stability_num_select")
            _radar_chart(df, selected, num_report)
        else:
            st.info("No valid numerical columns to analyse.")
    else:
        st.info("No numerical columns found.")

    if has_categorical:
        st.subheader("Categorical Features")
        cat_report = compute_categorical_stability(df, cat_columns)
        if not cat_report.empty:
            styled_cat = (
                cat_report.style
                .map(_color_stability, subset=["Stability"])
                .map(_color_score,     subset=["Stability Score"])
            )
            st.dataframe(styled_cat, use_container_width=True)
            st.plotly_chart(_bar_chart(cat_report, "Categorical Feature Stability Scores"), use_container_width=True)
        else:
            st.info("No valid categorical columns to analyse.")
