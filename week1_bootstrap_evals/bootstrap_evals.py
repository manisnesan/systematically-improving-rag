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
    question_with_context: str


def run_simple_request(q: EvalQuestion, n_return_vals, rerank=False):
    
    if rerank:
        results = (
            reviews_table.search(q.question_with_context, query_type=QUERY_TYPE)
#                .rerank(LinearCombinationReranker(weight=0.3)) # TODO: rerank is not working as expected, it raises a ValueError
                .select(["id"])
                .limit(n_return_vals)
                .to_list()
        )
    else:
        results = (
            reviews_table.search(q.question_with_context, query_type=QUERY_TYPE)
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
    # results = (reviews_table.search(q.question_with_context, query_type='auto') # query_type "auto" checks if the table has vector column then default to vector search
    #             .select(['id', 'review'])
    #             .limit(n_return_vals)
    #             .to_pandas())
    
    # print(q.question_with_context)
    # print(results)
    
    ## first stage retrieval
    # k_to_retrieve = [5, 10]
    # scores = pd.DataFrame([score_simple_search(n, eval_questions) for n in k_to_retrieve])
    # scores["n_retrieved"] = k_to_retrieve
    # print(scores)

    # reranking using lance
    # k_to_retrieve = [5, 10]
    # print("***** Reranking ****** ")
    # scores = pd.DataFrame([score_simple_search(n, eval_questions, rerank=True) for n in k_to_retrieve])
    # scores["n_retrieved"] = k_to_retrieve
    # print(scores)

    # reranking using cohere
    try:
        from scoring_utils import score_reranked_search_with_rate_limit_support
        
        k_to_retrieve = [5, 10]
        reranked_scores = score_reranked_search_with_rate_limit_support(eval_questions, reviews_table, k_to_retrieve)
        reranked_scores_df = pd.DataFrame([
                            {"precision": scores["precision"], "recall": scores["recall"], "n_retrieved": k}
                            for k, scores in reranked_scores.items()
        ])
        print(reranked_scores_df)

    except Exception as e:
        print(f"Could not run reranker.\n{e}")
        print("Ensure COHERE_API_KEY env is set... and cohere library diskcache are installed.")
        print("Connection reset by peer is likely rate limiting from Cohere")

    # vector
    # precision    recall  n_retrieved
    # 0   0.000667  0.003333            5
    # 1   0.000778  0.007778           10

    # fts
    # precision    recall  n_retrieved
    # 0   0.011778  0.058889            5
    # 1   0.012000  0.120000           10

    # hybrid with Linear Combination Reranker with weight of 0.7 provided to vector search
    # precision    recall  n_retrieved
    # 0   0.012667  0.063333            5
    # 1   0.011889  0.118889           10