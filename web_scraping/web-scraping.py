from bs4 import BeautifulSoup
import asyncio
from functions import fetchMatchDetails
from functions import writeData
import os
from pyppeteer import launch
from utils import get_browser_path
from functions import fetchMatchResults
import datetime


async def writeStatsMatches(season, page=None):

    with open("matches.html", "r") as file:
        soup = BeautifulSoup(file,features="html.parser")

    matches = soup.find_all(class_="match-fixture")    
    matchesData = []


    for match in matches:
        
        names_match = match.find_all(class_="match-fixture__short-name")
        score_match = match.find_all(class_="match-fixture__score")[0].text

        team1 = names_match[0].text.replace('\n', '').replace('\r', '').replace('\t', '').strip().upper()
        team2 = names_match[1].text.replace('\n', '').replace('\r', '').replace('\t', '').strip().upper()
        link ="https:"+ match.div["data-href"].replace('\n', '').replace('\r', '').replace('\t', '')
        matchData = {
            "home": team1,
            "away": team2,
            "home_goals": score_match.split("-")[0].strip(),
            "away_goals": score_match.split("-")[1].strip(),
            "link": link
        }
        matchesData.append(matchData)


    failed = []
    index = 0
    for match in matchesData:
        print(f"({index+1}):  ",end="")
        try:
            await fetchMatchDetails(match["link"], page)  # esta funcion escribe e el archivo temp-match-stats.html      
            await writeData(match["home"], match["away"], match["home_goals"], match["away_goals"], season) # esta funcion lee el archivo temp-match-stats.html y escribe en el archivo matches.csv
        except Exception as e:
            print(f"Error: {e}")
            failed.append(match)
            continue
        index += 1
            
        
    print("match stats failed (", len(failed), ")")	
    for fail in failed:

        print(fail["home"],"  ", fail["away"],"   ", fail["link"],"  trying again...", end=" ")
        

        # se vuelven a intentar obtener las estadisticas de los partidos que fallaron
        try:
            await fetchMatchDetails(fail["link"], page)        
            await writeData(fail["home"], fail["away"], fail["home_goals"], fail["away_goals"], season)
        except Exception as e:
            print(f"Error: {e}")
            continue
        print("\n")


async def main():
    if not get_browser_path():
        print("No se encontró el navegador")
        return

    
    currentYear = datetime.datetime.now().year
    amountOfSeasonsToScrape = 4
    year = currentYear - amountOfSeasonsToScrape+1
    seasons = [ f"{currentYear-i}-{str(currentYear-i+1)[2:]}" for i in range(amountOfSeasonsToScrape)]
    browser = await launch(executablePath=get_browser_path(), headless=False, ignoreHTTPSErrors = True, autoClose=False)
    page = await browser.newPage()

    await page.goto("https://www.premierleague.com/", {'waitUntil':['load']})
    try:
        await page.waitForSelector("#onetrust-accept-btn-handler", timeout=3000)
        await page.querySelectorEval("#onetrust-accept-btn-handler", "node => node.click()") # acepta las cookies
    except Exception as e:
        print("no se encontró el selector de cookies")

    
    for season in reversed(seasons):

        # validar si ya existen los datos de la temporada, sino entonces se va a la pagina de la temporada

        if os.path.exists(f"pruebas/{season}/matches.csv") and year != datetime.datetime.now().year:
            print(f"Ya existen los datos de la temporada {season}")
            year += 1
            continue
        
        print(f"\tSeason: {season}")
        print(page)
        await fetchMatchResults(year, page)
        await writeStatsMatches(season, page)
        year += 1

    await browser.close()

        # falta agregar condicion del año actual, si es el año actual entonces verifica el ultimo partido 
        # que tiene registrado y busca partidos nuevos a partir de ese partido


asyncio.run(main())

