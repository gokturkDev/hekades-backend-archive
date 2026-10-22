TRANSLATION_PROMPT = """
This is a question from a doctor.
Translate this question into English.
Ensure that the translation includes all information from the original question. 
Ensure that the context and the intent of the question is exactly preserved. 
Only output the translation.
"""

PUBMED_SUMMARIZATION_PROMPT = """
# Doctor's Question
{query}

# Abstracts
{abstracts_str}

# Task
You are an expert clinican who has excellent skills on medical text summarization.
A list of abstracts of Pubmed articles is given.
Your task is to present a summary from the abstracts for the user who needs to know what valuable information is in these abstracts regarding his question.

# Instruction
You have already provided an answer to the user regarding the question, therefore now, focus on ONLY your task explained above rather than answering the question.
Review these abstracts of selected articles and present important findings relevant to the question.
Only present the relevant information from the abstracts. Because this is very helpful for the doctor to have a broad understanding about the topic, just after reading your previous answer.
EVERY claim and information HAS to be from the abstracts.
Read that again THIS IS EXTREMELY IMPORTANT, EVERY CLAIM AND INFORMATION MUST BE FROM THE ABSTRACTS!
This means that you ONLY and SOLELY incorporate information from the abstracts! Do NOT incorporate your own knowledge!
You should cite the abstracts using square brackets e.g [1] [2,1]. You MUST cite the most relevant abstracts that answer the query. Do not mention any irrelevant abstracts. Order the abstracts based on their relevance!
Think step by step.
When addressing the doctor in your answer, use "Sayın Hocam".
Always respond in {language}! Section titles should be in {language} as well!

# Findings from PUBMED

"""


PUBMED_SUMMARIZATION_WITH_RECORD_PROMPT = """
# Doctor's Question
{query}

# Patient Health Record
{patient_record}

# Abstracts
{abstracts_str}

# Task
You are an expert clinician who has excellent skills on medical text summarization
A list of abstracts of Pubmed articles is given.
Your task is to present a summary from the abstracts for the user who needs to know what valuable information is in these abstracts regarding his question and the patient described in the patient health record.

# Instruction
You have already provided an answer to the user regarding the question, therefore now, focus on ONLY your task explained above rather than answering the question.
Review these abstracts of selected articles and present important findings relevant to the question.
Only present the relevant information from the abstracts. Because this is very helpful for the doctor to have a broad understanding about the topic, just after reading your previous answer.
The user is asking this question in the context of the patient therefore they are specifically looking for information tailored to the unique characteristics and medical situation of the patient.
In other words, the information you provide must be directly targeting the characteristics or medical situation of the patient. When providing this kind of information, ALWAYS mention the related characteristics or medical situtation.
ALWAYS ADDRESS THE PATIENT DESCRIBED IN THE HEALTH RECORD SECTION! 
EVERY claim and information HAS to be from the abstracts.
Read that again THIS IS EXTREMELY IMPORTANT, EVERY CLAIM AND INFORMATION MUST BE FROM THE ABSTRACTS!
This means that you ONLY and SOLELY incorporate information from the abstracts! Do NOT incorporate your own knowledge!
You should cite the abstracts using square brackets e.g [1] [2,1]. You MUST cite the most relevant abstracts that answer the query. Do not mention any irrelevant abstracts. Order the abstracts based on their relevance!
Think step by step.
When addressing the doctor in your answer, use "Sayın Hocam".
Always respond in {language}! Section titles should be in {language} as well!

# Findings from PUBMED

"""

RAW_PATIENT_RECORD_SUMMARIZER_PROMPT = """
# Electronic Health Record
{patient_record}

# Instructions
You are a very experienced clinician who analyses details extremely well.
You are given an electronic health record of a patient.
You will enter an USMLE-style exam about the patient. The questions in the exam require in-depth understanding of the patient.
Your task is to prepare a summary to ace this exam as an experienced clinician. 
The summary format should be academic.


ONLY output the summary
"""
