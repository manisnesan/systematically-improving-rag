These are thoughts that occurred when I reviewed the tool creation notebook.


- Review the user questions and identified questions that are not answerable by the current content.
- We identified that these questions could be answered by adding new datasrouce 

## Structured Output Extraction from Question using External Tools (Reads Data)

INTENT: `ShippingDate` | `ShippingCost`
ENTITIES: TEMPORAL | QUANTITY | COST | LOCATION

```
- `How many of these are available to be shipped right now?`
- `How much will it cost to ship this item to Florida?`
```

The default mode is instructor.Mode.TOOLS which is the recommended mode for OpenAI clients for __Structured Output Extraction__

System:
`You must always use tools`

User Question:
`When will this product be in stock again? And how much will it cost to ship this item to Florida?`

Mode:
**PARALLEL_TOOLS**

Enables to call multiple functions simulateneously in a single request.

See https://python.useinstructor.com/concepts/parallel/

When posed this question with the expected Response Model as `Iterable[ShippingCostRequest | ShippingDateRequest]` then 

Output:
```
[ShippingDateRequest(sku='1234567890'),
 ShippingCostRequest(sku='1234567890', shipping_location='Florida')]
```

These ShippingDateRequest can be individual arbitrary functions or API interfaces to satisfy that specific request. 

| Response Model | Function Call with args | 
| --- | --- |
| ShippingDateRequest | get_available_shipping_date(call.sku) |
| ShippingCostRequest | get_shipping_cost(call.shipping_location) |  
 
Calling arbitrary functions as we've seen hear opens up a wide range of data sources.

- Read from a database
- Calculations
- Side effects (e.g. write to a database, send an email)
- More LLM calls

Call functions to do more than reading data.

## Structured Output Extraction from Content using Tools (Write Data)

System:
Extract a list of atomic facts about a person that may help us recommend better tools for them in the future.

Content:
dan@gmail.com made the following request while viewing a 7" axe:
I'm looking for an axe with a rubberized handle. I have nerve damage in my elbow which makes hard handles painful. How hard is this axe handle? I will buy an axe with a soft handle if I can find it.

Response Model: `Iterable[Fact]`
Tools: `[{"type": "function", "function": log_requests}]`

Similarly extract stuctured data from question & content.

Example of preprocessing axe descriptions to populate a database of product specs for querying later. 

```
HandToolsStats
- tool_type: [axe, hammer, screwdriver, saw, other]
- handle_material (attribute)
- blade_material (attribute)
- weight_grams (attribute)
- color (attribute)
- length_cm (attribute)
- country_of_origin (source origin)
```

## Structured Output Extraction from non-text data

### Images

System:
Extract specs from the product description. Include all fields you can extract from the image.

User: 
```
Image:
- type: image_url
- image_url: 
    - url: $URL_VALUE
```

### Tables (OMG!!!)

_OMG!!. This is amazing especially extracting tables from slides!!!_

Data Model:
```
Table:
- caption: str
- md_dataframe: str
```

System: None

User:
```
Image:
- type: image_url
- image_url:
    url: $URL_VALUE

Text:
- type: text
- text: |
Analyze the image to determine appropriate headers for output tables.
For each identified table, create an informative h2 title and a concise description of the contents.
Finally, output the markdown representation of all data in the table/graph.

Escape the markdown table properly, and make sure to include the caption and the dataframe.
Only return a markdown table in dataframe, nothing else. Make sure to capture all data that should be in the table.

Capture visual data that is not explicitly labeled with text from the image
```

## Pydantic Custom Type

```
from pydantic import BaseModel

class Person(BaseModel):
    name: str
    age: int

person = Person(name="Alice", age=30)
```

Name type with built-in validation (`constr`)
```
from pydantic import constr

Name = constr(min_length=2, max_length=50)

class Person(BaseModel):
    name: Name
    age: int

person = Person(name="Alice", age=30)  # Valid
# person = Person(name="A", age=30)  # Would raise an error
```

Complex custom type using `Annotated` with both field validation & a custom validator.
```
from typing import Annotated
from pydantic import BaseModel, Field, validator

def validate_age(age: int) -> int:
    if age < 0 or age > 120:
        raise ValueError("Age must be between 0 and 120")
    return age

Age = Annotated[int, Field(ge=0, le=120), validator('age', allow_reuse=True)(validate_age)]

class Person(BaseModel):
    name: str
    age: Age

person = Person(name="Alice", age=30)  # Valid
# person = Person(name="Alice", age=150)  # Would raise an error
```

In this example, `MarkdownDataFrame` is a custom type that automatically converts markdown to a DataFrame when data is input, and converts back to markdown when the model is serialized.
```
from typing import Annotated
from pydantic import BaseModel, BeforeValidator, PlainSerializer
import pandas as pd

def md_to_df(data: str) -> pd.DataFrame:
    # Convert markdown to DataFrame (simplified for example)
    return pd.read_csv(StringIO(data), sep="|")

MarkdownDataFrame = Annotated[
    pd.DataFrame,
    BeforeValidator(md_to_df),
    PlainSerializer(lambda df: df.to_markdown())
]

class Report(BaseModel):
    title: str
    data: MarkdownDataFrame

markdown_data = """
| Name | Age |
|------|-----|
| Alice | 30 |
| Bob | 25 |
"""

report = Report(title="Employee Report", data=markdown_data)
print(report.data)  # This will be a pandas DataFrame
print(report.model_dump())  # This will include the markdown representation
```


## Structured Output Extraction into Dataframes from Images. 

DataModel:

```
Table:
- caption
- dataframe: MarkdownDataFrame
```

```
MultipleTables:
- tables: List[Table]
```

ResponseModel: MultipleTables

User:
- type: image_url
- image_url:
  - url: $URL

Same as above

Caveat:
- Slow to call all tools for all queries.

# Appendix 

- [HW] Structured Output from Cases
  - Similar to how the HandToolStats are extracted, we can extract structured data from the support case.
  - Question: QuestionType{NLQ, Error, Multilingual}, Entities{Product, Component, SBR, Tag}, Symptoms present, Served_by_Chunk_Document_Summary, is_1Turn, IssueType, AttachmentRequired

- [HW] Expanding Structured Output Content using Labs.

Similarly can extract Labs

```
Labs
- type: [Configuration, Deployment, Security, Troubleshoot]
- product and version
- [SAMPLE_QUESTIONS]
- component
- sbr, tag
- CUSTOMER_SITUATIONAL_CONTEXT (eg: when user about to migrate, when affected by a given vulnerability)
```

Enhanced Data Model for Labs.
```
Labs
- lab_name (string)
- lab_description (text)
- type: [Configuration, Deployment, Security, Troubleshoot, Management, Performance]
- difficulty_level: [Beginner, Intermediate, Advanced]
- estimated_time (in minutes)
- applicable_product_versions (list)
- related_products (list)
- components (list)
- prerequisites (list)
- sample_questions (list)
- customer_situational_context (text)
- customer_input_required (list)
- lab_steps (list of ordered steps)
- lab_output (text or list)
- additional_resources (list of URLs)
- tags (list)
- sbr (string, if applicable)
```

Example Data Model for SSH Vulnerability Helper Lab
```
Labs
- lab_name: "SSH Vulnerability Helper"
- lab_description: "This application helps you mitigate known SSH vulnerabilities reported for Red Hat Enterprise Linux 7, 8, and 9. It provides proactive solutions for critical vulnerabilities, enabling faster resolution."
- type: [Security, Troubleshoot]
- difficulty_level: Intermediate
- estimated_time: 30
- applicable_product_versions: ["Red Hat Enterprise Linux 7", "Red Hat Enterprise Linux 8", "Red Hat Enterprise Linux 9"]
- related_products: ["Red Hat Enterprise Linux"]
- components: ["SSH", "Security"]
- prerequisites: ["Access to Red Hat Enterprise Linux system", "Basic knowledge of SSH configuration"]
- sample_questions: 
  - "How can I identify SSH vulnerabilities in my RHEL system?"
  - "What steps should I take to mitigate SSH vulnerabilities?"
  - "Which SSH vulnerabilities affect my version of RHEL?"
- customer_situational_context: "When a user needs to assess and mitigate SSH vulnerabilities in their Red Hat Enterprise Linux environment, particularly after security announcements or as part of regular security maintenance."
- customer_input_required: 
  - "RHEL version (7, 8, or 9)"
  - "Current SSH configuration details"
- lab_steps:
  1. "Access the SSH Vulnerability Helper application"
  2. "Select your RHEL version (7, 8, or 9)"
  3. "Review the list of known SSH vulnerabilities for your version"
  4. "For each vulnerability, read the description and impact"
  5. "Follow the provided mitigation steps for each applicable vulnerability"
  6. "Verify the changes using the suggested commands or methods"
  7. "Repeat the process for any other RHEL systems you manage"
- lab_output: 
  - "A list of mitigated SSH vulnerabilities"
  - "Updated SSH configurations for improved security"
  - "Verification results for each applied mitigation"
- additional_resources: 
  - "https://access.redhat.com/security/vulnerabilities"
  - "https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/securing_networks/using-secure-communications-between-two-systems-with-openssh_securing-networks"
- tags: ["SSH", "Security", "Vulnerability", "RHEL", "Mitigation"]
- sbr: "Security Vulnerabilities"
```

```
Labs
- lab_name: "VNC Configurator for RHEL"
- lab_description: "This lab guides you through the process of installing, configuring, and validating VNC (Virtual Network Computing) on Red Hat Enterprise Linux systems. It provides both automatic configuration options and validation tools for existing VNC setups."
- type: [Configuration, Security]
- difficulty_level: Intermediate
- estimated_time: 60
- applicable_product_versions: ["Red Hat Enterprise Linux 7", "Red Hat Enterprise Linux 8", "Red Hat Enterprise Linux 9"]
- related_products: ["Red Hat Enterprise Linux"]
- components: ["VNC", "TigerVNC", "Networking"]
- prerequisites: 
  - "Access to a Red Hat Enterprise Linux system with root privileges"
  - "Basic knowledge of Linux command line"
  - "Understanding of networking concepts"
- sample_questions:
  - "How do I install VNC on my RHEL system?"
  - "What are the best security practices for configuring VNC?"
  - "How can I validate my existing VNC configuration?"
  - "What are the steps to make VNC start automatically on system boot?"
- customer_situational_context: "When a user needs to set up remote desktop access to their RHEL server, either for personal use or to allow team members to access the system graphically from remote locations."
- customer_input_required:
  - "RHEL version (7, 8, or 9)"
  - "Desired VNC port number"
  - "Preferred VNC password"
  - "Network firewall details (if any)"
- lab_steps:
  1. "Install VNC server packages"
  2. "Configure VNC server settings"
  3. "Set up VNC passwords"
  4. "Configure firewall rules for VNC"
  5. "Start and enable VNC service"
  6. "Validate VNC configuration"
  7. "Test VNC connection"
  8. "Configure automatic startup (optional)"
  9. "Implement additional security measures"
- lab_output:
  - "A fully configured and operational VNC server on RHEL"
  - "Validation report of VNC configuration"
  - "List of open ports and firewall rules for VNC"
  - "Instructions for connecting to the VNC server"
- additional_resources:
  - "https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_basic_system_settings/configuring-vnc-server_configuring-basic-system-settings"
  - "https://access.redhat.com/solutions/5588"
  - "https://www.redhat.com/sysadmin/vnc-screen-sharing-linux"
- tags: ["VNC", "Remote Desktop", "RHEL", "TigerVNC", "Security", "Networking"]
- sbr: "Desktop"
```

Postfix

```
Labs
- lab_name: "Postfix Configuration and Troubleshooting Helper"
- lab_description: "This lab guides you through the process of configuring, optimizing, and troubleshooting Postfix on Red Hat Enterprise Linux systems. It covers both general Postfix configuration and specific relaying scenarios, providing step-by-step assistance for common issues and best practices."
- type: [Configuration, Troubleshoot]
- difficulty_level: Intermediate
- estimated_time: 90
- applicable_product_versions: ["Red Hat Enterprise Linux 7", "Red Hat Enterprise Linux 8", "Red Hat Enterprise Linux 9"]
- related_products: ["Red Hat Enterprise Linux"]
- components: ["Postfix", "SMTP", "Mail Server"]
- prerequisites:
  - "Access to a Red Hat Enterprise Linux system with root privileges"
  - "Basic knowledge of Linux command line"
  - "Understanding of email server concepts and SMTP protocol"
  - "Existing Postfix installation (the lab will guide through installation if not present)"
- sample_questions:
  - "How do I configure Postfix as a null client?"
  - "What are the best practices for securing Postfix?"
  - "How can I set up Postfix to relay through an external SMTP server?"
  - "What steps should I take to troubleshoot mail delivery issues?"
  - "How do I configure SPF, DKIM, and DMARC with Postfix?"
- customer_situational_context: 
  "1. Postfix Configuration: When a user needs to set up a new Postfix server, optimize an existing configuration, or implement specific mail routing policies.
   2. Postfix Relaying: When a user needs to configure Postfix to relay emails through an external SMTP server, set up smart host configuration, or troubleshoot relaying issues."
- customer_input_required:
  - "RHEL version (7, 8, or 9)"
  - "Current Postfix configuration files (if existing)"
  - "Desired mail routing policies"
  - "External SMTP relay information (if applicable)"
  - "Domain name and DNS records"
- lab_steps:
  1. "Verify Postfix installation or install if necessary"
  2. "Review current Postfix configuration"
  3. "Configure basic Postfix settings"
  4. "Set up mail routing policies"
  5. "Configure relaying (if applicable)"
  6. "Implement security measures (SASL, TLS)"
  7. "Set up SPF, DKIM, and DMARC"
  8. "Test mail sending and receiving"
  9. "Troubleshoot common issues"
  10. "Optimize Postfix performance"
  11. "Configure logging and monitoring"
- lab_output:
  - "A fully configured and operational Postfix server"
  - "Documented mail routing policies"
  - "Secure relay configuration (if applicable)"
  - "Implemented SPF, DKIM, and DMARC configurations"
  - "Troubleshooting guide for common Postfix issues"
  - "Performance optimization recommendations"
- additional_resources:
  - "https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_basic_system_settings/assembly_configuring-postfix_configuring-basic-system-settings"
  - "https://access.redhat.com/solutions/1466263"
  - "https://www.redhat.com/sysadmin/postfix-email-server"
- tags: ["Postfix", "SMTP", "Mail Server", "Email Relay", "RHEL", "Security", "Troubleshooting"]
- sbr: "Services"
```

