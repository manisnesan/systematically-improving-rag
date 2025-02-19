Adopt the Top Down Learning approach https://forums.fast.ai/t/learning-strategy-for-top-down-approach/66173 
Status: Pass 1
Read the slides. Watch the lecture once. Run the notebook. Create Zoterno notes and Synthesis.md. Complete the HW.

Review the zotero notes for the HW present in the slides.

## DOING

- [NB_Week1] - Refactoring metrics into a module and gettings benchmark evals using fts, vector, hybrid, cohere reranker.
- [NB_Week4] - Benchmark tool retrieval
- [Week5] - Reviewed the evaluate_sbert.py script and synthesized into a excalidraw diagram.

## TODO

- [Slides_Week1] - Generate Synthetic data from Content (1. Labs, 2. Solutions 3. Documentation). Establish baseline for Recall, Precision, Lexical Search, Semantic Search, Reranker.
- [Lecture_Week1] - Review the Lecture from Week 1 and also the Guest Lecture.
- [HW_Week3] - Extracted Structured Output from Labs & Create Labs Index.
- [HW] Extract Structured Output from Cases. 
  - Question: QuestionType{NLQ, Error, Multilingual}, Entities{Product, Component, SBR, Tag}, Symptoms present, Served_by_Chunk_Document_Summary, is_1Turn, IssueType, AttachmentRequired

- [Week1_Suggested_Refinements] - Improve retrieval component (lexical enhancement, integrate vector search), Enhance with more powerful rerankers, Blend both lexical and semantic search
- Week 2 Suggested Refinments - BertTopic Clustering and Identify topics with low recall 

## DONE

- [Week3] Rerun tool creation
- [Week2] Rerun Yaml and RAG Classifier. Key takeaways are if you have identified topics, able to collect positive and negative examples then use YamlClassifier. If not use RAG Classifier based on similairty.
- [HW_Week1] 
  - Submission in [Slack](https://improvingrag.slack.com/archives/C07EY6ML4PJ/p1723240648008799)
  - Review by AI [Perplexity](https://www.perplexity.ai/search/you-are-a-expert-teaching-assi-s3liPHuVQRWe043xDbmbqw)
  - Case Analysis to perform Error Analysis Review - See the Google Doc
- [Week1] Rerun make_product_reviews, make_synthetic_questions, metrics nbs. 

## APPENDIX 

### Suggestions for Week 1 Submission from Instructor

via [Perplexity](https://www.perplexity.ai/search/you-are-a-expert-teaching-assi-s3liPHuVQRWe043xDbmbqw)

Thank you for sharing the additional suggestions from the instructor. I'll review and restate these suggestions in a gradual complexity manner for better clarity.

#### 1. Blending Semantic Search

Suggestion: Implement semantic search alongside lexical search to improve recall.

Gradual complexity approach:
1. Basic: Implement a simple semantic search using pre-trained embeddings (e.g., BERT or SBERT).
2. Intermediate: Combine lexical and semantic search results using a basic ranking fusion method (e.g., reciprocal rank fusion).
3. Advanced: Fine-tune embeddings on your domain-specific data and implement a more sophisticated hybrid retrieval system.

#### 2. Clarify Retrieval Units

Suggestion: Specify whether the retrieval is based on passages or entire documents.

Gradual complexity approach:
1. Basic: Clearly define the unit of retrieval (passages or documents) in your evaluation metrics.
2. Intermediate: If using documents, experiment with passage-level retrieval to potentially improve granularity.
3. Advanced: Implement a hierarchical retrieval system that considers both passage and document-level relevance.

#### 3. Topic Clustering Analysis

Suggestion: Use BERTopic to cluster the dataset and analyze recall across different topics.

Gradual complexity approach:
1. Basic: Apply BERTopic to cluster your dataset into main topics.
2. Intermediate: Calculate and compare recall rates for each identified topic.
3. Advanced: Analyze low-performing topics in detail, considering factors like vocabulary, query complexity, and data distribution.

These suggestions provide valuable directions for improving your retrieval system:

1. Blending semantic search could significantly boost your recall, especially at higher k values.
2. Clarifying the retrieval units (passages vs. documents) will help in better understanding and potentially improving your system's performance.
3. Topic clustering analysis can uncover patterns in your data that might be affecting recall rates, allowing for targeted improvements.

By approaching these suggestions in a gradual manner, you can systematically enhance your system while gaining deeper insights into its performance across different aspects of your dataset.
