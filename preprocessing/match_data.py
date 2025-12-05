import pandas as pd
import numpy as np
import json

def parse_json_column(value):
    if isinstance(value, str):
        try:
            return json.loads(value.replace("'", '"'))
        except:
            return []
    return value

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
            lineup_raw = parse_json_column(row[f'{team_prefix}.formation.lineup'])
            bench_raw = parse_json_column(row[f'{team_prefix}.formation.bench'])

            lineup_Players = [p['playerId'] for p in lineup_raw]
            bench_Players = [p['playerId'] for p in bench_raw]

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
            subs_raw = parse_json_column(row[f'{team_prefix}.formation.substitutions'])

            if isinstance(subs_raw, float) and np.isnan(subs_raw):
                subs_raw = []
            elif subs_raw in [None, 'null', 'None', '', {}]:
                subs_raw = []
            elif not isinstance(subs_raw, list):
                subs_raw = []
            
            player_in = [s.get('playerIn') for s in subs_raw]
            player_out = [s.get('playerOut') for s in subs_raw]
            sub_minute = [s.get('minute') for s in subs_raw]

            df_in = pd.DataFrame({
                'playerId': player_in,
                'substituteIn': 1,
                'minuteStart': sub_minute
            })
            df_out = pd.DataFrame({
                'playerId': player_out,
                'substituteOut': 1,
                'minuteEnd': sub_minute
            })

            #Merge infomation substitutions
            df_team = pd.merge(df_team, df_in[["playerId", "substituteIn", "minuteStart"]],
                               on = "playerId", how = 'left')

            df_team = pd.merge(df_team, df_out[["playerId", "substituteOut", "minuteEnd"]],
                               on = "playerId", how = 'left')
            
            #Fill data
            df_team['substituteIn'] = df_team['substituteIn'].fillna(0).astype(int)
            df_team['substituteOut'] = df_team['substituteOut'].fillna(0).astype(int)
            df_team['minuteStart'] = df_team['minuteStart'].fillna(0)
            df_team['minuteEnd'] = df_team['minuteEnd'].fillna(90)

            # clip minute value to the 0 to 90 range.
            df_team['minuteStart'] = df_team['minuteStart'].clip(0, 90)
            df_team['minuteEnd'] = df_team['minuteEnd'].clip(0, 90)

            #If a player did not start AND did not substitute in => minuteEnd = 0
            df_team.loc[(df_team['lineup'] == 0) & (df_team['substituteIn'] == 0), 'minuteEnd'] = 0

            #Calculate minutes played
            df_team['minutePlayed'] = df_team['minuteEnd'] - df_team['minuteStart'].clip(0, 90)

            lst_formations.append(df_team)

    return pd.concat(lst_formations, ignore_index=True)



            