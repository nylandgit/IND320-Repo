### Streamlit app: https://nylandgit-ind320-repo.streamlit.app/

# README

This repo is used in academic work related to the course IND320 Data to Decision at NMBU. It is connected to the Streamlit app linked above, in which data from various sources is compiled and analysed as a means to guide executive decisionmaking.

## Oblig/ folder houses relevant project files:
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

## App Pages (WIP):
* Reservoirs Data: To be removed, ignore for now.
* Magasinstatistikk Data Selector and Plots: Select desired time period for Magasinstatistikk. Used in later pages.
* In-Out Flows Charts: 
