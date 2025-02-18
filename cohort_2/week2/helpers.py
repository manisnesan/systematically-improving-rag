import itertools
from lancedb.rerankers import Reranker
from lancedb.table import Table


def calculate_mrr(predictions: list[str], gt: list[str]):
    mrr = 0
    for label in gt:
        if label in predictions:
            mrr = max(mrr, 1 / (predictions.index(label) + 1))
    return mrr


def get_recall(predictions: list[str], gt: list[str]):
    return len([label for label in gt if label in predictions]) / len(gt)


def get_metrics_at_k(
    metrics: list[str],
    sizes: list[int],
):
    metric_to_score_fn = {
        "mrr": calculate_mrr,
        "recall": get_recall,
    }

    for metric in metrics:
        if metric not in metric_to_score_fn:
            raise ValueError(f"Metric {metric} not supported")

    eval_metrics = [(metric, metric_to_score_fn[metric]) for metric in metrics]

    return {
        f"{metric_name}@{size}": lambda predictions, gt, m=metric_fn, s=size: (
            lambda p, g: m(p[:s], g)
        )(predictions, gt)
        for (metric_name, metric_fn), size in itertools.product(eval_metrics, sizes)
    }


def task(user_query: str, table: Table, reranker: Reranker, max_k: int):
    query = table.search(user_query, query_type="vector").limit(max_k)

    if reranker:
        query = query.rerank(reranker)

    return [item["text"] for item in query.to_list()]
