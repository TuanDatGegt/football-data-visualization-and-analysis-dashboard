import pandas as pd
import numpy as np

def formation_data(df):
    """
    Docstring for formation_data: Create DataFrame formation_data from match_data

    df: DataFrame have data with JSON list columns team1.formation, team2.formation,.. etc

    return: pd.DataFrame containing all formations of all matches: matchID, teamID, playerID, lineup, substitutionIn, substitutionOut, minuteStart, minuteEnd, minutePlayed
    """
    lst_formations = []
    for idx, row in df.iterrows():
        match_id = row['wyId']
        for team_prefix in ['team1', 'team2']:
            team_id = row[f'{team_prefix}.teamId']

            #Get list player from lineup and bench
            lineup_Players = [p['playerId'] for p in row[f'{team_prefix}.formation.lineup']]
            bench_Players = [p['playerId'] for p in row[f'{team_prefix}.formation.bench']]

            #Player in lineup
            df_lineup = pd.DataFrame({
                'playerId': lineup_Players,
                'lineup': 1
            })

            #Player in bench
            df_bench = pd.DataFrame({
                'playerId': bench_Players,
                'lineup': 0
            })

            df_team = pd.concat([df_lineup, df_bench], axis=0)
            df_team['matchId'] = match_id
            df_team['teamId'] = team_id


            #Substitutions
            subs = row.get(f'{team_prefix}.formation.substitutions', [])
            if subs is None or subs == 'null':
                subs = []
            
            player_in = [s['playerIn'] for s in subs]
            player_out = [s['playerOut'] for s in subs ]
            sub_minute = [s['minute'] for s in subs]

            df_in = pd.DataFrame({
                'playerId': player_in,
                'subtituteIn': 1,
                'minuteStart': sub_minute
            })
            df_out = pd.DataFrame({
                'playerOut': player_out,
                'substituteOut': 1,
                'minuteEnd': sub_minute
            })

            