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
            "tactical": {"pitch": "#121212", "line": "#FFFFFF", "goal": "#ffffff", "heatmap": "Viridis"},
            "classic": {"pitch": "#224422", "line": "#FFFFFF", "goal": "#FFFFFF", "heatmap": "Hot"},
            "white": {"pitch": "white", "line": "#222222", "goal": "#000000", "heatmap": "YlGnBu"}
        }
        self.theme = themes.get(theme, themes["tactical"])
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
            xaxis = dict(range=[-5, self.length + 5], showgrid=False, zeroline=False, visible=False),
            yaxis = dict(range=[-5, self.width + 5], showgrid=False, zeroline=False, visible=False, scaleanchor="x", scaleratio=1),
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
        fig.add_trace(go.Scatter(x=[11, self.length/2, self.length-11], y=[self.width/2]*3, mode="markers", marker=dict(color=self.theme["line"], size=10), hoverinfo='skip'))
        cx, cy = self._create_arc(self.length/2, self.width/2, 9.15, 0, 360)
        fig.add_trace(go.Scatter(x=cx, y=cy, mode="lines", line=line_style, hoverinfo='skip'))

        #Vòng cung D
        lx, ly = self._create_arc(11, self.width/2, 9.15, -53, 53)
        rx, ry = self._create_arc(self.length-11, self.width/2, 9.15, 127, 233)
        fig.add_trace(go.Scatter(x=lx, y=ly, mode='lines', line=line_style, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=rx, y=ry, mode='lines', line=line_style, hoverinfo='skip'))

        return fig
    

    def _build_grid(self, min_value, max_value, nb_buckets):
        edges = np.linspace(min_value, max_value, nb_buckets + 1)
        centers = (edges[:-1] + edges[1:]) / 2  
        return edges, centers
    
    def  _assign_bucket(self, series, edges):
        idx = np.digitize(series, edges)
        return np.clip(idx, 0, len(edges) - 2)
    
    
    def add_binned_heatmap(self, df, col_x, col_y, metrics, nb_buckets_x=24, nb_buckets_y=17):

        df = df.copy()

        x_edges, x_centers = self._build_grid(0, self.length, nb_buckets_x)
        y_edges, y_centers = self._build_grid(0, self.width, nb_buckets_y)

        df["x_Zone"] = self._assign_bucket(df[col_x], x_edges)
        df["y_Zone"] = self._assign_bucket(df[col_y], y_edges)

        df = df[
            df.x_Zone.between(0, nb_buckets_x - 1) &
            df.y_Zone.between(0, nb_buckets_y - 1)
        ]
        
        grouped = (
            df.groupby(["x_Zone", "y_Zone"]).agg(**{
                k: (v["col"] if v["col"] else col_x,v["agg"])
                for k, v in metrics.items()
            }).reset_index()
        )

        full_grid = pd.MultiIndex.from_product(
            [range(nb_buckets_x), range(nb_buckets_y)],
            names=["x_Zone", "y_Zone"]
        ).to_frame(index=False)

        grouped = full_grid.merge(grouped, how="left").fillna(0)

        matrices = {
            k: grouped.pivot(index='y_Zone', columns='x_Zone', values=k).values
            for k in metrics
        }

        return matrices, x_centers, y_centers
    

    def hover_text(self, z, dict_infor):
        ny, nx = z.shape

        hovertext = []
        for iy in range(ny):
            row = []
            for ix in range(nx):
                if z[iy, ix] == 0:
                    row.append("No data")
                    continue

                text = ""
                for key, info in dict_infor.items():
                    val = info["values"][iy, ix]
                    fmt = info.get("display_type", ".2f")
                    text += f"{key}: {val:{fmt}}<br>"
                row.append(text)
            hovertext.append(row)
        return hovertext
    
    
    def add_heatmap_(self, z, x_centers, y_centers, title=None, opacity=0.85, dict_infor=None):

        z = np.asarray(z)
        
        hovertext = None
        if dict_infor is not None:
            hovertext = self.hover_text(z, dict_infor)

    
        self.fig.add_trace(go.Heatmap(
            x= x_centers,
            y= y_centers,
            z= z,
            colorscale=self.theme["heatmap"],
            hoverinfo="text",
            hovertext=hovertext,
            opacity=opacity,
            colorbar=dict(title="Value"),
            zsmooth=False
        ))

        if title:
            self.fig.update_layout(title=dict(text=title, x=0.5, y=0.95, xanchor='center', yanchor='top'))

        return self.fig
     

    def add_shots_(self, df, x_start="posBeforeXMeters", y_start="posBeforeYMeters", goal_col="Goal"):
        """
        Required dataframe must be x, y, xG, result(Goal/No Goal)
        """
        df['result'] = df[goal_col].map({1:"Goal", 0:"No Goal"})
        colors={"Goal": "#00FF00", "No Goal" : "#FF0000"}
        for res in df['result'].unique():
            data=df[df['result']==res]
            self.fig.add_trace(go.Scatter(x=data[x_start], y=data[y_start], mode="markers", name=res,
                                          marker=dict(size=12, color=colors.get(res, "white"), line=dict(width=1, color="white"), opacity=0.8)))
        return self.fig
    

    def add_events_(self, x_start, y_start, x_end, y_end, color="yellow"):
        """
        Plot pass trajectories
        """
        for xs, ys, xe, ye in zip(x_start, y_start, x_end, y_end):
            self.fig.add_trace(go.Scatter(
                x=[xs, xe], y=[ys, ye], mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(size=6, symbol="lines", angleref = "previous"),
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
    
    
    def show(self):
        self.fig.show()