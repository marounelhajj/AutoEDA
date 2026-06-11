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


# ── Time-series feature stability ─────────────────────────────────────────────

def _build_windows(df_sorted, time_col, window_size, step_size):
    n = len(df_sorted)
    windows, wid, start = [], 0, 0
    while start + window_size <= n:
        label = df_sorted[time_col].iloc[start] if time_col else start
        windows.append((wid, label, df_sorted.iloc[start : start + window_size]))
        start += step_size
        wid += 1
    return windows


def _compute_psi(reference, current, n_bins=10):
    lo, hi = min(reference.min(), current.min()), max(reference.max(), current.max())
    if lo == hi:
        return 0.0
    bins    = np.linspace(lo, hi, n_bins + 1)
    ref_pct = np.histogram(reference, bins=bins)[0] / len(reference)
    cur_pct = np.histogram(current,   bins=bins)[0] / len(current)
    ref_pct = np.where(ref_pct == 0, 1e-4, ref_pct)
    cur_pct = np.where(cur_pct == 0, 1e-4, cur_pct)
    return round(float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct))), 4)


def _compute_js_divergence(s1, s2):
    cats = set(s1.unique()) | set(s2.unique())
    p = s1.value_counts(normalize=True).reindex(cats, fill_value=1e-10)
    q = s2.value_counts(normalize=True).reindex(cats, fill_value=1e-10)
    m = 0.5 * (p + q)
    return round(float(0.5 * stats.entropy(p, m, base=2) + 0.5 * stats.entropy(q, m, base=2)), 4)


def _drift_label_ks(v):
    if not isinstance(v, float) or np.isnan(v): return "N/A"
    if v < 0.05:  return "Stable"
    if v < 0.10:  return "Moderate"
    if v < 0.20:  return "Drifting"
    return "High Drift"


def _drift_label_js(v):
    if not isinstance(v, float) or np.isnan(v): return "N/A"
    if v < 0.05:  return "Stable"
    if v < 0.15:  return "Moderate"
    if v < 0.30:  return "Drifting"
    return "High Drift"


_DRIFT_COLORS = {
    "Stable":     "#28a745",
    "Moderate":   "#ffc107",
    "Drifting":   "#fd7e14",
    "High Drift": "#dc3545",
    "N/A":        "#adb5bd",
}

_DRIFT_STYLES = {
    "Stable":     "background-color: #d4edda; color: #155724",
    "Moderate":   "background-color: #fff3cd; color: #856404",
    "Drifting":   "background-color: #ffe0b2; color: #e65100",
    "High Drift": "background-color: #f8d7da; color: #721c24",
}


def _color_drift(val):
    return _DRIFT_STYLES.get(val, "")


@st.cache_data
def compute_ts_numerical_stability(df, time_col, num_columns, window_size, step_size):
    df_sorted = df.sort_values(time_col).reset_index(drop=True) if time_col else df.reset_index(drop=True)
    windows   = _build_windows(df_sorted, time_col, window_size, step_size)
    if not windows:
        return pd.DataFrame()

    ref_df = windows[0][2]
    rows   = []

    for i, (wid, label, wdf) in enumerate(windows):
        for col in num_columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            series = wdf[col].dropna()
            if len(series) == 0:
                continue

            ks_stat = np.nan
            if i > 0:
                prev = windows[i - 1][2][col].dropna()
                if len(prev) > 0:
                    ks_stat = round(float(stats.ks_2samp(prev, series).statistic), 4)

            psi = np.nan
            if i > 0:
                ref_s = ref_df[col].dropna()
                if len(ref_s) > 0:
                    psi = _compute_psi(ref_s.values, series.values)

            rows.append({
                "window_id":         wid,
                "window_start":      label,
                "Feature":           col,
                "Mean":              round(float(series.mean()),     4),
                "Std":               round(float(series.std()),      4),
                "Skewness":          round(float(series.skew()),     4),
                "Kurtosis":          round(float(series.kurtosis()), 4),
                "Missing Rate (%)":  round((wdf[col].isnull().sum() / len(wdf)) * 100, 2),
                "KS Stat (vs prev)": ks_stat,
                "PSI (vs ref)":      psi,
            })

    return pd.DataFrame(rows)


@st.cache_data
def compute_ts_categorical_stability(df, time_col, cat_columns, window_size, step_size):
    df_sorted = df.sort_values(time_col).reset_index(drop=True) if time_col else df.reset_index(drop=True)
    windows   = _build_windows(df_sorted, time_col, window_size, step_size)
    if not windows:
        return pd.DataFrame()

    ref_df   = windows[0][2]
    obj_cols = [c for c in cat_columns if not pd.api.types.is_numeric_dtype(df[c])]
    rows     = []

    for i, (wid, label, wdf) in enumerate(windows):
        for col in obj_cols:
            series = wdf[col].dropna()
            if len(series) == 0:
                continue

            vp      = series.value_counts(normalize=True)
            n_uniq  = series.nunique()
            max_ent = np.log2(n_uniq) if n_uniq > 1 else 1.0
            ent     = float(stats.entropy(vp, base=2))

            js_prev = np.nan
            if i > 0:
                prev = windows[i - 1][2][col].dropna()
                if len(prev) > 0:
                    js_prev = _compute_js_divergence(prev, series)

            js_ref = np.nan
            if i > 0:
                ref_s = ref_df[col].dropna()
                if len(ref_s) > 0:
                    js_ref = _compute_js_divergence(ref_s, series)

            rows.append({
                "window_id":          wid,
                "window_start":       label,
                "Feature":            col,
                "Mode Frequency (%)": round(float(vp.iloc[0]) * 100, 2),
                "Entropy (bits)":     round(ent, 3),
                "Norm. Entropy":      round(ent / max_ent, 3) if max_ent > 0 else 0.0,
                "Cardinality (%)":    round((n_uniq / len(wdf)) * 100, 2),
                "Missing Rate (%)":   round((wdf[col].isnull().sum() / len(wdf)) * 100, 2),
                "JS Div (vs prev)":   js_prev,
                "JS Div (vs ref)":    js_ref,
            })

    return pd.DataFrame(rows)


def _ts_numerical_summary(ts_df):
    rows = []
    for feat, grp in ts_df.groupby("Feature"):
        avg_ks  = float(grp["KS Stat (vs prev)"].mean())
        max_psi = float(grp["PSI (vs ref)"].max())
        rows.append({
            "Feature":          feat,
            "Avg KS (vs prev)": avg_ks  if not np.isnan(avg_ks)  else np.nan,
            "Max PSI (vs ref)": max_psi if not np.isnan(max_psi) else np.nan,
            "Avg Missing (%)":  round(float(grp["Missing Rate (%)"].mean()), 2),
            "Drift":            _drift_label_ks(avg_ks),
        })
    return (
        pd.DataFrame(rows)
        .sort_values("Avg KS (vs prev)", ascending=False, na_position="last")
        .reset_index(drop=True)
    )


def _ts_categorical_summary(ts_df):
    rows = []
    for feat, grp in ts_df.groupby("Feature"):
        avg_js  = float(grp["JS Div (vs prev)"].mean())
        max_ref = float(grp["JS Div (vs ref)"].max())
        rows.append({
            "Feature":          feat,
            "Avg JS (vs prev)": avg_js  if not np.isnan(avg_js)  else np.nan,
            "Max JS (vs ref)":  max_ref if not np.isnan(max_ref) else np.nan,
            "Avg Missing (%)":  round(float(grp["Missing Rate (%)"].mean()), 2),
            "Drift":            _drift_label_js(avg_js),
        })
    return (
        pd.DataFrame(rows)
        .sort_values("Avg JS (vs prev)", ascending=False, na_position="last")
        .reset_index(drop=True)
    )


def display_ts_stability_report(df, num_columns, cat_columns):
    st.markdown(
        "Feature stability is measured by sliding a window across the dataset and computing "
        "per-window statistics. **KS Stat** and **PSI** (numerical) and **JS Divergence** "
        "(categorical) quantify how much each feature's distribution shifts between windows."
    )

    # ── Window configuration ───────────────────────────────────────────────────
    with st.expander("⚙️ Window Configuration", expanded=True):
        time_col_label = st.selectbox(
            "Time column (defines ordering)",
            ["Row order"] + list(df.columns),
            key="ts_time_col",
            help="Column used to sort the data before windowing. 'Row order' uses row indices.",
        )
        time_col = None if time_col_label == "Row order" else time_col_label

        n_rows       = len(df)
        default_win  = max(10, n_rows // 10)
        default_step = max(1,  default_win // 2)

        c1, c2 = st.columns(2)
        with c1:
            window_size = int(st.number_input(
                "Window size (rows)", min_value=2, max_value=n_rows,
                value=min(default_win, n_rows), step=1, key="ts_window_size",
                help="Number of rows in each window.",
            ))
        with c2:
            step_size = int(st.number_input(
                "Step size (rows)", min_value=1, max_value=n_rows,
                value=min(default_step, n_rows), step=1, key="ts_step_size",
                help="Rows to advance between consecutive windows. Step < window size creates overlap.",
            ))

    # ── Validation ─────────────────────────────────────────────────────────────
    n_windows = max(0, (n_rows - window_size) // step_size + 1)
    if n_windows == 0:
        st.error(f"Window size ({window_size}) exceeds the dataset ({n_rows} rows). Reduce it.")
        return

    st.info(
        f"**{n_windows} window{'s' if n_windows != 1 else ''}** — "
        f"window size = {window_size} rows, step = {step_size} rows."
    )
    if n_windows == 1:
        st.warning(
            "Only 1 window produced — drift metrics (KS, PSI, JS Divergence) need at least 2 windows. "
            "Reduce the window size or step size."
        )

    # ── Numerical features ─────────────────────────────────────────────────────
    has_num = bool(num_columns) and any(pd.api.types.is_numeric_dtype(df[c]) for c in num_columns)
    if has_num:
        st.subheader("Numerical Features")
        ts_num = compute_ts_numerical_stability(df, time_col, num_columns, window_size, step_size)

        if ts_num.empty:
            st.info("No valid numerical data for the chosen window configuration.")
        else:
            num_sum = _ts_numerical_summary(ts_num)
            st.dataframe(
                num_sum.style
                    .map(_color_drift, subset=["Drift"])
                    .format({"Avg KS (vs prev)": "{:.4f}", "Max PSI (vs ref)": "{:.4f}"}, na_rep="N/A"),
                use_container_width=True,
            )

            plot_num = num_sum.dropna(subset=["Avg KS (vs prev)"])
            if not plot_num.empty:
                fig_sum = px.bar(
                    plot_num, x="Feature", y="Avg KS (vs prev)", color="Drift",
                    color_discrete_map=_DRIFT_COLORS,
                    title="Average KS Statistic per Feature (vs previous window)",
                )
                fig_sum.add_hline(y=0.05, line_dash="dot", line_color="green",  annotation_text="Stable")
                fig_sum.add_hline(y=0.10, line_dash="dot", line_color="orange", annotation_text="Moderate")
                fig_sum.add_hline(y=0.20, line_dash="dot", line_color="red",    annotation_text="Drifting")
                st.plotly_chart(fig_sum, use_container_width=True)

            # Feature drill-down
            st.subheader("Feature Drill-Down")
            sel_num = st.selectbox(
                "Select a numerical feature:", ts_num["Feature"].unique().tolist(), key="ts_num_sel"
            )
            fdf = ts_num[ts_num["Feature"] == sel_num].sort_values("window_id")
            x   = fdf["window_start"]

            # Mean ± Std band
            fig1 = go.Figure()
            fig1.add_trace(go.Scatter(
                x=x, y=fdf["Mean"] + fdf["Std"],
                mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip",
            ))
            fig1.add_trace(go.Scatter(
                x=x, y=fdf["Mean"] - fdf["Std"],
                mode="lines", fill="tonexty", fillcolor="rgba(160,112,236,0.2)",
                line=dict(width=0), name="±1 Std",
            ))
            fig1.add_trace(go.Scatter(
                x=x, y=fdf["Mean"], mode="lines+markers", name="Mean", line=dict(color="#a070ec"),
            ))
            fig1.update_layout(
                title=f"{sel_num} — Mean ± Std", xaxis_title="Window Start", yaxis_title="Value"
            )
            st.plotly_chart(fig1, use_container_width=True)

            # Skewness & Kurtosis
            fig2 = go.Figure([
                go.Scatter(x=x, y=fdf["Skewness"], mode="lines+markers",
                           name="Skewness", line=dict(color="#17becf")),
                go.Scatter(x=x, y=fdf["Kurtosis"], mode="lines+markers",
                           name="Kurtosis", line=dict(color="#e377c2")),
            ])
            fig2.add_hline(y=0, line_dash="dash", line_color="gray")
            fig2.update_layout(title=f"{sel_num} — Skewness & Kurtosis", xaxis_title="Window Start")
            st.plotly_chart(fig2, use_container_width=True)

            # Drift metrics
            if n_windows > 1:
                fig3 = go.Figure([
                    go.Scatter(x=x, y=fdf["KS Stat (vs prev)"], mode="lines+markers",
                               name="KS Stat (vs prev)", line=dict(color="#d62728")),
                    go.Scatter(x=x, y=fdf["PSI (vs ref)"],      mode="lines+markers",
                               name="PSI (vs ref)",      line=dict(color="#ff7f0e")),
                ])
                fig3.add_hline(y=0.05, line_dash="dot", line_color="green",  annotation_text="KS Stable < 0.05")
                fig3.add_hline(y=0.10, line_dash="dot", line_color="orange", annotation_text="KS Moderate < 0.10")
                fig3.add_hline(y=0.25, line_dash="dot", line_color="red",    annotation_text="PSI Shift > 0.25")
                fig3.update_layout(
                    title=f"{sel_num} — Drift Metrics", xaxis_title="Window Start", yaxis_title="Score"
                )
                st.plotly_chart(fig3, use_container_width=True)

            # Missing rate
            st.plotly_chart(
                px.line(fdf, x="window_start", y="Missing Rate (%)", markers=True,
                        title=f"{sel_num} — Missing Rate", color_discrete_sequence=["#636efa"]),
                use_container_width=True,
            )
    else:
        st.info("No numerical columns found.")

    # ── Categorical features ───────────────────────────────────────────────────
    has_cat = bool(cat_columns) and any(not pd.api.types.is_numeric_dtype(df[c]) for c in cat_columns)
    if has_cat:
        st.subheader("Categorical Features")
        ts_cat = compute_ts_categorical_stability(df, time_col, cat_columns, window_size, step_size)

        if ts_cat.empty:
            st.info("No valid categorical data for the chosen window configuration.")
        else:
            cat_sum = _ts_categorical_summary(ts_cat)
            st.dataframe(
                cat_sum.style
                    .map(_color_drift, subset=["Drift"])
                    .format({"Avg JS (vs prev)": "{:.4f}", "Max JS (vs ref)": "{:.4f}"}, na_rep="N/A"),
                use_container_width=True,
            )

            plot_cat = cat_sum.dropna(subset=["Avg JS (vs prev)"])
            if not plot_cat.empty:
                fig_cat = px.bar(
                    plot_cat, x="Feature", y="Avg JS (vs prev)", color="Drift",
                    color_discrete_map=_DRIFT_COLORS,
                    title="Average JS Divergence per Feature (vs previous window)",
                )
                fig_cat.add_hline(y=0.05, line_dash="dot", line_color="green",  annotation_text="Stable")
                fig_cat.add_hline(y=0.15, line_dash="dot", line_color="orange", annotation_text="Moderate")
                fig_cat.add_hline(y=0.30, line_dash="dot", line_color="red",    annotation_text="Drifting")
                st.plotly_chart(fig_cat, use_container_width=True)

            # Feature drill-down
            st.subheader("Feature Drill-Down")
            sel_cat = st.selectbox(
                "Select a categorical feature:", ts_cat["Feature"].unique().tolist(), key="ts_cat_sel"
            )
            cdf = ts_cat[ts_cat["Feature"] == sel_cat].sort_values("window_id")
            xc  = cdf["window_start"]

            st.plotly_chart(
                px.line(cdf, x="window_start", y="Entropy (bits)", markers=True,
                        title=f"{sel_cat} — Shannon Entropy", color_discrete_sequence=["#a070ec"]),
                use_container_width=True,
            )
            st.plotly_chart(
                px.line(cdf, x="window_start", y="Mode Frequency (%)", markers=True,
                        title=f"{sel_cat} — Mode Frequency", color_discrete_sequence=["#17becf"]),
                use_container_width=True,
            )

            if n_windows > 1:
                fig_js = go.Figure([
                    go.Scatter(x=xc, y=cdf["JS Div (vs prev)"], mode="lines+markers",
                               name="JS Div (vs prev)", line=dict(color="#d62728")),
                    go.Scatter(x=xc, y=cdf["JS Div (vs ref)"],  mode="lines+markers",
                               name="JS Div (vs ref)",  line=dict(color="#ff7f0e")),
                ])
                fig_js.add_hline(y=0.05, line_dash="dot", line_color="green",  annotation_text="Stable")
                fig_js.add_hline(y=0.15, line_dash="dot", line_color="orange", annotation_text="Moderate")
                fig_js.add_hline(y=0.30, line_dash="dot", line_color="red",    annotation_text="Drifting")
                fig_js.update_layout(
                    title=f"{sel_cat} — JS Divergence",
                    xaxis_title="Window Start", yaxis_title="JS Divergence",
                )
                st.plotly_chart(fig_js, use_container_width=True)

            st.plotly_chart(
                px.line(cdf, x="window_start", y="Missing Rate (%)", markers=True,
                        title=f"{sel_cat} — Missing Rate", color_discrete_sequence=["#636efa"]),
                use_container_width=True,
            )
    else:
        st.info("No categorical columns found.")

