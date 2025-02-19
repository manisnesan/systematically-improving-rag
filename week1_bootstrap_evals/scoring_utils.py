import cohere
from diskcache import Cache
import lancedb
import os
from typing import List, Dict

from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

assert os.getenv("COHERE_API_KEY")
cohere_api_key = os.environ["COHERE_API_KEY"]


class EvalQuestion(BaseModel):
    question: str
    answer: str
    chunk_id: str
    question_with_context: str


def score(hits):
    n_retrieval_requests = len(hits)
    total_retrievals = sum(len(l) for l in hits)
    true_positives = sum(sum(sublist) for sublist in hits)
    precision = true_positives / total_retrievals if total_retrievals > 0 else 0
    recall = true_positives / n_retrieval_requests if n_retrieval_requests > 0 else 0
    return {"precision": precision, "recall": recall}


def run_reranked_request(
    q: EvalQuestion,
    reviews_table: lancedb.table.LanceTable,
    max_n_return_vals: int,
    n_to_rerank: int = 40,
    model: str = "rerank-english-v3.0",
) -> List[bool]:
    cache = Cache("./cohere_cache")
    cache_key = f"{q.question_with_context}_{max_n_return_vals}_{model}".replace(
        "?", ""
    )

    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return cached_result

    initial_results = (
        reviews_table.search(q.question_with_context)
        .select(["id", "review"])
        .limit(n_to_rerank)
        .to_list()
    )

    texts = [r["review"] for r in initial_results]

    # Rerank using Cohere
    co = cohere.Client(cohere_api_key)
    reranked = co.rerank(
        query=q.question_with_context,
        documents=texts,
        top_n=max_n_return_vals,
        model=model,
    )

    # Map reranked results back to original IDs
    reranked_ids = [initial_results[r.index]["id"] for r in reranked.results]
    result = [str(q.chunk_id) == str(r) for r in reranked_ids]
    cache.set(cache_key, result)
    return result


def score_reranked_search(
    eval_questions: List[EvalQuestion],
    reviews_table: lancedb.table.LanceTable,
    k_values: List[int],
    n_to_rerank: int = 40,
    model="rerank-english-v3.0",
) -> Dict[int, Dict[str, float]]:
    max_k = max(k_values)
    with ThreadPoolExecutor() as executor:
        all_hits = list(
            executor.map(
                lambda q: run_reranked_request(
                    q, reviews_table, max_k, n_to_rerank, model
                ),
                eval_questions,
            )
        )

    results = {}
    for k in k_values:
        hits = [h[:k] for h in all_hits]
        results[k] = score(hits)

    return results

import time  # Add this import at the top of the file

def score_reranked_search_with_rate_limit_support(
    eval_questions: List[EvalQuestion],
    reviews_table: lancedb.table.LanceTable,
    k_values: List[int],
    n_to_rerank: int = 40,
    model="rerank-english-v3.0",
) -> Dict[int, Dict[str, float]]:
    max_k = max(k_values)
    all_hits = []  # Initialize all_hits here
    results = {}
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for i, q in enumerate(eval_questions):
            # Rate limiting: wait if necessary
            if i > 0 and i % 10 == 0:  # Every 10 requests
                time.sleep(60)  # Wait for 60 seconds
            
            futures.append(
                executor.submit(
                    run_reranked_request,
                    q, reviews_table, max_k, n_to_rerank, model
                )
            )

        # Collect results after all submissions
        for future in futures:
            all_hits.append(future.result())

    for k in k_values:
        hits = [h[:k] for h in all_hits]
        results[k] = score(hits)

    return results