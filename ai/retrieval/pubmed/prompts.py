SEARCH_TERM_GENERATION_PROMPT = """
# Doctor's question
{question}

# Instructions
You are an expert clinician. 
You are given a question from a doctor. 
Your task is to come up with new boolean search queries to be searched against a traditional literature database.
Follow the algorithm below

Algorithm:
    - Analyze the intent behind the question, identify what the doctor is really looking for
    - Extract keywords from the analysis
    - Come up with keyword pairs that preserve logic and intent behind the original question
    - Combine each pair with the "AND" operator.

Queries can have a maximum of 3 keywords.
Always respond in English.
Think step by step.
"""

SEARCH_TERM_GENERATION_WITH_ANALYSIS_PROMPT = """
# Doctor's question
{question}

# Preliminary Analysis
{analysis}

# Instruction
You are an expert clinician. 
You are given a question and a preliminary analysis about how to approach this question. 
Your task is to come up with new boolean search queries to be searched against a traditional literature database.
Follow the algorithm below

Algorithm:
    - Analyze the intent behind the question, identify what the doctor is really looking for
    - Extract keywords from the preliminary analysis
    - Come up with keyword pairs that preserve logic and intent behind the original question
    - Combine each pair with the "AND" operator.

Queries can have a maximum of 3 keywords.
Always respond in English.
Think step by step.
"""

SEARCH_TERM_GENERATION_WITH_RECORD_AND_ANALYSIS_PROMPT = """
# Doctor's question
{question}

# Patient Record
{record}

# Analysis
{analysis}

# Instruction
You are an expert clinician. 
You are given a patient, a question concerning the patient and a preliminary analysis about how to approach this question. 
Your task is to come up with new boolean search queries to be searched against a traditional literature database.
Follow the algorithm below

Algorithm:
    - Analyze the patient record and then identify intent behind the question, identify what the doctor is really looking for
    - Extract keywords from the preliminary analysis
    - Come up with keyword pairs that preserve logic and intent behind the original question
    - Combine each pair with the "AND" operator.

Queries can have a maximum of 3 keywords.
Always respond in English.
Think step by step.
"""

TERM_EXTRACTOR_PROMPT = """
You are given an analysis about coming up with boolean search queries. Your job is to extract the final boolean search queries.
"""

ANALYSIS_WITH_RECORD_PROMPT = """
# Case
{record}

# Task
You are an expert clinician.
You're given a doctor question regarding a case.
Your task is to prepare a preliminary analysis with the below algorithm in order to facilitiate enhanced reasoning capabilities in an LLM.

# Algorithm
    - Initial Understanding: Describe your initial understanding of the given case and doctor question, and any relevant concepts or assumptions you'll be making.
    - Analysis: Break down your understanding into smaller components and analyze each part. Explain how you'll approach each component and what factors you'll consider.
    - Hypothesis Generation: Generate potential hypotheses to address your understanding. Explain the reasoning behind each hypothesis and how you'll evaluate them.
    - Evaluation: Evaluate each hypothesis and explain the pros and cons of each. Describe any trade-offs or limitations you've considered.
    - Conclusion: Based on your analysis and evaluation, arrive at a final commentary context and the content. Explain why you've chosen this solution and how it addresses your understanding.
    - Summary: Provide a clear and concise summary of your preliminary analysis.

Think step by step.
"""

ANALYSIS_PROMPT = """
# Task
You are an expert clinician.
You're given a doctor question regarding a case.
Your task is to prepare a preliminary analysis with the below algorithm in order to facilitiate enhanced reasoning capabilities in an LLM.

# Algorithm
    - Initial Understanding: Describe your initial understanding of the given case and doctor question, and any relevant concepts or assumptions you'll be making.
    - Analysis: Break down your understanding into smaller components and analyze each part. Explain how you'll approach each component and what factors you'll consider.
    - Hypothesis Generation: Generate potential hypotheses to address your understanding. Explain the reasoning behind each hypothesis and how you'll evaluate them.
    - Evaluation: Evaluate each hypothesis and explain the pros and cons of each. Describe any trade-offs or limitations you've considered.
    - Conclusion: Based on your analysis and evaluation, arrive at a final commentary context and the content. Explain why you've chosen this solution and how it addresses your understanding.
    - Summary: Provide a clear and concise summary of your preliminary analysis.

Think step by step.
"""

RERANKER_PROMPT="""
{query}
"""

RERANKER_WITH_RECORD_PROMPT="""
{patient_record}

For the above patient:
{query}
"""