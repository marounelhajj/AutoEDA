
System Architecture
===================

Overview
--------

AutoEDA follows a modular architecture.

Project Structure
-----------------

.. code-block:: text

   AutoEDA/
   │
   ├── main.py
   ├── home_page.py
   ├── data_analysis_functions.py
   ├── data_preprocessing_function.py
   ├── feature_stability_functions.py
   └── docs/

Module Responsibilities
-----------------------

main.py
^^^^^^^^

Application entry point.

home_page.py
^^^^^^^^^^^^

User interface and navigation.

data_analysis_functions.py
^^^^^^^^^^^^^^^^^^^^^^^^^^

Exploratory data analysis functions : 
* Load data 
* Separate features into numerical and categorical
* Display data overview
* Display missing values
* Display statistics visualization
* Display data types
* Search for specific column
* Display individual feature distribution
* Display scatter plot of two numeric features
* Categorical variable analysis
* Feature exploration of numerical variables and 
* Categorical vs Numerical variable analysis

data_preprocessing_function.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data cleaning and transformation operations:
* Remove selected columns
* Remove selected rows with missing data
* Fill missing data with mean or median or mode
* Encode using One Hot Encoding or Label Encoding
* Scale using StandardScaler() or MinMaxScaler()
* Detect outliers using IQR method
* Remove outliers
* Transform outliers by replacing their values with the value of the median of non-outliers
  

feature_stability_functions.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Feature stability calculations:
* Compute outlier rate using IQR method
* Compute stability score for numerical features
* Compute stability score for categorical features
* Build Bar Chart
* Build Radar Chart
* Display Stability Report