import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import scipy.spatial

from supportFolder.statical_eventTracking import number_pass_accurate
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
    
    
    def add_binned_heatmap(self, df, col_x, col_y, metrics, nb_buckets_x=24, nb_buckets_y=17, return_df=False):

        df_result = df.copy()

        x_edges, x_centers = self._build_grid(0, self.length, nb_buckets_x)
        y_edges, y_centers = self._build_grid(0, self.width, nb_buckets_y)

        df_result["x_Zone"] = self._assign_bucket(df[col_x], x_edges)
        df_result["y_Zone"] = self._assign_bucket(df[col_y], y_edges)

        df_filtered = df_result[
            df_result.x_Zone.between(0, nb_buckets_x - 1) &
            df_result.y_Zone.between(0, nb_buckets_y - 1)
        ].copy()
        
        grouped = (
            df_filtered.groupby(["x_Zone", "y_Zone"]).agg(**{
                k: (v["col"] if v["col"] else col_x, v["agg"])
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

        if return_df:
            return df_result, matrices, x_centers, y_centers

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
    
    def prepare_pass_(self, df_events, df_stats, show_top_K_percent=None, view_90_minute=False):
        
        if df_stats["teamID"].nunique() > 1:
            raise ValueError("Position plot should only contain 1 team")

        team_id = df_stats["teamID"].unique()[0]

        # GỌI HÀM BỔ TRỢ VỪA VIẾT Ở TRÊN
        df_passes = number_pass_accurate(df_events, team_id)

        # Lọc chỉ lấy những cầu thủ có trong df_stats
        players = df_stats["playerID"].unique()
        df_passes = df_passes[
            df_passes["player1ID"].isin(players) & df_passes["player2ID"].isin(players)
        ]

        # Lấy centroid và minutesPlayed
        df_centroid = df_stats[["playerID", "centroidX", "centroidY", "minutePlayed"]].copy()

        # Merge tọa độ Player 1
        df_pos_p1 = df_centroid.rename(columns={
            "playerID": "player1ID", "centroidX": "centroidX1", 
            "centroidY": "centroidY1", "minutePlayed": "minutePlayed1"
        })
        df_pass_share = pd.merge(df_passes, df_pos_p1, on="player1ID")

        # Merge tọa độ Player 2
        df_pos_p2 = df_centroid.rename(columns={
            "playerID": "player2ID", "centroidX": "centroidX2", 
            "centroidY": "centroidY2", "minutePlayed": "minutePlayed2"
        })
        df_pass_share = pd.merge(df_pass_share, df_pos_p2, on="player2ID")

        # Tính toán view 90 phút
        if view_90_minute:
            min_mins = df_pass_share[["minutePlayed1", "minutePlayed2"]].min(axis=1)
            # Tránh chia cho 0
            df_pass_share["totalPasses"] = (df_pass_share["totalPasses"] / min_mins * 90).replace([np.inf, -np.inf], 0)

        # Tính sharePasses để làm độ dày đường kẻ (width)
        max_passes = df_pass_share["totalPasses"].max()
        if max_passes > 0:
            df_pass_share["sharePasses"] = df_pass_share["totalPasses"] / max_passes
        else:
            df_pass_share["sharePasses"] = 0

        # Lọc Top K%
        if show_top_K_percent is not None:
            df_pass_share = df_pass_share.sort_values("totalPasses", ascending=False)
            df_pass_share["cumShare"] = df_pass_share["totalPasses"].cumsum() / df_pass_share["totalPasses"].sum()
            df_pass_share = df_pass_share[df_pass_share["cumShare"] <= show_top_K_percent / 100].copy()

        return df_pass_share

    def add_position_plot(self, df_stats, title=None, dict_info=None, colour_kpi=None,
                          colour_scale=None, df_passes=None, convex_hull=False):
        
        df_stats = df_stats.copy()
        df_stats["centroidY"] = self.width - df_stats["centroidY"]

        if convex_hull:
            field_player = df_stats[df_stats["playerPosition"] != "Goalkeeper"]
            if len(field_player) >= 3:
                centroids = field_player[["centroidX", "centroidY"]].to_numpy()
                hull = scipy.spatial.ConvexHull(centroids)
                convex_x = centroids[hull.vertices, 0]
                convex_y = centroids[hull.vertices, 1]

                convex_x = np.append(convex_x, convex_x[0])
                convex_y = np.append(convex_y, convex_y[0])

                self.fig.add_trace(go.Scatter(
                    x=convex_x, y=convex_y, fill="toself", mode="lines",
                    fillcolor="rgba(255, 255, 255, 0.1)",
                    line=dict(color=self.theme['lines'], width=1, dash='dot'),
                    showlegend=False, name="Convex Hull"
                ))

        if df_passes is not None:
            df_pass = df_passes.copy()
            df_pass["centroidY1"] = self.width - df_pass["centroidY1"]
            df_pass["centroidY2"] = self.width - df_pass["centroidY2"]

            for _, row in df_pass.iterrows():
                self.fig.add_trace(go.Scatter(
                    x=[row["centroidX1"], row["centroidX2"]],
                    y=[row["centroidY1"], row["centroidY2"]],
                    mode="lines", showlegend=False,
                    line=dict(color="#FFD700", width=row.get("sharePasses", 1)*20),
                    opacity=0.3
                ))

        marker_color = df_stats[colour_kpi] if colour_kpi is not None else "red"
        self.fig.add_trace(go.Scatter(
            x=df_stats["centroidX"],
            y=df_stats["centroidY"],
            mode="markers+text",
            text=df_stats["playerName"],
            textposition="bottom center",
            name="Players",
            marker=dict(
                color=marker_color, 
                size=12, 
                colorscale="Reds" if colour_kpi else None,
                showscale=True if colour_kpi else False,
                line=dict(width=1, color="white")
            )
        ))

        # 4. Xử lý Hover Information
        default_dict = {
            "Player name": {"values": "playerName"},
            "Minutes played": {"values": "minutePlayed", "display_type": ".0f"},
            "Total passes": {"values": "totalPasses", "display_type": ".0f"},
            "Total passes/90": {"values": "totalPasses90", "display_type": ".0f"},
            "Accurate passes (%)": {"values": "shareAccuratePasses", "display_type": ".1f"},
            "Total shots": {"values": "totalShots", "display_type": ".0f"},
            "Total goals": {"values": "totalGoals", "display_type": ".0f"},
        }
        
        target_info = dict_info if dict_info is not None else default_dict
        hover_list = []
        for _, row in df_stats.iterrows():
            text = ""
            for label, info in target_info.items():
                col = info["values"]
                if col in row:
                    val = row[col]
                    if pd.isna(val):
                        text += f"{label}: N/A<br />"
                    elif "display_type" in info:
                        # Sử dụng format từ code mẫu của bạn
                        text += "{}: {:^{display_type}}<br />".format(label, val, display_type=info["display_type"])
                    else:
                        text += f"{label}: {val}<br />"
            hover_list.append(text)
        
        self.fig.data[-1].hovertemplate = hover_list

        if colour_kpi:
            legend_name = next((k for k, v in target_info.items() if v["values"] == colour_kpi), colour_kpi)
            self.fig.add_annotation(
                x=1.12, y=1.05, text=legend_name, showarrow=False,
                xref="paper", yref="paper", font=dict(color="white")
            )

        if title:
            self.fig.update_layout(title=dict(text=title, x=0.5, y=0.95, xanchor="center"))
        
        return self.fig

    def show(self):
        self.fig.show()