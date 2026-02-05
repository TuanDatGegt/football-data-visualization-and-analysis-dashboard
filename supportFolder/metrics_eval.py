import numpy as np
import pandas as pd
from sklearn import metrics
import plotly.graph_objects as go
from supportFolder.heatmap_xG import compute_calibration_data   # hoặc cùng file

def compute_classification_metrics(y_true, y_prob, threshold=0.104, model_name=None):
    """
    Compute and print classification metrics.
    """
    y_pred = (y_prob >= threshold).astype(int)

    results = {
        "Log loss": metrics.log_loss(y_true, y_prob),
        "AUC": metrics.roc_auc_score(y_true, y_prob),
        "Precision": metrics.precision_score(y_true, y_pred),
        "Recall": metrics.recall_score(y_true, y_pred),
        "F1-score": metrics.f1_score(y_true, y_pred),
        "Balanced Accuracy": metrics.balanced_accuracy_score(y_true, y_pred)
    }

    header = f"Các chỉ số đánh giá ({model_name})" if model_name else "Các chỉ số đánh giá"
    print("=" * len(header))
    print(header)
    print("=" * len(header))

    percent_metrics = {"AUC", "Precision", "Recall", "F1-score", "Balanced Accuracy"}

    for k, v in results.items():
        if k in percent_metrics:
            print(f"{k:20s}: {v*100:6.5f}%")
        else:
            print(f"{k:20s}: {v:.5f}")

    print(f"Threshold used      : {threshold:.5f}\n")

    return results



def plot_mertrics_comparison(metrics_dict, metric_name):
    """
    metrics_dict = {
        "Baseline": {...},
        "With angle": {...},
        "Head/body interaction": {...}
    }
    """

    models = list(metrics_dict.keys())
    values = [metrics_dict[m][metric_name] for m in models]

    # convert to percentage if needed
    if metric_name != "Log loss":
        values = [v * 100 for v in values]
        y_title = f"{metric_name} (%)"
    else:
        y_title = metric_name

    fig = go.Figure(
        data=[go.Bar(x=models, y=values)]
    )

    fig.update_layout(
        title=f"So sánh {metric_name} giữa các mô hình",
        xaxis_title="Mô hình / Tập đặc trưng",
        yaxis_title=y_title,
        template="plotly_white"
    )

    return fig



def build_xg_calibration_figure(
    df,
    models=("lr", "rf", "svm")
):
    fig = go.Figure()

    MODEL_CONFIG = {
        "lr": {
            "col": "prediction_lr",
            "label": "Logistic Regression"
        },
        "rf": {
            "col": "prediction_rf",
            "label": "Random Forest"
        },
        "svm": {
            "col": "prediction_svm",
            "label": "SVM (RBF)"
        }
    }

    for m in models:
        if m not in MODEL_CONFIG:
            continue

        cfg = MODEL_CONFIG[m]
        calib_df = compute_calibration_data(df, cfg["col"])

        fig.add_trace(
            go.Scatter(
                x=calib_df["mean_predicted_prob"],
                y=calib_df["observed_goal_rate"],
                mode="lines+markers",
                name=cfg["label"]
            )
        )

    # Perfect calibration line
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Perfect calibration",
            line=dict(dash="dash", color="gray"),
            showlegend=True
        )
    )

    fig.update_layout(
        title="xG Calibration Curves",
        xaxis_title="Predicted probability (xG)",
        yaxis_title="Observed goal frequency",

        legend=dict(
            orientation="h",      # 👈 legend nằm ngang
            yanchor="top",
            y=-0.25,               # 👈 hạ xuống dưới plot
            xanchor="center",
            x=0.5
        ),

        margin=dict(
            t=60,
            b=90                  # 👈 chừa không gian cho legend
        ),

        template="plotly_white"
    )


    return fig


def build_roc_curve_figure(
    df,
    models=("lr", "rf", "svm"),
    y_col="Goal"
):
    fig = go.Figure()

    MODEL_CONFIG = {
        "lr": {
            "col": "prediction_lr",
            "label": "Logistic Regression"
        },
        "rf": {
            "col": "prediction_rf",
            "label": "Random Forest"
        },
        "svm": {
            "col": "prediction_svm",
            "label": "SVM (RBF)"
        }
    }

    y_true = df[y_col].values

    for m in models:
        if m not in MODEL_CONFIG:
            continue

        cfg = MODEL_CONFIG[m]
        y_prob = df[cfg["col"]].values

        fpr, tpr, _ = metrics.roc_curve(y_true, y_prob)
        auc_score = metrics.roc_auc_score(y_true, y_prob)

        fig.add_trace(
            go.Scatter(
                x=fpr,
                y=tpr,
                mode="lines",
                name=cfg["label"]
            )
        )

    # Random guess line
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="Random guess",
            line=dict(dash="dash", color="gray")
        )
    )

    fig.update_layout(
        title="ROC Curves for xG Models",
        xaxis_title="False Positive Rate (1 - Specificity)",
        yaxis_title="True Positive Rate (Sensitivity)",

        # 🔴 QUAN TRỌNG: khóa tỉ lệ trục
        xaxis=dict(range=[0, 1], constrain="domain"),
        yaxis=dict(range=[0, 1], scaleanchor="x", scaleratio=1),

        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=60, b=90)
    )

    return fig



def assign_predicted_label(df, prob_col, threshold):
    df = df.copy()
    df["y_pred"] = (df[prob_col] >= threshold).astype(int)
    return df


def compute_confusion_counts(df, label_col="Goal", pred_col="y_pred"):
    TP = ((df[label_col] == 1) & (df[pred_col] == 1)).sum()
    FP = ((df[label_col] == 0) & (df[pred_col] == 1)).sum()
    TN = ((df[label_col] == 0) & (df[pred_col] == 0)).sum()
    FN = ((df[label_col] == 1) & (df[pred_col] == 0)).sum()

    return {
        "TP": TP,
        "FP": FP,
        "TN": TN,
        "FN": FN
    }


def build_confusion_df(df, prob_col, threshold):
    df_pred = assign_predicted_label(df, prob_col, threshold)
    counts = compute_confusion_counts(df_pred)

    return pd.DataFrame([counts])




