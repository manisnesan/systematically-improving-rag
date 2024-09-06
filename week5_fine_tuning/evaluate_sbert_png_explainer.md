Sure! The image you provided outlines the process of evaluating an SBERT (Sentence-BERT) cross-encoder using both a base model (non-fine-tuned) and a fine-tuned model. Here's a breakdown of the steps:

1. **Input Query and Corpus**: The process starts with an input query and a corpus of documents.

2. **Two Branches**:
   - **Base Cross Encoder Model**: This branch uses the base cross-encoder model that hasn't been fine-tuned.
   - **Fine-Tuned Cross Encoder Model**: This branch uses a cross-encoder model that has been fine-tuned.

3. **Compute Pairwise Similarity Scores**: Both models compute similarity scores between the input query and the documents in the corpus.

4. **Sort Based on Scores**: The documents are then sorted based on the computed similarity scores.

5. **Ranked Relevant Documents**: Finally, the sorted documents are output as ranked relevant documents.

Below the main flowchart, there are two sections for evaluating each model:

- **Model 1: eval**:
  - Load the base model.
  - Compute similarity scores using cosine similarity.
  - Sort documents based on these scores.
  - Output the ranked relevant documents.

- **Model 2: eval**:
  - Load the fine-tuned model.
  - Compute similarity scores using the dot product.
  - Sort documents based on these scores.
  - Output the ranked relevant documents.

This process helps compare the performance of the non-fine-tuned and fine-tuned models in ranking document relevance based on the input query. If you have any specific questions about this process or need further details, feel free to ask!