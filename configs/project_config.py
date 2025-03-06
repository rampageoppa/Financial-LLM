"""
project_config.py

Contains project-specific configuration values such as model hyperparameters,
retriever settings, and prompt templates.
Compatible with Python 3.1 by avoiding variable annotations and f-strings.
"""

class ProjectConfig(object):
    """
    Project-level configuration class for model hyperparameters, retriever
    settings, and any other domain-specific parameters or constants.
    """

    # Default embedding model and usage settings
    EMBEDDINGS_MODEL_NAME = "multilingual-e5-large"

    # Other project-wide constants
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 20

    # LangChain integration settings
    LANGCHAIN_TRACING_V2 = "true"
    LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY = "YOUR-LANGCHAIN-API-KEY"
    LANGCHAIN_PROJECT = "RAG for public firm"

    # Prompt Templates and Questions
    PROMPT_TEMPLATE = """
    You are the CEO of {company_name}, identified by the CIK number {cik}. The current year is {fyear}.

    Based on the annual reports provided and the information from similar companies, please perform the following tasks and provide detailed analyses.

    === ANNUAL REPORTS FOR {company_name} (PAST YEARS) ===
    {context}
    END OF REPORTS

    === ANNUAL REPORTS FROM SIMILAR INDUSTRIES (PAST YEARS) ===
    {context_same_SICH}
    END OF REPORTS

    === CHAT HISTORY ===
    {chat_history_str}
    END OF CHAT HISTORY

    === QUESTION ===
    {question}
    END OF QUESTION
    """

    QUESTION_1 = """
    1. Read the Business Description Section: Understand the company’s core business and strategic direction.
    2. Read the Management Discussion and Analysis: Analyze the MD&A section to grasp management’s interpretation of past performance, current challenges, and future outlook.
    3. Identify Current Investment Focus: Determine the company’s current projects and business model as disclosed in the annual report.
    4. Analyze the Market and Competitive Environment: Examine the industry dynamics and competitive environment mentioned in the annual report.

    Please provide a detailed report summarizing your findings from these steps.
    """

    QUESTION_2 = """
    Based on your previous analysis, your next task is to predict the company's next three potential projects for consideration.

    Instructions:

    Output Format: Provide your answer in the specified JSON format between the markers <BEGIN_JSON> and <END_JSON>. DO NOT include any other text or explanations within these markers.

    Formatting Guidelines:
        - The output should be a list of JSON objects.
        - Each object must include:
            "PROJECT": The name of the proposed project.
            "DESCRIPTION": A brief description of the project.
            "MARKET VALUE": Estimated market value in million dollars (discounted present value of future cash flows).
            "IMPLEMENTATION COST": Estimated cost to implement the project in million dollars (can be larger than the market value).
            "REASONING": Explanation for why this project is proposed.
            "CONFIDENCE": A confidence level in the prediction (0-100).
            "SIMILAR FIRMS": A list of three public firms engaged in similar businesses, including their names and tickers.
            "PRIORITY": A priority ranking (1-3).
            "PRIORITY_REASONING": Justification for the assigned priority.

    <BEGIN_JSON>
    [
      {
        "PROJECT": "project1",
        "DESCRIPTION": "description1",
        "MARKET VALUE": "value1",
        "IMPLEMENTATION COST": "cost1",
        "REASONING": "reasoning1",
        "CONFIDENCE": "0-100",
        "SIMILAR FIRMS": [
          {"NAME": "firm1_name", "TICKER": "firm1_ticker"},
          {"NAME": "firm2_name", "TICKER": "firm2_ticker"},
          {"NAME": "firm3_name", "TICKER": "firm3_ticker"}
        ],
        "PRIORITY": "1-3",
        "PRIORITY_REASONING": "reasoning_for_priority1"
      },
      {
        "PROJECT": "project2",
        "DESCRIPTION": "description2",
        "MARKET VALUE": "value2",
        "IMPLEMENTATION COST": "cost2",
        "REASONING": "reasoning2",
        "CONFIDENCE": "0-100",
        "SIMILAR FIRMS": [
          {"NAME": "firm1_name", "TICKER": "firm1_ticker"},
          {"NAME": "firm2_name", "TICKER": "firm2_ticker"},
          {"NAME": "firm3_name", "TICKER": "firm3_ticker"}
        ],
        "PRIORITY": "1-3",
        "PRIORITY_REASONING": "reasoning_for_priority2"
      },
      {
        "PROJECT": "project3",
        "DESCRIPTION": "description3",
        "MARKET VALUE": "value3",
        "IMPLEMENTATION COST": "cost3",
        "REASONING": "reasoning3",
        "CONFIDENCE": "0-100",
        "SIMILAR FIRMS": [
          {"NAME": "firm1_name", "TICKER": "firm1_ticker"},
          {"NAME": "firm2_name", "TICKER": "firm2_ticker"},
          {"NAME": "firm3_name", "TICKER": "firm3_ticker"}
        ],
        "PRIORITY": "1-3",
        "PRIORITY_REASONING": "reasoning_for_priority3"
      }
    ]
    <END_JSON>

    Note: Ensure all monetary values are in million dollars. Remember that the implementation cost can be larger than the market value of a project.
    """
