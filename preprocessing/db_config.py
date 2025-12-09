import pandas as pd
import ast
import os

def extract_teams_form_matches(matches_df):
    records = []

    for _,row in matches_df.iterrows():
        match_id = row.get('mathID')
        teams_Data = row.get('teamsData')

        if pd.isna(teams_Data):
            continue

        try:
            teams_dict = ast.literal_eval(teams_Data)
        except Exception:
            continue

        for team_key, team_info in teams_dict.items():
            team_id = team_info.get('teamId')
            coach_id = team_info.get('coachId')
            side = team_info.get('side')
            #score = team_info.get('score', None)

            records.append({
                "matchID": match_id,
                "teamID": team_id,
                "coachID": coach_id,
                "side": side
                #"score":
            })
