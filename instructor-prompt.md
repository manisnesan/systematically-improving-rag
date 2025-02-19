
As a genius expert, your task is to understand the content and provide the parsed objects in json that match the following json_schema:

{
  "properties": {
    "name": {
      "title": "Name",
      "type": "string"
    },
    "age": {
      "title": "Age",
      "type": "integer"
    },
    "fact": {
      "description": "A list of facts about the character",
      "items": {
        "type": "string"
      },
      "title": "Fact",
      "type": "array"
    }
  },
  "required": [
    "name",
    "age",
    "fact"
  ],
  "title": "Character",
  "type": "object"
}

Make sure to return an instance of the JSON, not the schema itself