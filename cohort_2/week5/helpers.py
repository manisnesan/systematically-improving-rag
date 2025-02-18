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

    return [item["id"] for item in query.to_list()]


def process_taxonomy_file(yaml_path: str) -> dict:
    """
    Process a taxonomy YAML file and extract taxonomy map, occasions, materials, and other relevant data.

    Args:
        yaml_path (str): Path to the taxonomy YAML file

    Returns:
        dict: Dictionary containing:
            - taxonomy_map: Nested dictionary mapping categories -> subcategories -> attributes
            - occasions: List of valid occasions
            - materials: List of valid materials
            - taxonomy: Raw taxonomy data
    """
    import yaml

    # Load the YAML file
    with open(yaml_path, "r") as f:
        taxonomy = yaml.safe_load(f)

    # Create taxonomy map
    taxonomy_map = {}
    for category in taxonomy["categories"]:
        cat_name = category["name"]
        taxonomy_map[cat_name] = {}

        for subcategory in category["subcategories"]:
            subcat_name = subcategory["name"]
            taxonomy_map[cat_name][subcat_name] = {}

            # Add product types
            taxonomy_map[cat_name][subcat_name]["product_type"] = subcategory.get(
                "types", []
            )

            # Add attributes and their values
            taxonomy_map[cat_name][subcat_name]["attributes"] = {}
            for attr in subcategory.get("attributes", []):
                for attr_name, values in attr.items():
                    taxonomy_map[cat_name][subcat_name]["attributes"][attr_name] = (
                        values
                    )

    # Extract occasions and materials from common attributes
    occasions = []
    materials = []
    common_attributes = {}
    for attr in taxonomy["common_attributes"]:
        if "Occasion" in attr:
            occasions = attr["Occasion"]
        elif "Material" in attr:
            materials = attr["Material"]

        attr_name = list(attr.keys())[0]
        attr_values = attr[attr_name]
        common_attributes[attr_name] = attr_values

    return {
        "taxonomy_map": taxonomy_map,
        "occasions": occasions,
        "materials": materials,
        "common_attributes": common_attributes,
        "taxonomy": taxonomy["categories"],  # Raw taxonomy data for reference
    }
