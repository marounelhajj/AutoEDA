API Reference
=============

Data Analysis Module
--------------------

.. py:function:: load_data(file)

   Load a CSV or Excel file into a DataFrame.

   Supported formats: ``.csv``, ``.xls``, ``.xlsx``. CSV files are tried
   with multiple encodings (utf-8, latin-1, cp1252, utf-16) before falling
   back to Excel parsing.

   :param file: File path or Streamlit ``UploadedFile`` object.
   :type file: str or file-like
   :returns: The loaded dataset.
   :rtype: pandas.DataFrame
   :raises ValueError: If the file cannot be parsed as CSV or Excel.

.. py:function:: categorical_numerical(df)

   Classify DataFrame columns into numerical and categorical lists.

   A column is treated as numerical when it has a numeric dtype **and** more
   than 30 distinct values; otherwise it is treated as categorical.

   :param df: The input dataset.
   :type df: pandas.DataFrame
   :returns: ``(num_columns, cat_columns)`` — lists of numerical and categorical column names.
   :rtype: tuple[list[str], list[str]]

.. py:function:: display_dataset_overview(df, cat_columns, num_columns)

   Render a dataset overview section in the Streamlit app.

   Displays a configurable row preview followed by a summary card showing
   row/column counts, duplicate count, and the lists of categorical and
   numerical columns.

   :param df: The dataset to summarise.
   :type df: pandas.DataFrame
   :param cat_columns: Categorical column names.
   :type cat_columns: list[str]
   :param num_columns: Numerical column names.
   :type num_columns: list[str]

.. py:function:: display_missing_values(df)

   Render a missing-value summary table in the Streamlit app.

   Shows columns that contain at least one null value, sorted by missing
   count descending. Displays an info message when the dataset is complete.

   :param df: The dataset to inspect.
   :type df: pandas.DataFrame

.. py:function:: display_statistics_visualization(df, cat_columns, num_columns)

   Render summary statistics and bar charts for all column types.

   For numerical columns, shows ``df.describe()`` output. For categorical
   columns, renders interactive bar charts and value-count tables for a
   user-selected subset of columns.

   :param df: The dataset to visualise.
   :type df: pandas.DataFrame
   :param cat_columns: Categorical column names.
   :type cat_columns: list[str]
   :param num_columns: Numerical column names.
   :type num_columns: list[str]

.. py:function:: display_data_types(df)

   Render a data-type table for every column in the Streamlit app.

   :param df: The dataset whose column dtypes should be displayed.
   :type df: pandas.DataFrame

.. py:function:: search_column(df)

   Render an interactive column search and dtype filter in the Streamlit app.

   Provides a text input to search column names by substring and a selectbox
   to filter by data type. The filtered DataFrame is displayed below the controls.

   :param df: The dataset to search through.
   :type df: pandas.DataFrame

.. py:function:: display_individual_feature_distribution(df, num_columns)

   Render distribution plots for a single numerical feature.

   Lets the user pick a numerical column and a plot type (Histogram, Scatter
   Plot, Density Plot, or Box Plot) and displays the resulting Plotly chart
   along with descriptive statistics.

   :param df: The dataset to visualise.
   :type df: pandas.DataFrame
   :param num_columns: Numerical column names available for selection.
   :type num_columns: list[str]

.. py:function:: display_scatter_plot_of_two_numeric_features(df, num_columns)

   Render an interactive scatter plot comparing two numerical features.

   :param df: The dataset to visualise.
   :type df: pandas.DataFrame
   :param num_columns: Numerical column names. At least two columns are required.
   :type num_columns: list[str]

.. py:function:: categorical_variable_analysis(df, cat_columns)

   Render visualisations for a single categorical feature.

   Supports Bar Chart, Pie Chart, Stacked Bar Chart, and Frequency Count.
   Charts are capped at 50 categories to keep rendering fast.

   :param df: The dataset to visualise.
   :type df: pandas.DataFrame
   :param cat_columns: Categorical column names available for selection.
   :type cat_columns: list[str]

.. py:function:: feature_exploration_numerical_variables(df, num_columns)

   Render multi-feature exploration tools for numerical variables.

   Allows the user to select two or more numerical columns and generate a
   Scatter Plot Matrix, Pair Plot, or Correlation Heatmap on demand.

   :param df: The dataset to visualise.
   :type df: pandas.DataFrame
   :param num_columns: Numerical column names available for selection.
   :type num_columns: list[str]

.. py:function:: categorical_numerical_variable_analysis(df, cat_columns, num_columns)

   Render a grouped bar chart of mean numerical value per category.

   Results are limited to the top 50 categories by mean value.

   :param df: The dataset to visualise.
   :type df: pandas.DataFrame
   :param cat_columns: Categorical column names available for selection.
   :type cat_columns: list[str]
   :param num_columns: Numerical column names available for selection.
   :type num_columns: list[str]


Data Preprocessing Module
-------------------------

.. py:function:: remove_selected_columns(df, columns_remove)

   Drop the specified columns from a DataFrame.

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param columns_remove: Column names to drop.
   :type columns_remove: list[str]
   :returns: Dataframe with the specified columns removed.
   :rtype: pandas.DataFrame

.. py:function:: remove_rows_with_missing_data(df, columns)

   Drop rows that contain missing values in the specified columns.

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param columns: Column names to check for null values.
   :type columns: list[str]
   :returns: Dataframe with the affected rows removed.
   :rtype: pandas.DataFrame

.. py:function:: fill_missing_data(df, columns, method)

   Impute missing values in the specified columns.

   :param df: Input dataframe (modified in-place).
   :type df: pandas.DataFrame
   :param columns: Column names whose null values will be filled.
   :type columns: list[str]
   :param method: Imputation strategy — ``'mean'``, ``'median'``, or ``'mode'``.
   :type method: str
   :returns: Dataframe with missing values filled.
   :rtype: pandas.DataFrame

.. py:function:: one_hot_encode(df, columns)

   Apply one-hot encoding to the specified categorical columns.

   Each column is replaced by binary indicator columns prefixed with the
   original column name (``drop_first=False``).

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param columns: Categorical column names to encode.
   :type columns: list[str]
   :returns: Dataframe with the original columns replaced by dummy variables.
   :rtype: pandas.DataFrame

.. py:function:: label_encode(df, columns)

   Apply label encoding to the specified categorical columns.

   Each unique string value is mapped to an integer using
   ``sklearn.preprocessing.LabelEncoder``, fit per column independently.

   :param df: Input dataframe (modified in-place).
   :type df: pandas.DataFrame
   :param columns: Categorical column names to encode.
   :type columns: list[str]
   :returns: Dataframe with the specified columns replaced by integer labels.
   :rtype: pandas.DataFrame

.. py:function:: standard_scale(df, columns)

   Standardize columns to zero mean and unit variance.

   :param df: Input dataframe (modified in-place).
   :type df: pandas.DataFrame
   :param columns: Numerical column names to scale.
   :type columns: list[str]
   :returns: Dataframe with the specified columns standardised.
   :rtype: pandas.DataFrame

.. py:function:: min_max_scale(df, columns, feature_range=(0, 1))

   Scale columns to a specified minimum–maximum range.

   :param df: Input dataframe (modified in-place).
   :type df: pandas.DataFrame
   :param columns: Numerical column names to scale.
   :type columns: list[str]
   :param feature_range: Desired output range, default ``(0, 1)``.
   :type feature_range: tuple[float, float]
   :returns: Dataframe with the specified columns scaled.
   :rtype: pandas.DataFrame

.. py:function:: detect_outliers_iqr(df, column_name)

   Detect outliers using the IQR method.

   Values below ``Q1 - 1.5 × IQR`` or above ``Q3 + 1.5 × IQR`` are flagged.

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param column_name: Name of the numerical column to inspect.
   :type column_name: str
   :returns: Sorted list of outlier values.
   :rtype: list

.. py:function:: detect_outliers_zscore(df, column_name)

   Detect outliers using the Z-score method.

   Values whose absolute Z-score exceeds 3 are flagged.

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param column_name: Name of the numerical column to inspect.
   :type column_name: str
   :returns: List of outlier values.
   :rtype: list

.. py:function:: remove_outliers(df, column_name, outliers)

   Remove rows containing outlier values from a specified column.

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param column_name: Name of the column in which outliers were detected.
   :type column_name: str
   :param outliers: List of values identified as outliers.
   :type outliers: list
   :returns: Dataframe with all rows containing outlier values removed.
   :rtype: pandas.DataFrame

.. py:function:: transform_outliers(df, column_name, outliers)

   Replace outlier values with the median of non-outlier observations.

   :param df: Input dataframe.
   :type df: pandas.DataFrame
   :param column_name: Name of the column containing outliers.
   :type column_name: str
   :param outliers: List of values identified as outliers.
   :type outliers: list
   :returns: Dataframe with outlier values replaced by the non-outlier median.
   :rtype: pandas.DataFrame


Feature Stability Module
------------------------

.. py:function:: compute_numerical_stability(df, num_columns)

   Compute stability metrics for all numerical columns.

   For each column the following statistics are calculated: missing rate,
   coefficient of variation, skewness, excess kurtosis, and IQR-based outlier
   rate. These feed into a composite **Stability Score** (0–100).

   Scoring penalties:

   .. list-table::
      :header-rows: 1

      * - Factor
        - Max deduction
      * - Missing rate
        - −30 pts
      * - Coefficient of variation
        - −25 pts
      * - Skewness
        - −20 pts
      * - Kurtosis
        - −15 pts
      * - Outlier rate
        - −10 pts

   :param df: The dataset to analyse.
   :type df: pandas.DataFrame
   :param num_columns: Numerical column names to include.
   :type num_columns: list[str]
   :returns: One row per column with fields: ``Feature``, ``Missing Rate (%)``,
             ``Coeff. of Variation``, ``Skewness``, ``Kurtosis (excess)``,
             ``Outlier Rate (%)``, ``Stability Score``, ``Stability``.
             Sorted by ``Stability Score`` descending.
   :rtype: pandas.DataFrame

.. py:function:: compute_categorical_stability(df, cat_columns)

   Compute stability metrics for all categorical (non-numeric) columns.

   For each column the following statistics are calculated: missing rate,
   cardinality, mode frequency, and normalised Shannon entropy. These feed
   into a composite **Stability Score** (0–100).

   Scoring penalties:

   .. list-table::
      :header-rows: 1

      * - Factor
        - Max deduction
      * - Missing rate
        - −30 pts
      * - Cardinality
        - −30 pts
      * - Mode dominance (> 80 %)
        - −20 pts
      * - Low entropy
        - −20 pts

   :param df: The dataset to analyse.
   :type df: pandas.DataFrame
   :param cat_columns: Column names to consider. Numeric columns are skipped.
   :type cat_columns: list[str]
   :returns: One row per column with fields: ``Feature``, ``Missing Rate (%)``,
             ``Unique Values``, ``Cardinality (%)``, ``Entropy (bits)``,
             ``Mode Frequency (%)``, ``Stability Score``, ``Stability``.
             Sorted by ``Stability Score`` descending.
   :rtype: pandas.DataFrame

.. py:function:: display_stability_report(df, num_columns, cat_columns)

   Render the full Feature Stability Analysis section in the Streamlit app.

   Displays a colour-coded stability table, bar chart, and radar chart for
   numerical features, and a colour-coded stability table and bar chart for
   categorical features.

   Stability label thresholds:

   .. list-table::
      :header-rows: 1

      * - Label
        - Score range
      * - Stable
        - ≥ 80
      * - Moderate
        - 60 – 79
      * - Unstable
        - 40 – 59
      * - Highly Unstable
        - < 40

   :param df: The dataset to analyse.
   :type df: pandas.DataFrame
   :param num_columns: Numerical column names.
   :type num_columns: list[str]
   :param cat_columns: Categorical column names.
   :type cat_columns: list[str]


Time-Series Feature Stability Module
-------------------------------------

.. py:function:: compute_ts_numerical_stability(df, time_col, num_columns, window_size, step_size)

   Compute per-window stability metrics for numerical columns over time.

   Sorts the DataFrame by ``time_col`` (or uses row order when ``None``), then
   slides a window of ``window_size`` rows forward by ``step_size`` rows at a
   time. For each window the following statistics are recorded: mean, standard
   deviation, skewness, excess kurtosis, missing rate, KS statistic versus the
   previous window, and PSI versus the first (reference) window.

   :param df: The dataset to analyse.
   :type df: pandas.DataFrame
   :param time_col: Column name used to sort the data before windowing, or
                    ``None`` to use the existing row order.
   :type time_col: str or None
   :param num_columns: Numerical column names to include.
   :type num_columns: list[str]
   :param window_size: Number of rows per window.
   :type window_size: int
   :param step_size: Number of rows to advance between consecutive windows.
                     Values smaller than ``window_size`` produce overlapping windows.
   :type step_size: int
   :returns: One row per (window, feature) pair with fields: ``window_id``,
             ``window_start``, ``Feature``, ``Mean``, ``Std``, ``Skewness``,
             ``Kurtosis``, ``Missing Rate (%)``, ``KS Stat (vs prev)``,
             ``PSI (vs ref)``. Returns an empty DataFrame when fewer windows
             than ``window_size`` rows exist.
   :rtype: pandas.DataFrame

.. py:function:: compute_ts_categorical_stability(df, time_col, cat_columns, window_size, step_size)

   Compute per-window stability metrics for categorical columns over time.

   Applies the same sliding-window scheme as
   :func:`compute_ts_numerical_stability`. For each window the following
   statistics are recorded: mode frequency, Shannon entropy, normalised
   entropy, cardinality, missing rate, JS divergence versus the previous
   window, and JS divergence versus the first (reference) window.

   :param df: The dataset to analyse.
   :type df: pandas.DataFrame
   :param time_col: Column name used to sort the data before windowing, or
                    ``None`` to use the existing row order.
   :type time_col: str or None
   :param cat_columns: Categorical column names to include. Numeric columns
                       in this list are skipped.
   :type cat_columns: list[str]
   :param window_size: Number of rows per window.
   :type window_size: int
   :param step_size: Number of rows to advance between consecutive windows.
   :type step_size: int
   :returns: One row per (window, feature) pair with fields: ``window_id``,
             ``window_start``, ``Feature``, ``Mode Frequency (%)``,
             ``Entropy (bits)``, ``Norm. Entropy``, ``Cardinality (%)``,
             ``Missing Rate (%)``, ``JS Div (vs prev)``, ``JS Div (vs ref)``.
             Returns an empty DataFrame when fewer windows than ``window_size``
             rows exist.
   :rtype: pandas.DataFrame

.. py:function:: display_ts_stability_report(df, num_columns, cat_columns)

   Render the Time-Series Feature Stability section in the Streamlit app.

   Exposes a window-configuration panel where the user selects a time column
   (or row order), window size, and step size. Then displays:

   * A colour-coded drift summary table for numerical features with average
     KS statistic and maximum PSI across all windows.
   * A bar chart of average KS statistics per numerical feature.
   * Per-feature drill-down charts: mean ± std band, skewness/kurtosis over
     time, KS/PSI drift metrics, and missing rate (numerical).
   * A colour-coded drift summary table for categorical features with average
     JS divergence and maximum JS divergence versus the reference window.
   * A bar chart of average JS divergence per categorical feature.
   * Per-feature drill-down charts: Shannon entropy, mode frequency, JS
     divergence, and missing rate (categorical).

   Drift label thresholds (numerical — KS statistic):

   .. list-table::
      :header-rows: 1

      * - Label
        - KS range
      * - Stable
        - < 0.05
      * - Moderate
        - 0.05 – 0.09
      * - Drifting
        - 0.10 – 0.19
      * - High Drift
        - ≥ 0.20

   Drift label thresholds (categorical — JS divergence):

   .. list-table::
      :header-rows: 1

      * - Label
        - JS range
      * - Stable
        - < 0.05
      * - Moderate
        - 0.05 – 0.14
      * - Drifting
        - 0.15 – 0.29
      * - High Drift
        - ≥ 0.30

   :param df: The dataset to analyse.
   :type df: pandas.DataFrame
   :param num_columns: Numerical column names.
   :type num_columns: list[str]
   :param cat_columns: Categorical column names.
   :type cat_columns: list[str]
