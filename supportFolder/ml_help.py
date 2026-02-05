import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
import scipy.stats as ss
from collections import Counter
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
            raise ValueError("Giá trị step không hợp lệ. Step phải có dạng sao cho khi nhân với 1000 thì thu được một số nguyên.")

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
    def create_variable_graph(df, col, target_col, y1_axis_name = "Tỷ trọng số cú sút (%)", y2_axis_name ="Xác suất ghi bàn (%)", binned_cols = False, title_name = None):
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
            f"Giá trị: {row[col]} <br>Tỉ trọng cú sút (%): {row['share']:.2f}"
            for _, row in df_group.iterrows()
        ]

        hovertext_target = [
            f"Giá trị: {row[col]} <br>Tỉ lệ ghi bàn (%): {row['share_target']:.2f}"
            for _, row in df_group.iterrows()
        ]

        #plot
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Bar(
                x=df_group[col],
                y=df_group["share"],
                name=y1_axis_name,
                hoverinfo="skip",
                text=hovertext_variable,
                textposition="none",   # ⬅️ QUAN TRỌNG
                marker=dict(color=DEFAULT_PLOTLY_COLORS[0]),
            ),
            secondary_y=False
        )
        
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
            height= 650,
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


    @staticmethod
    def check_columns_match(df1, df2, columns):
        
        assert_frame_equal(df1[columns], df2[columns])
        return True
    

    @staticmethod
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
    

    @staticmethod
    def convert(data, target):
        
        if target == "array":
            if isinstance(data, np.ndarray):
                result = data
            elif isinstance(data, pd.Series):
                result = data.to_numpy()
            elif isinstance(data, list):
                result = np.asarray(data)
            elif isinstance(data, pd.DataFrame):
                result = data.values
            else:
                result = None

        elif target == "list":
            if isinstance(data, list):
                result = data
            elif isinstance(data, (pd.Series, np.ndarray)):
                result = list(data)
            else:
                result = None

        elif target == "dataframe":
            if isinstance(data, pd.DataFrame):
                result = data
            elif isinstance(data, np.ndarray):
                result = pd.DataFrame(data)
            else:
                result = None
        
        else: 
            raise ValueError(f"Không thể chuyển đổi kiểu dữ liệu: {target}")
        
        if result is None:
            raise TypeError(f"Không thể chuyển đổi kiểu dữ liệu cho đối tượng: {type(data)} tới {target}")
        
        return result
    

    @staticmethod
    def cramers_v(x, y):
        confusion = pd.crosstab(x, y)
        chisq = ss.chi2_contingency(confusion)[0]

        n = confusion.values.sum()
        phisq = chisq/n

        r, k = confusion.shape

        phisq_corr = max(
            0.0, phisq - ((k - 1 ) * (r - 1)) / (n - 1)
        )

        r_corr = r - ((r - 1)**2) / (n - 1)
        k_corr = k - ((k - 1)**2) / (n - 1)

        return np.sqrt(phisq_corr / min(k_corr - 1, r_corr - 1))
    

    @staticmethod
    def conditional_entropy(x, y):
        joint_counts = Counter(zip(x, y))
        y_counts = Counter(y)

        total = sum(y_counts.values())
        entropy_val = 0.0

        for (_, y_value), joint_freq in joint_counts.items():
            p_xy = joint_freq / total
            p_y = y_counts[y_value] / total

            if p_xy < 1e-6 or p_y < 1e-6:
                return -100
            
            entropy_val += p_xy * math.log(p_y/p_xy)

        return entropy_val
    

    @staticmethod
    def theils_u(x, y):
        s_xy = MachineLearningHelp.conditional_entropy(x, y)
        x_counts = Counter(x)

        total = sum(x_counts.values())
        p_x = [v / total for v in x_counts.values()]
        s_x = ss.entropy(p_x)

        return 1 if s_x == 0 else (s_x - s_xy) / s_x

    
    @staticmethod
    def correlation_ratio(categories, vals):
        categories = MachineLearningHelp.convert(categories, "array")
        vals = MachineLearningHelp.convert(vals, "array")

        cat_codes, _ =  pd.factorize(categories)
        n_cats = np.max(cat_codes) + 1

        means = np.zeros(n_cats)
        counts = np.zeros(n_cats)

        for i in range(n_cats):
            valss = vals[cat_codes == i]
            counts[i] = len(valss)
            means[i] = np.mean(valss)
        
        global_means = np.sum(means * counts) / np.sum(counts)

        num = np.sum(counts * (means - global_means)**2)
        den = np.sum((vals - global_means) ** 2)

        return 0.0 if num==0 else np.sqrt(num/den)
    

    @staticmethod
    def compute_associations(df, col_a, col_b, nominal_cols, use_theil=False):
        if col_a == col_b:
            return 1.0, 1.0

        a_is_cat = col_a in nominal_cols
        b_is_cat = col_b in nominal_cols

        if a_is_cat and b_is_cat:
            if use_theil:
                return (
                    MachineLearningHelp.theils_u(df[col_a], df[col_b]),
                    MachineLearningHelp.theils_u(df[col_b], df[col_a])
                )
            val = MachineLearningHelp.cramers_v(df[col_a], df[col_b])
            return val, val
        
        if a_is_cat != b_is_cat:
            cat_col, num_col = (col_a, col_b) if a_is_cat else (col_b, col_a)
            valid = ~np.isnan(df[num_col])

            val = MachineLearningHelp.correlation_ratio(
                df.loc[valid, cat_col],
                df.loc[valid, num_col]
            )
            return val, val
        
        x = df[col_a].to_numpy()
        y = df[col_b].to_numpy()
    
        valid = ~np.isnan(x) & ~np.isnan(y)
        corr, _ = ss.pearsonr(x[valid], y[valid])

        return corr, corr
    

    @staticmethod
    def associations(dataset, nominal_cols=None, mark_cols=False, theil_u=False, return_results=True,):
        """
        Calculate the correlation / strength-of-association between features in a dataset.
        """

        # ensure dataframe format
        dataset = MachineLearningHelp.convert(dataset, "dataframe")
        columns = dataset.columns

        # handle nominal columns
        if nominal_cols is None:
            nominal_cols = []
        elif nominal_cols == "all":
            nominal_cols = columns

        # initialize correlation matrix
        corr = pd.DataFrame(index=columns, columns=columns)

        # compute associations
        for i, col_i in enumerate(columns):
            for j in range(i, len(columns)):
                col_j = columns[j]

                if i == j:
                    corr.loc[col_i,col_j] = 1.0
                else:
                    val_1, val_2 = MachineLearningHelp.compute_associations(dataset, col_i, col_j, nominal_cols, theil_u,)
                    corr.loc[col_j,col_i] = val_1
                    corr.loc[col_i,col_j] = val_2

        corr.fillna(value=np.nan, inplace=True)

        # mark column types if requested
        if mark_cols:
            marked = [
                f"{col} (nom)" if col in nominal_cols else f"{col} (con)"
                for col in columns
            ]
            corr.columns = marked
            corr.index = marked

        if return_results:
            return corr

 