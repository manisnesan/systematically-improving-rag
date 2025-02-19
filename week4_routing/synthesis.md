# Key Takeaways

- Tools is another name for Intents. LLM detects which intent/tool the given question fall into and then call the function (routing) with the appropriate arguments.

## Functions to Call / Intents

- ShippingDateRequest(sku)
- ShippingCostRequest(shipping_location)
- ProductDimensionRequest(sku)
- PriceHistoryRequest(sku)
- ProductComparisonRequest(sku1, sku2)
- LogDesiredFeatureRequest(sku, user_id, desired_feature)
- ExtractDataFromImageRequest(image_url, question)
- ProductMaterialsRequest(sku)


# Appendix 

## Slide Notes

Retrival Indices
- Types of Indexes 
  - Knowledge Centered (Solutions, Articles, Labs)
  - Documentation 
  - Security (CVE, Errata)
  - Training
  - Containers

Index Data Model

Example
```
Blueprint:
  - description: str
  - date: str

  - extract_blueprint(image_url) -> Blueprint
```

**Defining the above index as a tool**
```
SearchBlueprint
  - blueprint_description
  - start_date
  - end_date

  - execute -> RankedResult
```

Given a user input question, create search blueprints using `SearchBlueprint` as Response Model with few shot examples. 

Define another index for Searching Text
```
SearchText
  - search_query
  - filter_by_type: Literal['contracts', 'proposals', 'bids', 'all']
  - end_date

  - execute -> RankedResult
```



