import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy import stats


def remove_selected_columns(df, columns_remove):
    """Drop the specified columns from a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    columns_remove : list of str
        Column names to drop.

    Returns
    -------
    pandas.DataFrame
        Dataframe with the specified columns removed.
    """
    return df.drop(columns=columns_remove)

def remove_rows_with_missing_data(df, columns):
    """Drop rows that contain missing values in the specified columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    columns : list of str
        Column names to check for null values. Only rows with nulls in
        these columns are removed; other rows are preserved.

    Returns
    -------
    pandas.DataFrame
        Dataframe with the affected rows removed, or ``None`` if
        ``columns`` is empty.
    """
    if columns:
        df = df.dropna(subset=columns)
        return df

def fill_missing_data(df, columns, method):
    """Impute missing values in the specified columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe (modified in-place).
    columns : list of str
        Column names whose null values will be filled.
    method : {'mean', 'median', 'mode'}
        Imputation strategy to apply to each column.

    Returns
    -------
    pandas.DataFrame
        Dataframe with missing values filled according to ``method``.
    """
    for column in columns:
        if method == 'mean':
            df[column].fillna(df[column].mean(), inplace=True)
        elif method == 'median':
            df[column].fillna(df[column].median(), inplace=True)
        elif method == 'mode':
            mode_val = df[column].mode().iloc[0]
            df[column].fillna(mode_val, inplace=True)
    return df


def one_hot_encode(df, columns):
    """Apply one-hot encoding to the specified categorical columns.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    columns : list of str
        Categorical column names to encode. Each column is replaced by
        binary indicator columns prefixed with the original column name.
        The first dummy is kept (``drop_first=False``).

    Returns
    -------
    pandas.DataFrame
        Dataframe with the original columns replaced by dummy variables.
    """
    df = pd.get_dummies(df, columns=columns, prefix=columns, drop_first=False)
    return df


def label_encode(df, columns):
    """Apply label encoding to the specified categorical columns.

    Each unique string value is mapped to an integer using
    ``sklearn.preprocessing.LabelEncoder``. The encoding is fit and
    applied per column independently.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe (modified in-place).
    columns : list of str
        Categorical column names to encode.

    Returns
    -------
    pandas.DataFrame
        Dataframe with the specified columns replaced by integer labels.
    """
    label_encoder = LabelEncoder()
    for col in columns:
        df[col] = label_encoder.fit_transform(df[col])
    return df



def standard_scale(df, columns):
    """Standardise columns to zero mean and unit variance.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe (modified in-place).
    columns : list of str
        Numerical column names to scale.

    Returns
    -------
    pandas.DataFrame
        Dataframe with the specified columns standardised using
        ``sklearn.preprocessing.StandardScaler``.
    """
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df

def min_max_scale(df, columns, feature_range=(0, 1)):
    """Scale columns to a specified minimum–maximum range.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe (modified in-place).
    columns : list of str
        Numerical column names to scale.
    feature_range : tuple of (float, float), optional
        Desired output range, by default ``(0, 1)``.

    Returns
    -------
    pandas.DataFrame
        Dataframe with the specified columns scaled using
        ``sklearn.preprocessing.MinMaxScaler``.
    """
    scaler = MinMaxScaler(feature_range=feature_range)
    df[columns] = scaler.fit_transform(df[columns])
    return df

def detect_outliers_iqr(df, column_name):
    """Detect outliers in a column using the IQR method.

    Values below ``Q1 - 1.5 * IQR`` or above ``Q3 + 1.5 * IQR`` are
    considered outliers.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    column_name : str
        Name of the numerical column to inspect.

    Returns
    -------
    list
        Sorted list of outlier values found in the column.
    """
    data = df[column_name]
    q25, q50, q75 = np.percentile(data, [25, 50, 75])
    iqr = q75 - q25
    lower_bound = q25 - 1.5 * iqr
    upper_bound = q75 + 1.5 * iqr
    outliers = [x for x in data if x < lower_bound or x > upper_bound]
    outliers.sort()
    return outliers



def detect_outliers_zscore(df, column_name):
    """Detect outliers in a column using the Z-score method.

    Values whose absolute Z-score exceeds 3 are considered outliers.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.
    column_name : str
        Name of the numerical column to inspect.

    Returns
    -------
    list
        List of outlier values found in the column.
    """
    data = df[column_name]
    z_scores = np.abs(stats.zscore(data))
    threshold = 3  
    outliers = [data[i] for i in range(len(data)) if z_scores[i] > threshold]
    return outliers


def remove_outliers(df, column_name, outliers):
    """
    Remove rows containing outlier values from a specified column.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.

    column_name : str
        Name of the column in which outliers were detected.

    outliers : list
        List of values identified as outliers.

    Returns
    -------
    pandas.DataFrame
        A dataframe with all rows containing outlier values removed.

    Notes
    -----
    Rows are removed if their value in the specified column
    appears in the provided outliers list.
    """
    return df[~df[column_name].isin(outliers)]
def transform_outliers(df, column_name, outliers):
    """
    Replace outlier values with the median of non-outlier observations.

    Parameters
    ----------
    df : pandas.DataFrame
        Input dataframe.

    column_name : str
        Name of the column containing outliers.

    outliers : list
        List of values identified as outliers.

    Returns
    -------
    pandas.DataFrame
        Dataframe with outlier values replaced by the median
        of the non-outlier values.

    Notes
    -----
    The median is computed using only the values that are
    not considered outliers. All detected outliers are then
    replaced with this median value.
    """
    non_outliers = df[~df[column_name].isin(outliers)]
    median_value = non_outliers[column_name].median()
    df.loc[df[column_name].isin(outliers), column_name] = median_value
    return df
