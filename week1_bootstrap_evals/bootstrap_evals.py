import json
import lancedb
import os
import pandas as pd
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from lancedb.rerankers import LinearCombinationReranker

# Related to Hybrid Searhc
# https://blog.lancedb.com/hybrid-search-and-reranking-report/

QUERY_TYPE = 'hybrid' # auto, vector, fts, hybrid Note: # query_type "auto" checks if the table has vector column then default to vector search


class EvalQuestion(BaseModel):
    question: str
    answer: str
    chunk_id: str


def run_simple_request(q: EvalQuestion, n_return_vals, rerank=False):
    
    if rerank:
        results = (
            reviews_table.search(q.question, query_type=QUERY_TYPE)
                # .rerank(LinearCombinationReranker(weight=0.3)) # TODO: rerank is not working as expected, it raises a ValueError
                .select(["id"])
                .limit(n_return_vals)
                .to_list()
        )
    else:
        results = (
            reviews_table.search(q.question, query_type=QUERY_TYPE)
                .select(["id"])
                .limit(n_return_vals)
                .to_list()
        )
    return [
        str(q.chunk_id) == str(r["id"]) 
        for r in results
    ]


def score(hits):
    # This implementation assumes
    n_retrieval_requests = len(hits)
    total_retrievals = sum(len(l) for l in hits)
    true_positives = sum(
                        sum(sublist) 
                        for sublist in hits
                        )
    precision = true_positives / total_retrievals if total_retrievals > 0 else 0
    recall = true_positives / n_retrieval_requests if n_retrieval_requests > 0 else 0
    return {"precision": precision, "recall": recall}


def score_simple_search(n_to_retrieve: List[int], eval_questions: List[EvalQuestion], rerank=False) -> Dict[str, float]:
    # parallelize to speed this up 5-10X
    with ThreadPoolExecutor() as executor:    
        hits = list(
            executor.map(lambda q: run_simple_request(q, n_to_retrieve, rerank), eval_questions)
        )
    return score(hits)

if __name__ == "__main__":
    db = lancedb.connect("./lancedb")
    reviews_table = db.open_table("reviews")

    with open("synthetic_eval_dataset.json", "r") as f:
        synthetic_questions = json.load(f)

    eval_questions = [EvalQuestion(**question) for question in synthetic_questions]

    # q = eval_questions[0]
    # n_return_vals = 5
    # results = (reviews_table.search(q.question, query_type='fts') # query_type "auto" checks if the table has vector column then default to vector search
    #             .select(['id', 'review'])
    #             .limit(n_return_vals)
    #             .to_pandas())
    
    # print(q)
    # print(results)

    k_to_retrieve = [5, 10, 20]
    # scores = pd.DataFrame([score_simple_search(n, eval_questions) for n in k_to_retrieve])
    # scores["n_retrieved"] = k_to_retrieve
    
    # print(scores)

    # reranking
    scores = pd.DataFrame([score_simple_search(n, eval_questions, rerank=True) for n in k_to_retrieve])
    scores["n_retrieved"] = k_to_retrieve
    
    print(scores)

    # vector
    # precision    recall  n_retrieved
    # 0   0.000444  0.002222            5
    # 1   0.000556  0.005556           10
    # 2   0.000864  0.015556           20

    # fts
    # precision    recall  n_retrieved
    # 0   0.000889  0.004444            5
    # 1   0.001227  0.012222           10
    # 2   0.000877  0.015556           20

    # hybrid (default: Linear Combination Reranker) - works the same way as vector with weight 0.7 (provided to vector search)
    # precision    recall  n_retrieved
    # 0   0.000889  0.004444            5
    # 1   0.000556  0.005556           10
    # 2   0.000864  0.015556           20