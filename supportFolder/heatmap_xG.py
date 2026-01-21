import numpy as np
import pandas as pd
from supportFolder.plot_pitch import create_soccer_Pitch


def build_goal_probability_heatmap(
    df_shots,
    col_x="posBeforeXMeters",
    col_y="posBeforeYMeters",
    nb_buckets_x=24,
    nb_buckets_y=17,
    theme="tactical"
):
    """
    Build observed goal conversion rate heatmap
    Refactored directly from notebook cell
    """

    pitch_prob = create_soccer_Pitch(theme=theme, view="half", attacking_direction="right")

    # =========================
    # 1. FILTER GOALS
    # =========================
    df_goals = df_shots[df_shots["Goal"] == 1].copy()

    # =========================
    # 2. BIN GOALS
    # =========================
    metrics_goals = {
        "Number of goals": {"col": None, "agg": "count"}
    }

    goals_data, x, y = pitch_prob.add_binned_heatmap(
        df_goals,
        col_x=col_x,
        col_y=col_y,
        nb_buckets_x=nb_buckets_x,
        nb_buckets_y=nb_buckets_y,
        metrics=metrics_goals
    )

    nb_goals = goals_data["Number of goals"]

    # =========================
    # 3. BIN SHOTS (ALL)
    # =========================
    metrics_shots = {
        "Number of shots": {"col": None, "agg": "count"}
    }

    shots_data, _, _ = pitch_prob.add_binned_heatmap(
        df_shots,
        col_x=col_x,
        col_y=col_y,
        nb_buckets_x=nb_buckets_x,
        nb_buckets_y=nb_buckets_y,
        metrics=metrics_shots
    )

    nb_shots = shots_data["Number of shots"]

    share_shots = nb_shots / nb_shots.sum() * 100

    # =========================
    # 4. GOAL PROBABILITY
    # =========================
    goal_probability = np.divide(
        nb_goals,
        nb_shots,
        out=np.zeros_like(nb_goals, dtype=float),
        where=nb_shots != 0
    ) * 100

    # =========================
    # 5. INFO LAYER
    # =========================
    dict_infor = {
        "Scoring probability (%)": {
            "values": goal_probability,
            "display_type": ".2f"
        },
        "Share of shots (%)": {
            "values": share_shots,
            "display_type": ".2f"
        },
        "Number of shots": {
            "values": nb_shots,
            "display_type": ".0f"
        },
        "Number of goals": {
            "values": nb_goals,
            "display_type": ".0f"
        }
    }

    # =========================
    # 6. FIGURE
    # =========================
    fig = pitch_prob.add_heatmap_(
        goal_probability,
        x,
        y,
        dict_infor=dict_infor,
        title="Goal Conversion Rate (%)",
        opacity=0.9
    )

    return fig



def filter_outlier_shots_and_plot_heatmap(df_events, prob_threshold=0.1, nb_buckets_x=24, nb_buckets_y=17):
    """
    Lọc các bàn thắng ngoại lệ dựa trên xác suất quyết định sút tại vị trí đó,
    sau đó vẽ Heatmap xác suất ghi bàn (Conversion Rate).
    
    Parameters:
    - df_events: DataFrame chứa dữ liệu sự kiện (Shot, Pass, ...).
    - prob_threshold: Ngưỡng xác suất sút tối thiểu để công nhận bàn thắng (mặc định 0.1).
    - nb_buckets_x, nb_buckets_y: Số lượng ô chia lưới theo trục x và y.
    """
    
    # --- BƯỚC 1: CHUẨN BỊ DỮ LIỆU ---
    # Tạo bản sao để tránh warning SettingWithCopy
    df_shots = df_events[df_events["eventName"] == "Shot"].copy()
    df_passed = df_events[df_events["eventName"] == "Pass"].copy()

    # Sử dụng pitch object "ảo" để lấy thông tin binning (x_Zone, y_Zone)
    # Lưu ý: Giả định thư viện của bạn có phương thức add_binned_heatmap trả về df đã được gán zone
    pitch_processor = create_soccer_Pitch(theme="tactical", view="half", attacking_direction="right")
    
    # Cấu hình chung cho việc chia bin
    bin_params = {
        'col_x': 'posBeforeXMeters',
        'col_y': 'posBeforeYMeters',
        'nb_buckets_x': nb_buckets_x,
        'nb_buckets_y': nb_buckets_y,
        'return_df': True
    }

    # Lấy thông tin Zone cho Shots
    metrics_dummy = {"count": {"col": None, "agg": "count"}} # Dummy metric chỉ để chạy hàm
    df_shots, _, _, _ = pitch_processor.add_binned_heatmap(df_shots, metrics=metrics_dummy, **bin_params)
    
    # Lấy thông tin Zone cho Passes
    df_passed, _, _, _ = pitch_processor.add_binned_heatmap(df_passed, metrics=metrics_dummy, **bin_params)

    # --- BƯỚC 2: TÍNH TOÁN XÁC SUẤT QUYẾT ĐỊNH SÚT (SHOT PROBABILITY) ---
    cell_zone_cols = ["x_Zone", "y_Zone"]

    # Đếm số lượng theo Zone
    df_shots_per_loc = df_shots.groupby(cell_zone_cols).size().reset_index(name='nbShots')
    df_pass_per_loc = df_passed.groupby(cell_zone_cols).size().reset_index(name='nbPasses')

    # Merge dữ liệu Shot và Pass
    df_actions = pd.merge(df_shots_per_loc, df_pass_per_loc, on=cell_zone_cols, how="outer").fillna(0)
    
    # Tính tỷ lệ: Tại zone này, cầu thủ chọn sút bao nhiêu % so với chuyền
    df_actions['ShotDecisionProb'] = df_actions['nbShots'] / (df_actions['nbShots'] + df_actions['nbPasses'])

    # --- BƯỚC 3: LỌC BÀN THẮNG NGOẠI LỆ (OUTLIER FILTERING) ---
    # Gán xác suất quyết định sút ngược lại vào dataframe shots gốc
    df_shots = pd.merge(df_shots, df_actions[cell_zone_cols + ['ShotDecisionProb']], on=cell_zone_cols, how='left')

    nb_goals_before = df_shots['Goal'].sum()

    # Logic: Nếu xác suất chọn sút ở vị trí này < threshold, ta coi bàn thắng (nếu có) là may mắn/ngoại lệ và loại bỏ nó (set Goal=0)
    # Lưu ý: Vẫn giữ lại cú sút (Shot) trong mẫu số, chỉ bỏ Goal trên tử số.
    df_shots['Goal'] = np.where(df_shots['ShotDecisionProb'] < prob_threshold, 0, df_shots['Goal'])

    # In báo cáo
    changed_nb_goals = nb_goals_before - df_shots['Goal'].sum()
    """   
    print(f"--- BÁO CÁO LỌC ---")
    print(f"Số bàn thắng bị loại bỏ (Outlier): {changed_nb_goals}")
    if nb_goals_before > 0:
        print(f"Tỷ lệ bàn thắng bị loại: {changed_nb_goals / nb_goals_before * 100:.2f}%")
    print(f"Tỷ lệ trên tổng cú sút: {changed_nb_goals / len(df_shots) * 100:.2f}%")
    print("-" * 20)
    """

    # --- BƯỚC 4: TÍNH TOÁN XÁC SUẤT GHI BÀN (SCORING PROBABILITY / CONVERSION RATE) ---
    # Đến đây ta cần tính lại heatmap dựa trên dữ liệu đã lọc
    
    # Tạo metrics thực tế cho biểu đồ cuối cùng
    metrics_shots = {"Number of shots": {"col": None, "agg": "count"}}
    
    # Pitch cuối cùng để vẽ
    pitch_visual = create_soccer_Pitch(theme="tactical", view="half", attacking_direction="right")

    # Tính lại binning cho shots (để lấy ma trận 2D nb_shots cho heatmap)
    # Lưu ý: df_shots đã có x_Zone/y_Zone nhưng hàm add_binned_heatmap tính toán lại ma trận x, y để plot
    _, shots_data, x, y = pitch_visual.add_binned_heatmap(df_shots, metrics=metrics_shots, **bin_params)
    
    nb_shots_matrix = shots_data["Number of shots"]
    total_shots = nb_shots_matrix.sum()
    
    # Tính ma trận chia sẻ % cú sút
    share_shots_matrix = (nb_shots_matrix / total_shots * 100) if total_shots > 0 else nb_shots_matrix

    # Lấy dữ liệu Goals (đã lọc)
    df_goals_filtered = df_shots[df_shots["Goal"] == 1].copy()
    metrics_goals = {"Number of goals": {"col": None, "agg": "count"}} # Đổi tên metrics cho đúng ngữ nghĩa

    _, goals_data, _, _ = pitch_visual.add_binned_heatmap(df_goals_filtered, metrics=metrics_goals, **bin_params)
    
    nb_goals_matrix = goals_data["Number of goals"]

    # Tính xác suất ghi bàn (Goals / Shots)
    # Sử dụng np.divide để xử lý chia cho 0 an toàn
    scoring_prob_matrix = np.divide(
        nb_goals_matrix, 
        nb_shots_matrix, 
        out=np.zeros_like(nb_goals_matrix, dtype=float), 
        where=nb_shots_matrix != 0
    ) * 100

    # --- BƯỚC 5: VẼ BIỂU ĐỒ ---
    dict_info = {
        "Scoring probability (in %)": {"values": scoring_prob_matrix, "display_type": ".1f"},
        "Share of shots (in %)":      {"values": share_shots_matrix,  "display_type": ".2f"},
        "Number of shots":            {"values": nb_shots_matrix,     "display_type": ".0f"},
        "Number of goals":            {"values": nb_goals_matrix,     "display_type": ".0f"}
    }
    
    # 
    # Vẽ heatmap cuối cùng
    fig = pitch_visual.add_heatmap_(
        scoring_prob_matrix, 
        x, y, 
        dict_infor=dict_info, 
        title="Probability to score (Filtered Outliers)", 
        opacity=0.9
    )

    return fig


##phần mô đánh giá mô hình xG
def compute_calibration_data(
    df,
    prob_col,
    target_col="Goal",
    n_bins=10
):
    """
    Return dataframe with:
    - mean_predicted_prob
    - observed_goal_rate
    """

    bins = np.linspace(0, 1, n_bins + 1)
    df_tmp = df[[prob_col, target_col]].copy()
    df_tmp["bin"] = pd.cut(df_tmp[prob_col], bins=bins, include_lowest=True)

    calib = (
        df_tmp
        .groupby("bin")
        .agg(
            mean_predicted_prob=(prob_col, "mean"),
            observed_goal_rate=(target_col, "mean"),
            count=(target_col, "size")
        )
        .dropna()
        .reset_index()
    )

    return calib







