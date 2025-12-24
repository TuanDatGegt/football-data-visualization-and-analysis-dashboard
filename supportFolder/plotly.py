import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
#import scrip

class create_soccer_Pitch:
    """
    Module support for soccer visualize 
    """
    def __init__(self, len_field = 105, wid_field = 68, theme = "tactical"):
        self.length = len_field
        self.width = wid_field

        themes = {
            "tactical": {"pitch": "#121212", "line": "#555555", "goal": "#ffffff", "heatmap": "Viridis"},
            "classic": {"pitch": "#224422", "line": "#FFFFFF", "goal": "#FFFFFF", "heatmap": "Hot"},
            "white": {"pitch": "#white", "line": "#222222", "goal": "#000000", "heatmap": "YlGnBu"}
        }
        self.theme = theme.get(theme, themes["tactical"])
        self.fig = self._create_empty_pitch()

    def _create_arc(self, x_center, y_center, radius, start_angle, end_angle):
        angles = np.linspace(start_angle, end_angle, 50)
        x = x_center + radius * np.cos(np.radians(angles))
        y = y_center + radius * np.sin(np.radians(angles))

        return x, y
    
    def _create_empty_pitch(self):
        fig = go.Figure()
        fig.update_layout(
            plot_bgcolor = self.theme["pitch"],
            paper_bgcolor = self.theme["pitch"],
            xasis = dict(range=[-5, self.length + 5], showgrid=False, zeroline=False, visible=False),
            yaxis = dict(range=[-5, self.length + 5], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
            margin = dict(l=10, r = 10, t=10, b=10),
            width=850, height=550, showlegend=False   
        )

        line_style = dict(color=self.theme['line'], width=1.5)

        shapes = [
            dict(type="rect", x0=0, y0=0, x1=self.length, y1=self.width, line=line_style, layer="above"),
            dict(type="line", x0=self.length/2, y0=0, x1=self.length/2, y1=self.width, line=line_style, layer="above"),
        ]

        for side in [0, 1]:
            x_edge = side * self.length
            dir = 1 if side == 0 else -1
            #Vòng cấm 16m5
            shapes.append(dict(type="rect", x0=x_edge, y0=(self.width-40.3)/2, x1=x_edge+(dir*16.5), y1=(self.width+40.3)/2, line=line_style, layer="above"))
            #Vòng cấm 5m50
            shapes.append(dict(type="rect", x0=x_edge, y0=(self.width-18.3)/2, x1=x_edge+(dir*5.5), y1=(self.width+18.3)/2, line=line_style, layer="above"))
            #Cầu môn
            shapes.append(dict(type="rect", x0=x_edge, y0=(self.width-7.32)/2, x1=x_edge-(dir*1.5), y1=(self.width+7.32)/2, line=dict(color=self.theme["goal"], width=2), layer="above"))

        fig.update_layout(shapes=shapes)

        #Chấm phạt đền & Vòng tròn giữa sân
        fig.add_trace(go.Scatter(x=[11, self.length/2, self.length-11], y=[self.width/2]*3, mode="markers", marker=dict(color=self.theme["line"], size=4), hoverinfo='skip'))
        cx, cy = self._create_arc(self.length/2, self.width/2, 9.15, 0, 360)
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=line_style, hoverinfo='skip'))

        #Vòng cung D
        lx, ly = self._create_arc(11, self.width/2, 9.15, -53, 53)
        rx, ry = self._create_arc(self.length-11, self.width/2, 9.15, 127, 233)
        fig.add_trace(go.Scatter(x=lx, y=ly, mode='lines', line=line_style, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=rx, y=ry, mode='lines', line=line_style, hoverinfo='skip'))

        return fig
    
    def calculate_bucket_for_position(self, series, nb_buckets, min_pos_val, max_pos_val):
        buckets=np.arange(min_pos_val, max_pos_val + 0.001, max_pos_val / nb_buckets)
        df_buckets = pd.DataFrame({
            "id": np.arange(len(buckets)-1),
            "minValueZone": list(buckets)[:-1],
            "maxValueZone": list(buckets)[1:],
        })

        df_buckets["meanValueZone"] = (df_buckets["minValueZone"] + df_buckets["maxValueZone"])/2
        buckets[-1] += 0.001
        return pd.cut(series, buckets, labels=False, include_lowest=True), df_buckets
    
    def add_binned_heatmap(self, df, col_x, col_y, nb_buckets_x=12, nb_buckets_y = 8, agg_cols = None, agg_type="count", title="None"):
        """
        Create heatmap by binned map. It is useful for analyzing the number of events in each area of the stadium.
        
        :param self: Description
        :param df: Description
        :param col_x: Description
        :param col_y: Description
        :param nb_buckets_x: Description
        :param nb_buckets_y: Description
        :param agg_cols: Description
        :param title: Description
        """
        df = df.copy()

        df[col_x + "Zone"], df_lookup_x = self.calculate_bucket_for_position(df[col_x], nb_buckets_x, 0, self.length)
        df[col_y + "Zone"], df_lookup_y = self.calculate_bucket_for_position(df[col_y], nb_buckets_y, 0, self.width)

        target_col = agg_cols if agg_cols else col_x + "Zone"
        df_pos = df.groupby([col_x + "Zone", col_y + "Zone"]).agg(aggVal=(target_col, agg_type)).reset_index()

        df_all_pos = pd.DataFrame([(x, y) for x in df_lookup_x["id"] for y in df_lookup_y["id"]], columns=[col_x + "Zone", col_y + "Zone"])
        df_all_pos = df_all_pos.merge(df_lookup_x[["id", "meanValueZone"]].rename(columns={"id": col_x + "Zone", "meanValueZone": col_x + "MZ"}), on=col_x + "Zone")
        df_all_pos = df_all_pos.merge(df_lookup_y[["id", "meanValueZone"]].rename(columns={"id": col_y + "Zone", "meanValueZone": col_y + "MZ"}), on=col_y + "Zone")

        df_final = df_all_pos.merge(df_pos, on=[col_x + "Zone", col_y + "Zone"], how="left").fillna(0)
        df_image = df_final.pivot(index=col_y + "MZ", columns=col_x + "MZ", values="aggVal")

        self.fig.add_trace(go.Heatmap(
            z=df_image.values,
            x=df_image.columns,
            y= df_image.index,
            colorscale=self.theme["heatmap"],
            zsmooth="best",
            opacity=0.7,
            colorbar=dict(title=agg_type.capitalize())
        ))

        if title:
            self.fig.update_layout(title={"text": title, "x": 0.5, "y": 0.95})

        return self.fig
    

    def add_shots_(self, df):
        """
        Required dataframe must be x, y, xG, result(Goal/No Goal)
        """
        for res in df['result'].unique():
            data=df[df['result']==res]
            self.fig.add_trace(go.Scatter(
                x=data['x'], y=data['y'], mode="markers",
                name=res,
                marker=dict(size=data['xG']*35, line=dict(width=1, color="white"), opacity=0.8),
                hovertemplate="xG: %{marker.size}<extra></extra>"
            ))
        return self.fig
    
    def add_events_(self, x_start, y_start, x_end, y_end, color="yellow"):
        """
        Plot pass trajectories
        """
        for xs, ys, xe, ye in zip(x_start, y_start, x_end, y_end):
            self.fig.add_trace(go.Scatter(
                x=[xs, xe], y=[ys, ye], mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=6, symbol="arrow", angleref = "previous"),
                opacity=0.5
            ))

        return self.fig
    
    def add_tracking_(self, players_df):
        """
        Plot one frame tracking. player_df: [x, y, team, number]
        """
        colors = {"Home": "#3498db", "Away": "#e74c3c"}
        for team in players_df['teamID'].unique():
            td = players_df[players_df['team'] == team]
            self.fig.add_trace(go.Scatter(
                x=td["number"], textposition="middle center",
                textfont=dict(color="white", size = 8),
                marker=dict(size=18, color=colors.get(team, "gray"), line= dict(width=1, color="white"))
            ))

        return self.fig
    
