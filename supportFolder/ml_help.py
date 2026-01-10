import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pandas._testing import assert_frame_equal
from plotly.subplots import make_subplots
from plotly.colors import DEFAULT_PLOTLY_COLORS

class MachineLearningHelp:
    @staticmethod

    def build_bucket_zone(df, col, step_size, min_value = None, max_value = None, delete = False):
        """
        Docstring for build_bucket_zone
        
        :param df: Description
        :param col: Description
        :param step_size: Description
        :param min_value: Description
        :param max_value: Description
        :param delete: Description
        """
        df = df.copy()

        factor = None
        for f in [1, 10, 100, 1000]:
            if float(step_size * f).is_integer():
                factor = f
                break
        if factor is None:
            raise ValueError("Chỉ sử dụng các bước nhảy có thể chuyển đổi thành số nguyên bằng cách nhân với 1000.")

        df[col] = df[col] * factor
        step_size = step_size * factor

        if max_value is not None:
            max_value = max_value * factor
            if delete:
                df = df[df[col] <= max_value].copy()
            df[col] = df[col].clip(upper=max_value)

        
        if min_value is not None:
            min_value = min_value * factor
            if delete:
                df = df[df[col] >= min_value].copy()
            df[col] = df[col].clip(lower=min_value)


        #binning
        df[col] = df[col].apply(lambda x: int(x/step_size) * step_size)

        if factor > 1:
            df[col] = df[col] / factor

        return df[col]
    

    @staticmethod
    def create_variable_graph(df, col, target_col, y1_axis_name = "Share obs. (%)", y2_axis_name = "Target prob. (%)", binned_cols = False, title_name = None):
        """
        Docstring for create_variable_graph
        
        :param df: Description
        :param col: Description
        :param target_col: Description
        :param y1_axis_name: Description
        :param y2_axis_name: Description
        :param binned_cols: Description
        :param title_name: Description
        """
        df = df[df[col].notnull()].copy()

        if binned_cols:
            unique_values = sorted(df[col].unique())
            lst_x_titles = []
            for i in range(len(unique_values)):
                if i == 0:
                    lst_x_titles.append(f"< {unique_values[i + 1]}")
                elif i == len(unique_values) - 1:
                    lst_x_titles.append(f">= {unique_values[i]}")
                else:
                    lst_x_titles.append(f"{unique_values[i]} - {unique_values[i + 1]}")
        
        df_group = (
            df.groupby(col)
                .agg(
                    total_count=(col, "count"),
                    total_target=(target_col, "sum")
                )
                .reset_index()
                .assign(
                    share=lambda x: x["total_count"] / len(df) * 100,
                    share_target=lambda x: np.where(
                        x["total_count"] > 0,
                        x["total_target"] / x["total_count"] * 100,
                        0
                    )
                )
        )


        #howver text
        hovertext_variable = [
            f"Value: {row[col]} <br>Share obs.: {row['share']:.2f}"
            for _, row in df_group.iterrows()
        ]

        hovertext_target = [
            f"Value: {row[col]} <br>Target prob. (%): {row['share_target']:.2f}"
            for _, row in df_group.iterrows()
        ]

        #plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(
                x = df_group[col],
                y = df_group["share"],
                name=y1_axis_name,
                hoverinfo="text",
                text = hovertext_variable,
                marker=dict(color=DEFAULT_PLOTLY_COLORS[0]),
            ), secondary_y=False)
        
        fig.add_trace(
            go.Scatter(
                x = df_group[col],
                y = df_group["share_target"],
                name=y2_axis_name,
                hoverinfo="text",
                text = hovertext_target,
                marker=dict(color=DEFAULT_PLOTLY_COLORS[1]),
            ), secondary_y=True)
        
        fig.update_layout(
            yaxis=dict(
                title=dict(
                    text=y1_axis_name,
                    font=dict(size=16)   # thay vì titlefont_size
                ),
                tickfont=dict(size=14),   # thay vì tickfont_size
                rangemode='tozero',
            ),
            yaxis2=dict(
                title=dict(
                    text=y2_axis_name,
                    font=dict(size=16)
                ),
                tickfont=dict(size=14),
                rangemode='tozero',
            ),
        )

        
        if title_name is None:
            title_name = col
        
        fig.update_layout(
            title=dict(
                text=title_name,
                y=0.9,
                x=0.5,
                xanchor="center",
                yanchor="top",
            )
        )

        if binned_cols:
            fig.data[0]["x"] = np.array(lst_x_titles)
            fig.data[1]["x"] = np.array(lst_x_titles)

        return fig, df_group

    
    def check_columns_match(df1, df2, columns):
        
        assert_frame_equal(df1[columns], df2[columns])
        return True
    

    def combine_variable_graph(figures, cols, rows, shared_axis=False):
        titles = [
            fig['layout']['title']['text']
            for fig in figures
        ]

        fig = make_subplots(
            rows = rows,
            cols = cols,
            subplot_titles=titles,
            shared_xaxes=True
        )

        for r in range(rows):
            for c in range(cols):
                idx = r*cols + c
                for trace in figures[idx]["data"]:
                    fig.add_trace(trace, row=r + 1, col=c + 1)

        for i, src_fig in enumerate(figures):
            axis_name = "yaxis" if i == 0 else f"yaxis{i + 1}"
            fig.layout[axis_name]["title"] = src_fig['layout']['yaxis']['title']['text']
            fig.layout[axis_name]["tickfont"]["size"] = 8
            fig.layout[axis_name]['title']['font']['size'] = 10

        
        # configure right y-axes
        n_figs = len(figures)
        for i, src_fig in enumerate(figures):
            axis_name = f"yaxis{n_figs + 1 + i}"
            anchor = "x" if i == 0 else f"x{i + 1}"
            overlay = "y" if i == 0 else f"y{i + 1}"

            fig.layout[axis_name] = src_fig["layout"]["yaxis2"]
            fig.layout[axis_name]["anchor"] = anchor
            fig.layout[axis_name]["overlaying"] = overlay
            fig.layout[axis_name]["tickfont"]["size"] = 8
            fig.layout[axis_name]["title"]["font"]["size"] = 10

            # map right-axis trace correctly
            fig["data"][(2 * i) + 1].update(
                yaxis=f"y{n_figs + 1 + i}"
            )

        # shared axis adjustments
        if shared_axis:
            for i in range(n_figs):

                # align right y-axes
                if i > 0:
                    fig.layout[f"yaxis{n_figs + 1 + i}"]["matches"] = f"y{n_figs + 1}"

                # remove redundant right y-axis titles
                if i % cols != (cols - 1):
                    fig.layout[f"yaxis{n_figs + 1 + i}"]["title"] = None

                # remove redundant left y-axis titles
                if i % cols != 0:
                    fig.layout[f"yaxis{i + 1}"]["title"] = None

        fig.update_layout(
            showlegend=False,
            hovermode=False,
        )

        return fig

 