Installation
============

This section will describe how to install and run AutoEDA.
AutoEDA can be set up in two ways: using Docker (recommended) or a local Python envi- ronment. The full source code is available on the GitHub repository: https://github.com/ marounelhajj/AutoEDA
 
* Option 1 — Docker (recommended): Requires Docker Desktop.

 git clone https://github.com/marounelhajj/AutoEDA.git 
 
 cd AutoEDA
 
 docker compose up --build
 
 Then open http://localhost:8501 in your browser.

* Option 2 — Local Python: Requires Python 3.9+.

 git clone https://github.com/marounelhajj/AutoEDA.git 
 
 cd AutoEDA
 
 pip install -r requirements.txt 
 
 python -m streamlit run main.py
 
 Then open http://localhost:8501 in your browser.
