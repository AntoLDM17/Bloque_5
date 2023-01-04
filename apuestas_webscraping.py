import requests #Request para conseguir el html de la pagina
from bs4 import BeautifulSoup 
from fpdf import FPDF #Para crear el pdf
import pandas as pd
import matplotlib.pyplot as plt
import warnings


warnings.filterwarnings('ignore')


def extract_ws(link):
    #Conseguimos el html de la pagina
    r = requests.get(link) 
    #Lo parseamos con BS4
    soup = BeautifulSoup(r.text,'lxml')
    return soup

def transform_ws(soup):
    #Para conseguir el nombre de los partidos
    partidos = soup.find_all('div', class_="w-full xl:w-2/5 flex justify-center items-center py-4")

    #Creamos una lista con partidos cada partido es una lista con los equipos separados por 1X2 así podremos acceder a los equipos por separado
    lista_partidos = []
    for partido in partidos:
        lista_partidos.append(partido.text.replace('\n','').split('1X2'))
   

    #Tenemos una lista de listas, cada lista es un partido con los equipos
    #Ahora añadimos los ganadores a cada lista
    ganadores = soup.find_all('span', class_='flex justify-center items-center h-7 w-6 rounded-md font-semibold bg-primary-green text-white mx-1')
    lista_ganadores = [ganador.text for ganador in ganadores]
    

    for i in range(len(lista_partidos)):
        lista_partidos[i].append(lista_ganadores[i])
    return lista_partidos


def load_ws(lista_partidos, team):
    for partido in lista_partidos:
        if team in partido:
            hoy_no_juega = False
            if partido[2] == '1':
                ganador = partido[0]
            else:
                ganador = partido[1]
            print('En el partido',partido[0],'vs',partido[1],'el ganador es', ganador)
        else:
            hoy_no_juega = True
    if hoy_no_juega:
        print('El equipo',team,'no juega hoy. Inténtalo mañana.')
        



def extract_api(url_players,url_team, url_info, headers):
    response = requests.get(url_players, headers=headers).json()
    players_df = pd.DataFrame(response)
    response = requests.get(url_team, headers=headers).json()
    team_stats = pd.DataFrame(response)
    response = requests.get(url_info, headers=headers).json()
    players_info = pd.DataFrame(response)
    return players_df, players_info, team_stats


def transform_api(players_df, players_info, team_stats):
    
    #Sacar los datos de los jugadores
    players = players_df[['Name', 'Position', 'Games', 'Minutes', 'Points', 'OffensiveRebounds', 'DefensiveRebounds', 'Rebounds', 'Assists', 'Steals', 'BlockedShots', 'Turnovers', 'PersonalFouls']]
    players['Player [Pos]'] = players['Name'] + ' [' + players['Position'] + ']'
    players = players.drop(['Name', 'Position'], axis=1)
    players = players[['Player [Pos]', 'Games', 'Minutes', 'Points', 'OffensiveRebounds', 'DefensiveRebounds', 'Rebounds', 'Assists', 'Steals', 'BlockedShots', 'Turnovers', 'PersonalFouls']]
    #Cambiar nombres de columnas a abreviaturas, para que no se vea tan largo
    players = players.rename(columns={'Player [Pos]': 'Player', 'Games': 'G', 'Minutes': 'Min', 'Points': 'Pts', 'OffensiveRebounds': 'OR', 'DefensiveRebounds': 'DR', 'Rebounds': 'Rb', 'Assists': 'A', 'Steals': 'St', 'BlockedShots': 'Bl', 'Turnovers': 'TO', 'PersonalFouls': 'PF'})


    #Sacar los datos de los jugadores
    stats = players_df[['FieldGoalsMade', 'FieldGoalsAttempted', 'FieldGoalsPercentage', 'ThreePointersMade', 'ThreePointersAttempted', 'ThreePointersPercentage', 'TwoPointersMade', 'TwoPointersAttempted', 'TwoPointersPercentage', 'FreeThrowsMade', 'FreeThrowsAttempted', 'FreeThrowsPercentage', 'PlayerEfficiencyRating']]
    #Cambiar nombres de columnas a abreviaturas, para que no se vea tan largo
    stats = stats.rename(columns={'FieldGoalsMade': 'FGM', 'FieldGoalsAttempted': 'FGA', 'FieldGoalsPercentage': 'FG%', 'ThreePointersMade': '3PM', 'ThreePointersAttempted': '3PA', 'ThreePointersPercentage': '3P%', 'TwoPointersMade': '2PM', 'TwoPointersAttempted': '2PA', 'TwoPointersPercentage': '2P%', 'FreeThrowsMade': 'FTM', 'FreeThrowsAttempted': 'FTA', 'FreeThrowsPercentage': 'FT%', 'PlayerEfficiencyRating': 'PER'})
    #Añadir columna de nombre de jugador
    stats['Player'] = players_df['Name']
    #Cambiar el orden de las columnas para que quede más ordenado
    stats = stats[['Player', 'FGM', 'FGA', 'FG%', '3PM', '3PA', '3P%', '2PM', '2PA', '2P%', 'FTM', 'FTA', 'FT%', 'PER']]

    # Hacer un gráfico de barras de los puntos por jugador usando la librería matplotlib
    # Se debe incluir un título, etiquetas en los ejes y una leyenda
    # Se debe guardar el gráfico en un archivo .png

    # Primero, creamos un dataframe con los puntos de cada jugador
    puntos = pd.DataFrame()
    puntos['Player'] = players_df["Name"] 
    puntos['Pts'] = players_df['Points']

    # Ahora, ordenamos el dataframe por puntos de mayor a menor
    puntos = puntos.sort_values(by='Pts', ascending=False)

    # Creamos el gráfico de barras
    plt.figure(figsize=(10, 6))
    plt.bar(puntos['Player'], puntos['Pts'], color='blue')
    plt.title('Points per player')
    plt.xlabel('Player')
    plt.ylabel('Points')
    plt.xticks(rotation=30)
    plt.savefig('points.png')

    # Hacer un gráfico de barras apiladas de los rebotes (OffensiveRebounds y DefensiveRebounds) por jugador usando la librería matplotlib
    # Se debe incluir un título, etiquetas en los ejes y una leyenda
    # Se debe guardar el gráfico en un archivo .png

    # Primero, creamos un dataframe con los rebotes ofensivos y defensivos de cada jugador
    rebotes = pd.DataFrame()
    rebotes['Player'] = players_df["Name"]
    rebotes['OR'] = players['OR']
    rebotes['DR'] = players['DR']

    # Ahora, ordenamos el dataframe por rebotes ofensivos de mayor a menor
    rebotes = rebotes.sort_values(by='OR', ascending=False)

    # Creamos el gráfico de barras apiladas
    plt.figure(figsize=(10, 6))
    plt.bar(rebotes['Player'], rebotes['OR'], color='blue', label='Offensive Rebounds')
    plt.bar(rebotes['Player'], rebotes['DR'], color='red', label='Defensive Rebounds', bottom=rebotes['OR'])
    plt.title('Rebounds per player')
    plt.xlabel('Player')
    plt.ylabel('Rebounds')
    plt.xticks(rotation=30)
    plt.legend()
    plt.savefig('rebounds.png')

    # Hacer un gráfico de columnas de asistencias (A) por jugador usando la librería matplotlib
    # Se debe incluir un título, etiquetas en los ejes y una leyenda
    # Se debe guardar el gráfico en un archivo .png

    # Primero, creamos un dataframe con las asistencias de cada jugador
    asistencias = pd.DataFrame()
    asistencias['Player'] = players_df["Name"]
    asistencias['A'] = players['A']

    # Ahora, ordenamos el dataframe por asistencias de mayor a menor
    asistencias = asistencias.sort_values(by='A', ascending=False)

    # Creamos el gráfico de columnas
    plt.figure(figsize=(10, 6))
    plt.bar(asistencias['Player'], asistencias['A'], color='blue')
    plt.title('Assists per player')
    plt.xlabel('Player')
    plt.ylabel('Assists')
    plt.xticks(rotation=30)
    plt.savefig('assists.png')


    #Debido a que el equipo de los Lakers no es el primero en la lista, se debe ordenar por Key y acceder a la decimocuarta fila
    team_stats = team_stats.sort_values(by='Key').head(14).tail(1)
    
    # Creamos una lista con los nombres de las columnas que nos interesan del dataframe de team_stats
    lakers = pd.DataFrame()
    lakers['Category'] = ['Conference', 'Division', 'Wins', 'Losses', 'Win Percentage', 'Home Wins', 'Home Losses', 'Away Wins', 'Away Losses', 'Points Scored Per Game', 'Points Received Per Game', 'Streak', 'Conference Rank']
    lakers['Data'] = team_stats[['Conference', 'Division', 'Wins', 'Losses', 'Percentage', 'HomeWins', 'HomeLosses', 'AwayWins', 'AwayLosses', 'PointsPerGameFor', 'PointsPerGameAgainst', 'Streak', 'ConferenceRank']].values.tolist()[0]

    
    #Creamos una gráfica circular de el porcentaje de jugadores por posición
    #Primero, creamos un dataframe con los datos que nos interesan
    posiciones = pd.DataFrame()
    posiciones['Posicion'] = players_info['Position'].value_counts().index
    posiciones['Jugadores'] = players_info['Position'].value_counts().values

    #Ahora, creamos la gráfica
    plt.figure(figsize=(10, 6))
    plt.pie(posiciones['Jugadores'], labels=posiciones['Posicion'], autopct='%1.1f%%')
    plt.title('Players per position')
    plt.savefig('posiciones.png')

    return players, stats, lakers

def load_api(players, stats, lakers):
    
    #Creamos el PDF y para que se vea bien, lo ponemos en horizontal, con tamaño A4 y coordenadas en milímetros.
    pdf = PDF('L', 'mm', 'A4')
    # Establecemos los márgenes del documento
    pdf.set_margins(20, 25, 20)
    pdf.set_auto_page_break(auto = True, margin = 26)
    # Contamos las páginas del documento a medida que se crean
    pdf.alias_nb_pages()
    # Especificamos el autor del documento
    pdf.set_author('Antonio Lorenzo Díaz-Meco')

    # Creamos la portada del informe llamando a la función creada
    pdf.cover()

    # Creamos una página con la tabla a nivel de equipo
    pdf.add_page()
    pdf.lakers(lakers)

    # Creamos una página con la tabla a nivel de jugador
    pdf.add_page()
    pdf.set_y(16)
    # Establecemos un título
    pdf.set_text_color(0, 120, 140)
    pdf.set_font('times', 'B', 14)
    pdf.cell(0, 10, 'Stats of each player during Season 22/23', align = 'C')
    pdf.ln(19)
    # Incluimos un párrafo explicativo
    pdf.set_text_color(0)
    pdf.set_font('times', '', 12)
    text_players = 'In this section, we can see the stats of each player during the 22/23 season. The stats are: Games(G), Minutes(Min), Points(Pts), Offensive Rebounds(OR), Defensive Rebounds(DR), Rebounds(Rb), Assists(A), Steals(St), Blocks(Bl), Turnovers(TO) and Personal Fouls(PF). ' 
    pdf.multi_cell(246, 5.5, text_players, align = 'J')
    pdf.ln(7)
    # Adjuntamos la tabla correspondiente llamando a la función creada con el dataframe de jugadores
    pdf.draw_table(players)

    # Creamos una página con la tabla a nivel de tiros
    pdf.add_page()
    pdf.set_y(16)
    # Establecemos un título
    pdf.set_text_color(0, 120, 140)
    pdf.set_font('times', 'B', 14)
    pdf.cell(0, 10, 'Stats of the players in every type of shots on 2022/23 season', align = 'C')
    pdf.ln(19)
    # Incluimos un párrafo explicativo
    pdf.set_text_color(0)
    pdf.set_font('times', '', 12)
    text_shots = 'In this section, we can see the stats of each player during the 22/23 season. The stats are: Field Goals Made (FGM), Field Goals Attempted (FGA), Field Goal Percentage (FG%), 3 Points Made (3PM), 3 Points Attempted (3PA), 3 Points Percentage (3P%), 2 Points Made (2PM), 2 Points Attempted (2PA), 2 Points Percentage (2P%), Free Throws Made (FTM), Free Throws Attempted (FTA), Free Throws Percentage (FT%), and Player Efficiency Rating (PER).'
    pdf.multi_cell(246, 5.5, text_shots, align = 'J')
    pdf.ln(7)
    # Adjuntamos la tabla correspondiente llamando a la función creada con el datagrame de tiros
    pdf.draw_table(stats)


    #Creamos una página adjuntando la información de los puntos por jugador llamando a la función creada
    pdf.add_page()
    pdf.points()

    #Creamos una página adjuntando la información de los rebotes por jugador llamando a la función creada
    pdf.add_page()
    pdf.rebounds()

    #Creamos una página adjuntando la información de los asistencias por jugador llamando a la función creada
    pdf.add_page()
    pdf.assists()

    #Creamos una página adjuntando la correlación entre el salario y el impacto en el equipo llamando a la función creada
    pdf.add_page()
    pdf.percentage_position()

    # Exportamos el documento en formato PDF
    pdf.output('Stats_Report_NBA.pdf')


#Hacer lo mismo pero con Los Angeles Lakers en vez de Charlotte Hornets
class PDF(FPDF):
    def cover(self):
        self.add_page()
        # Establecemos un título
        self.set_text_color(0, 120, 140)
        self.set_font('times', 'B', 14)
        self.cell(0, 10, 'Los Angeles Lakers', align = 'C')
        self.ln(19)
        
        # Incluimos un párrafo explicativo
        self.set_text_color(0)
        self.set_font('times', '', 12)
        cover_text = 'In this Executive Report it is shown the statistics of Los Angeles Lakers in the 2022/23 season. Also more information about the team and the players is provided. The data is obtained from the website https://api.sportsdata.io. The data is up to date.  '
        self.multi_cell(247, 5.5, cover_text, align = 'J')
        self.ln(7)

        #Adjuntamos una imagen con el logo
        self.image('los_angeles_lakers_logo.png', x = 20, y = 80, w = 130)
        self.image('los_angeles_lakers_jugadores.jpg', x = 150, y = 80, w = 130)

        #Ponemos el nombre del autor
        self.set_text_color(100, 100, 100)
        self.set_font('times', 'B', 12)
        self.cell(0, 10, 'Antonio Lorenzo Díaz-Meco', align = 'C')

    
    def draw_table(self, dataframe):
        # Añadir los encabezados de las columnas
        for column in dataframe.columns:
            if column == dataframe.columns[0]:
                self.cell(247/len(dataframe.columns)*2.5, 5.5, column, border = 1, align = 'C')
            else:
                self.cell(247/len(dataframe.columns), 5.5, column, border = 1, align = 'C')
        self.ln(5.5)
        # Añadir los datos de cada fila
        for index, row in dataframe.iterrows():
            for i in range(len(row)):
                if i == 0:
                    self.cell(247/len(dataframe.columns)*2.5, 5.5, str(row[i]), border = 1, align = 'C')
                else:
                    self.cell(247/len(dataframe.columns), 5.5, str(row[i]), border = 1, align = 'C')
            self.ln(5.5)
        

        
    
    def lakers(self, lakers):
        
        #Hacer lo mismo pero dando color a la tabla
        self.set_y(16)
        # Establecemos un título
        self.set_text_color(0,120,140)
        self.set_font('times', 'B', 14)
        self.cell(0, 10, 'Los Angeles Lakers team stats this season', align = 'C')
        #Añadimos un párrafo explicativo
        self.ln(19)
        self.set_text_color(0)
        self.set_font('times', '', 12)
        text_lakers = 'On this page you can see the stats of the Los Angeles Lakers team this season. The stats are shown in the following table. '
        self.multi_cell(247, 5.5, text_lakers, align = 'J')
        self.ln(7)


        #Ahora creamos la tabla con los datos de los Lakers
        self.set_fill_color(0, 120, 140)
        self.set_text_color(255)
        for column in lakers.columns:
            self.cell(247/len(lakers.columns), 5.5, column, border = 1, align = 'C', fill = True)
        self.ln(5.5)
        # Añadir los datos de cada fila
        self.set_fill_color(255)
        self.set_text_color(0)
        for index, row in lakers.iterrows():
            for i in range(len(row)):
                self.cell(247/len(lakers.columns), 5.5, str(row[i]), border = 1, align = 'C', fill = True)
            self.ln(5.5)
        self.ln(7)



    def points(self):
        #Vamos a crear una página con la gráfica de puntos por jugador de los Lakers en la temporada 2022/23
        # Establecemos un título
        self.set_text_color(0,120,140)
        self.set_font('times', 'B', 14)
        self.cell(0, 10, 'Los Angeles Lakers points per player this season', align = 'C')
        self.set_text_color(0)
        self.set_font('times', '', 12)
        text_points = 'On this page you can see the points per player of the Los Angeles Lakers team this season. The stats are shown in the following graph. '
        self.image('points.png', x = 20, y = 40, w = 200)
        self.ln(19)
        self.multi_cell(246, 5.5, text_points, align = 'C')
        self.ln(19)
    
    def percentage_position(self):
        #Vamos a crear una página que contenga un gráfico circular con el porcentaje de jugadores por posición
        self.set_y(16)
        # Establecemos un título
        self.set_text_color(0,120,140)
        self.set_font('times', 'B', 14)
        self.cell(0, 10, 'Percentage of players per position', align = 'C')
        self.set_text_color(0)
        self.set_font('times', '', 12)
        self.set_y(25)
        self.set_x(20)
        self.image('posiciones.png', x = 40, y = 40, w = 200)
        #Ahora añadiremos un párrafo explicativo de la gráfica
        text_percentage = 'On this page you can see the percentage of players per position of the Los Angeles Lakers team this season. The stats are shown in the following graph. Each position is represented by a different color. PG means Point Guard, SG means Shooting Guard, SF means Small Forward, PF means Power Forward and C means Center. '
        self.multi_cell(246, 5.5, text_percentage, align = 'C')
        self.ln(19)
    
    def rebounds(self):
        #Vamos a crear una página con la gráfica de puntos por jugador de los Lakers en la temporada 2022/23
        self.set_y(16)
        # Establecemos un título
        self.set_text_color(0,120,140)
        self.set_font('times', 'B', 14)
        self.cell(0, 10, 'Los Angeles Lakers rebounds per player this season', align = 'C')
        self.set_text_color(0)
        self.set_font('times', '', 12)
        text_points = 'On this page you can see the rebounds per player of the Los Angeles Lakers team this season. The stats are shown in the following graph. '
        self.image('rebounds.png', x = 20, y = 40, w = 200)
        self.ln(19)
        self.multi_cell(246, 5.5, text_points, align = 'C')
        self.ln(19)

    def assists(self):
        #Vamos a crear una página con la gráfica de puntos por jugador de los Lakers en la temporada 2022/23
        self.set_y(16)
        # Establecemos un título
        self.set_text_color(0,120,140)
        self.set_font('times', 'B', 14)
        self.cell(0, 10, 'Los Angeles Lakers assists per player this season', align = 'C')
        self.set_text_color(0)
        self.set_font('times', '', 12)
        text_points = 'On this page you can see the assists per player of the Los Angeles Lakers team this season. The stats are shown in the following graph. '
        self.image('assists.png', x = 20, y = 40, w = 200)
        self.ln(19)
        self.multi_cell(246, 5.5, text_points, align = 'C')
        self.ln(19)


def ETL_ws():
    team = 'Los Angeles Lakers'
    link = 'https://www.sportytrader.es/pronosticos/baloncesto/usa/nba-306/'
    soup = extract_ws(link)
    lista_partidos = transform_ws(soup)
    load_ws(lista_partidos,team)

def ETL_api():
    season = 2023
    team = 'LAL'
    URL_PLAYERS = f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/{season}/{team}'
    URL_INFO = "https://api.sportsdata.io/v3/nba/scores/json/Players/LAL"
    URL_TEAM = "https://api.sportsdata.io/v3/nba/scores/json/Standings/2023"
    api_key = 'XXXXXXXXXXXXXXXXXXXXXXXXXX' # Se debe incluir aquí la clave del usuario
    headers = {'Ocp-Apim-Subscription-Key': api_key}

    players_df, players_info, team_stats = extract_api(URL_PLAYERS,URL_TEAM,URL_INFO, headers)
    players, stats, lakers = transform_api(players_df, players_info, team_stats)
    load_api(players, stats, lakers)


if __name__ == '__main__':
    ETL_ws()
    ETL_api()

































