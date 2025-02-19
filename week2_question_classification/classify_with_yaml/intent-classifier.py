import openai
import instructor
from yaml_classifier import YamlClassifier
from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List

client = instructor.from_openai(openai.OpenAI())

classifier = YamlClassifier.load("portal-search.yaml")


class Prediction(BaseModel):
    correct_labels: List[str] = Field(
        description="The predicted label(s) as a list of strings"
    )

    @field_validator("correct_labels")
    def validate_labels(cls, v, info: ValidationInfo):
        labels = info.context["labels"]
        for label in v:
            if label not in labels:
                raise ValueError(f"Label {label} not in {labels}")
        return v


class PredictionWithReasoning(Prediction):
    reasoning: str = Field(
        description="A detailed explanation of the thought process leading to the prediction, including key factors considered, comparisons to label descriptions and examples, and how the query's content and intent align with the chosen label"
    )

def main():
    samples = [    "Failed to parse JWT",     "how to send NMI to ILO",     "/user/1000",
    ]


    examples = [
        "Failed to get a valid plugin manifest from /api/plugins/monitoring-plugin/",
        "Failed to parse JWT",
        "Failed to pull image 192.168.70.9:5000/rhosp-rhel8/openstack-mistral-engine:16.2",
        "Failed to start ContainerManager",
        "Failed unmounting /var",
        '"Fatal IO error" on X server',
        "CVE-2016-2183",
        "CVE-2022-48566",
        "CVE-2024-20918",
        "CVE-2024-23334",
        "RHSA-2020:5437",
        "RHSA-2021:4788",
        "RHSA-2023:7201",
        "RHSA-2023:7166: tpm2-tss",
        "how to send NMI to ILO",
        "how do I log out of the customer portal?",
        "Which package provides the library libnsl.so.1",
        "Which version of Red Hat Enterprise Linux (RHEL) includes the OpenSSL 3",
        "Which command can the cluster administrator use to identify deprecated API resources",
        "/run/user/1000",
        "/user/1000",
        "BufferOverflowException 8190",
        "BufferOverflowException 48190"
    ]


    # Example without reasoning

    # Process each example
    for example in samples:
        try:
            resp = classifier.predict(
                query=example,
                response_model=PredictionWithReasoning,
                client=client,
                model="gpt-4o-mini"
            )
            print(f"Query: {example}")
            print(resp.model_dump_json(indent=2))
            print("---")
        except Exception as e:
            print(f"Error processing query: {example}")
            print(f"Error: {str(e)}")
            print("---")

    # Example with batch prediction with asyncio
    # from asyncio import run, gather

    # client = instructor.from_openai(openai.AsyncOpenAI())



    # async def run_predictions():
    #     tasks = [
    #         classifier.apredict(
    #             client=client,  # type: ignore
    #             model="gpt-4o-mini",
    #             query=query,
    #             response_model=Prediction,
    #         )
    #         for query in examples
    #     ]
    #     return await gather(*tasks)


    # resp = run(run_predictions())

    # for r in resp:
    #     print(r.model_dump_json(indent=2))

if __name__ == "__main__":
    main()