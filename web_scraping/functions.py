import csv
from bs4 import BeautifulSoup
import os
import asyncio
import datetime


scrollDown = """()=>{

    let footer = document.querySelector(".mainFooter");

    if(footer){
    
        footer.parentNode.removeChild(footer); // elimina el footer de la pagina
    }

    function scrollToMiddle() {
        const scrollHeight = document.body.scrollHeight ;
        const clientHeight = window.innerHeight;
        const middleHeight = (scrollHeight - clientHeight) / 2;

        // Subir el scroll a media altura
        window.scrollTo({ top: middleHeight, behavior: 'smooth' });

        // Esperar 1 segundo y luego bajar hasta el fondo
        setTimeout(() => {
            window.scrollTo({ top: scrollHeight, behavior: 'smooth' });
        }, 1000);

        
    }

    setInterval(scrollToMiddle, 3000);
    
}"""


# scrollDown = """()=>{

#     const nuevo

# } """


# scrollDown = """()=>{ 

#     const scrollPosition = document.body.scrollHeight * 0.89;
# window.scrollTo(0, scrollPosition);

# // Observador para detectar cambios en el DOM
# const observer = new MutationObserver((mutations) => {
#     mutations.forEach((mutation) => {
#         mutation.addedNodes.forEach((node) => {
#             if (node.nodeType === 1 && node.classList.contains('match-fixture__container')) {
#                 // Mantener el scroll en la posición deseada
#                 window.scrollTo(0, scrollPosition);
#             }
#         });
#     });
# });

# // Configuración del observador
# observer.observe(document.body, { childList: true, subtree: true });

# } """


def isMatchAlreadyScrapped(match):

    PATH_CSV_CURRENT_SEASON = "pruebas/2024-25/matches.csv"

    if not os.path.exists(PATH_CSV_CURRENT_SEASON):
        return True # Si no existe el archivo, se asume que no se ha scrapeado nada

    lista_columna1 = []
    lista_columna2 = []

    with open(PATH_CSV_CURRENT_SEASON, "r", newline='') as file:
        lector_csv = csv.reader(file)
        next(lector_csv)

        for fila in lector_csv:
            if len(fila) >= 2:  # Asegurarse de que hay al menos dos columnas
                lista_columna1.append(fila[0])  # Primera columna
                lista_columna2.append(fila[1])  # Segunda columna

    names_match = match.find_all(class_="match-fixture__short-name")
    team1 = names_match[0].text.replace('\n', '').replace('\r', '').replace('\t', '').strip().upper()
    team2 = names_match[1].text.replace('\n', '').replace('\r', '').replace('\t', '').strip().upper()

    if team1 in lista_columna1 and team2 in lista_columna2:
        return False
    else:
        return True

    # sopa = BeautifulSoup(match, 'html.parser')
    # equipos = sopa.select('.match-fixture__short-name')
    # nombres = [equipo.get_text().upper() for equipo in equipos]

    # # este if valida que el partido no haya sido scrapeado, verificando si 
    # # los nombres de los equipos coinciden con los nombres de los equipos en el archivo matches.html y en el orden correcto
    # if nombres[0] == team1 and nombres[1] == team2:
    #     return False
    # else:
    #     return True


    



COLUMNS = [
        "DATE",
        "home", "away",
        "home_goals", "away_goals",
        "possesion_home", "possesion_away", 
        "shots_on_target_home", "shots_on_target_away",
        "shots_home", "shots_away", 
        "touches_home", "touches_away",
        "passes_home", "passes_away",
        "tackles_home", "tackles_away",
        "clearances_home", "clearances_away",
        "corners_home", "corners_away",
        "offsides_home", "offsides_away",
        "yellow_cards_home", "yellow_cards_away",
        "red_cards_home", "red_cards_away",
        "fouls_conceded_home", "fouls_conceded_away"
]

ROWS_SELECTOR = ".matchCentreStatsContainer > tr" # las filas de la tabla que contiene las estadisticas del partido
DATA_TABLE_SELECTOR = ".matchCentreStatsContainer" # la tabla que contiene las estadisticas del partido
HTML_MATCH_STATS_FILE = "temp-match-stats.html" # archivo donde se guardaran las estadisticas del partido
DATE_SELECTOR = ".mc-summary__info" # selector que contiene la fecha del partido

HTML_MATCHES_FILE = "matches.html"
MATCHES_SELECTOR = ".match-fixture"





async def existsHTMLElement(page, selector: str) -> bool:
    attemptsToFindMatches = 0
    maxAttempts = 10
    while True:
        if await page.querySelector(selector):
            return True
        else:
            attemptsToFindMatches += 1
            if attemptsToFindMatches >= maxAttempts:
                print("No se encontraron elementos con el selector: ", selector)
                return False
            await asyncio.sleep(1.5)



async def fetchMatchResults(year:int=None, page = None ,timeToSleep=5):

    url = "https://www.premierleague.com/results"
    global HTML_MATCHES_FILE
    global MATCHES_SELECTOR
    global scrollDown
    band_to_scrapt_new_data = True # se asume que se va a scrapear datos de la temporada actual

    type(page)
    await page.goto(url, {'waitUntil':['load']})
    await page.waitForSelector( ".mainFooter", timeout=15000)
    await page.evaluate(scrollDown)
    


    if not year == datetime.datetime.now().year:
        await changeSeason(year, page)
        await page.evaluate(scrollDown) # necesario volver a hacer el scroll ya que la pagina se recargó en este punto
        band_to_scrapt_new_data = False
        attempts = 0
        # await page.evaluate("()=>{ setInterval(()=>{document.querySelector('body').click()},200) }")
        while await page.evaluate("()=>{ return document.querySelectorAll('"+MATCHES_SELECTOR+"').length}") != 380 and attempts < 360:
            await asyncio.sleep(1)
            attempts += 1
    else:
        await asyncio.sleep(5)
       
    await asyncio.sleep(timeToSleep)
    try:
        await page.waitForSelector(MATCHES_SELECTOR, timeout=15000)
        matches = await page.querySelectorAllEval(MATCHES_SELECTOR, "nodes => nodes.map(n => n.outerHTML)")

        if(band_to_scrapt_new_data):
            matches = filter(isMatchAlreadyScrapped, matches)

        with open(HTML_MATCHES_FILE, "w") as file:
            for match in matches:
                file.write(match)
                file.write("\n")

    except Exception as e:
        print("No se encontraron resultados de partidos: ", e)
        with open(HTML_MATCHES_FILE, "w") as file:
            file.write("")






async def fetchMatchDetails(url=None, page=None):

    global ROWS_SELECTOR
    global DATA_TABLE_SELECTOR
    global HTML_MATCH_STATS_FILE
    global DATE_SELECTOR

    print("fetching match details: ", url)
    await page.goto(url, {'waitUntil':['load']})
    await page.evaluate("()=>{ setInterval(()=>{document.querySelector('body').click()},200) }")
    try:
        await page.waitForSelector(selector='li[role="tab"][data-tab-index="2"]', timeout=15000)
    except Exception as e:
        await page.waitForSelector(selector='li[role="tab"][data-tab-index="2"]', timeout=5000)
        
    


    
    try:

        await page.waitForSelector( ".mainFooter", timeout=15000)
        await page.evaluate(""" ()=>{ let footer = document.querySelector(".mainFooter"); if(footer){ footer.parentNode.removeChild(footer); } } """)

        #da clic para que se despliegue la tabla de estadisticas y asi carguen los datos
        await page.querySelectorEval('li[role="tab"][data-tab-index="2"]', "node => node.click()")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight/3)")
        await page.waitForSelector(DATE_SELECTOR)
        await page.waitForSelector(ROWS_SELECTOR, timeout=15000)# verifica si se cargaron las estadisticas del partido, si al menos existe una fila en la tabla esta cargada
        while not await page.evaluate("()=>{ return document.querySelectorAll('"+ROWS_SELECTOR+"').length >= 9}"): # son 11 datos pero en algunos partidos falta uno
            await asyncio.sleep(1)

        stats = await page.querySelectorAllEval(DATA_TABLE_SELECTOR, "nodes => nodes.map(n => n.outerHTML)")
        date = await page.querySelectorEval(DATE_SELECTOR, "node => node.outerHTML")
        with open(HTML_MATCH_STATS_FILE, "w") as file:
            file.write(date)
            file.write(stats[0])
    except Exception as e:

        print(f"Error fetching details for {url}: {e}")
        with open(HTML_MATCH_STATS_FILE, "w") as file:
            file.write("")




async def changeSeason(year:str=None, page=None):

    endSeason = str(int(str(year)[2:])+1)

    try:
        await page.waitForSelector(selector=f"li[data-option-name='{year}/{endSeason}']", timeout=15000)
        await asyncio.sleep(1)
        print("click al boton: ", f"li[data-option-name='{year}/{endSeason}']")
        await page.querySelectorEval(f"li[data-option-name='{year}/{endSeason}']", "node => {node.click()}")
    except Exception as e:
        print("No se encontró el selector")
    





async def writeData(HOME_TEAM, AWAY_TEAM, HOME_GOALS, AWAY_GOALS, SEASON):

    
    alternative_columns = [
        "Possession %",
        "Shots on target",
        "Shots",
        "Touches",
        "Passes",
        "Tackles",
        "Clearances",
        "Corners",
        "Offsides",
        "Yellow cards",
        "Red cards",
        "Fouls conceded"
    ] 
    
    

    with open("temp-match-stats.html", "r") as file:
        soup = BeautifulSoup(file,features="html.parser")
        soup.find(class_="mc-summary__info").find("svg").decompose()
    
    DATE = soup.find(class_="mc-summary__info").text.replace("\"","").replace("\n","").replace("\t","").replace("\r","").strip().replace(" ","-")             
    PATCH_MATCHES = f"pruebas/{SEASON}/matches.csv" # este nombre se obtiene del archivo matches.html por cada jornada


    stats_html = soup.find_all("tr")
    stats = [DATE,HOME_TEAM, AWAY_TEAM, HOME_GOALS, AWAY_GOALS]


    stats_dict = {}
    for stat_row in stats_html:
        stat_name = stat_row.find_all("p")[1].text.strip().upper()
        home_stat = stat_row.find_all("p")[0].text.strip()
        away_stat = stat_row.find_all("p")[2].text.strip()
        stats_dict[stat_name] = (home_stat, away_stat)

    # Now loop through the alternative columns and either append stats or zeros
    for column in alternative_columns:
        # Match column name with dictionary keys (converted to uppercase)
        if column.upper() in stats_dict:
            home_stat, away_stat = stats_dict[column.upper()]
            stats.append(home_stat)
            stats.append(away_stat)
        else:
            # If the stat is not found, append two zeros
            stats.append("0")
            stats.append("0")


    # cont = 0
    # for stat in stats_html:    

    #     if stat.find_all("p")[1].text.upper() == alternative_columns[cont].upper():
    #         stats.append(stat.find_all("p")[0].text) # del equipo local
    #         stats.append(stat.find_all("p")[2].text) # del equipo visitante, se salta el segundo elemento que es un separador
    #         cont += 1
    #     else:
    #         stats.append("0")
    #         stats.append("0")
        

    if not os.path.exists(PATCH_MATCHES):
        os.makedirs(os.path.dirname(PATCH_MATCHES), exist_ok=True)

    with open(PATCH_MATCHES, "a", newline='') as file:
        writer = csv.writer(file)        
        if file.tell() == 0:
            alternative_columns_new = ["DATE", "home", "away", "home_goals", "away_goals"]
            for column in alternative_columns:
                alternative_columns_new.append(column.replace(" ","_").lower()+"_home")
                alternative_columns_new.append(column.replace(" ","_").lower()+"_away")

            writer.writerow(alternative_columns_new)
        writer.writerow(stats)



