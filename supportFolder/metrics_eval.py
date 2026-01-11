import numpy as np
from sklearn import metrics
import plotly.graph_objects as go

def compute_classification_metrics(y_true, y_prob, threshold=0.5, model_name=None):
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
            print(f"{k:20s}: {v*100:6.2f}%")
        else:
            print(f"{k:20s}: {v:.5f}")

    print(f"Threshold used      : {threshold:.2f}\n")

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


