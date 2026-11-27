### Streamlit app: https://nylandgit-ind320-repo.streamlit.app/

# README IND320 Energy Data Explorer

This repo is used in academic work related to the course IND320 Data to Decision at NMBU. It is connected to the Streamlit app linked above, in which data from various sources is compiled and analysed as a means to guide executive decisionmaking.

## Oblig folder houses relevant project files:
* /.streamlit: Folder necessary for Streamlit app.
* /Innleveringsfiler: .html versions of .ipynb files in /notebooks.
* /modules: .py modules for Streamlit app functionality.
* /notebooks: .ipynb files w/ relevant task solutions, handed in as part of the course.
* /pages: .py files for Streamlit app pages.
* /shapefiles: Shapefiles for relevant geography.

## Data Sources:
* NVE's Magasinstatistikk API found at: https://biapi.nve.no/magasinstatistikk/api/Magasinstatistikk/HentOffentligData
* ENTSO-E's API found through: https://documenter.getpostman.com/view/7009892/2s93JtP3F6
* Open-Meteo's Historical API found at: https://open-meteo.com/en/docs/historical-forecast-api
* NVE Atlas shapefiles found through: https://atlas.nve.no/vertigisstudio/web/?app=e0080b63a0c445a5a47e6d8c3b53ad8c
* MongoDB Atlas: Database used to store data, written to by project_work_part2.ipynb, retrieved by Streamlit app.

## Features

- **Interactive area selection** for EL, NO, and VASS areas, with shared year
  and month ranges across pages.
- **Reservoir maps** based on the NVE Magasinstatistikk filling ratio.
- **Reservoir data plots** for metrics and dates selected by the user.
- **Cross-border flow charts** using ENTSO-E data stored in MongoDB.
- **Meteorological data retrieval** from Open-Meteo for sampled locations within
  EL areas.
- **STL analysis and spectrograms** for reservoir time series.
- **Meteorological anomaly analysis** using SATV statistical process control and
  Local Outlier Factor.
- **Reservoir filling forecasts** based on lag features and River machine-learning
  models.
- **Rolling correlation analysis** between reservoir filling ratios and
  precipitation or temperature.

## Requirements

- Python 3.12
- Internet access for NVE, Open-Meteo, and MongoDB-backed data

The project dependencies are listed in `pyproject.toml` and `requirements.txt`.

## Run locally

From the `Oblig` directory, create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the application:

```powershell
streamlit run app.py
```

The app uses MongoDB for cross-border electricity flow data. Configure the
password in `.streamlit/secrets.toml`:

```toml
psw = "your-mongodb-password"
```

Do not commit `.streamlit/secrets.toml` or any other credentials.
