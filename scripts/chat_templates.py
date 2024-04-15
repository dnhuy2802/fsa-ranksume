# import prompt template
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

def input_data_cv_matching(cv_need_matching: str, jd_summary: str):
    input_data_cv_matching = f"""
This is the Resume needed to be matched with the JD:
{cv_need_matching}

This is the repeated JD needed to be matched with Resume:
{jd_summary}

YOUR TASK is CALCULATING the matching score between the candidate's qualifications in the CV and the job requirements in the JD using SCORING GUIDE.

You MUST ONLY respond a string using this format:
{{
    "education": {{
        "major": str,
        "major_relevance_score": int,
        "graduation_status": int[0, 1],
        "explanation": str
    }},
    "language_skills": [
        {{
            "language": str,
            "proficiency": int[1, 2, 3, 4, 5],
            "certification": int[0, 1],
            "required": int[0, 1],
            "explanation": str
        }}
    ],
    "technical_skills": {{
        "technical_score": int,
        "explanation": str
    }},
    "projects": [
        {{
            "project_name": str,
            "relevance_score": int,
            "difficulty_score": int,
            "duration_score": int,
            "explanation": str
        }}
    ]
}}
"""
    return input_data_cv_matching

# create the prompt template cv_matching
chat_template_cv_matching = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content="""
Let's think step by step.
Act as a HR Manager in the Information Technology field, given the CV and JD. Your task is calculating the matching score between the candidate's qualifications and the job requirements.
You must give score to each section and provide a brief explanation of your analysis.
It's ok to say candidate does not match the requirement.
You must only use the information provided in the CV and JD. You will be penalized if you make up information or provide inaccurate information.
All comments must be written using singular pronouns such as "he", "she", "the candidate", or the candidate's name.
SCORING GUIDE:
To determine the matching score, you must analyze the techinical skills, projetcs in the CV and compare them to the requirements outlined in the JD.
For each section provide the matching score as a numeric value between 0-100, along with a brief explanation of your analysis.
    EDUCATION section:
        MUST only use the information in the Resume.
            MAJOR section:
                Extract the candidate's major.
                If no MAJOR is listed, assign a value of null and state in the EXPLANATION section "No education information found on resume".
            RELEVANCE section:
                Evaluated based on the relevance of the major to the job ONLY IF the MAJOR has been identified.
                If no MAJOR is listed, assign a score of 0 and state in the EXPLANATION section "No education information found on resume".
                Score range:
                    16: Unrelated major
                    33: Slightly related major
                    50: Moderately related major
                    66: Strongly related major
            GRADUATION section:
                Evaluated based on the graduation status.
                Score range:
                    0: Not graduated
                    1: Graduated
    LANGUAGE SKILLS section:
        For each language, evaluated based on the level of proficiency, the certification, and the requirement in the JD.
        Rearrange the languages in this section in descending order of REQUIREMENT section score, then LEVEL OF PROFICIENCY section score.
        LEVEL OF PROFICIENCY section:
            Score range:
                1: Elementary proficiency           (CEFR A1 or A2, IELTS from 1.0 to 3.5, TOEFL from 0 to 30, TOEIC from 10 to 250, JLPT N5, Topik 1, HSK 1, ect.)
                2: Lower-intermediate proficiency   (CEFR B1, IELTS from 4.0 to 5.0, TOEFL from above 30 to 60, TOEIC from 255 to 400, JLPT N4, Topik 2, HSK 2, ect.)
                3: Intermediate proficiency         (CEFR B2, IELTS from 5.5 to 6.5, TOEFL from above 60 to 80, TOEIC from 405 to 600, JLPT N3, Topik 3, HSK 3, DSH 1, ect.)
                4: Upper-intermediate proficiency   (CEFR B2, IELTS from 7 to 7.5, TOEFL from above 80 to 100, TOEIC from 605 to 780, JLPT N2, Topik 4, HSK 4, DSH 2, ect.)
                5: Advanced proficiency             (CEFR C1 or C2, IELTS from 8 to 9.0, TOEFL from above 100 to 120, TOEIC from 785 to 990, JLPT N1, Topik 5 - 6, HSK 5 - 6, DSH 3, ect.)
        CERTIFICATION section:
            Score range:
                0: No certification
                1: Certified (CEFR, IELTS, TOEFL, TOEIC, JLPT, Topik, KLAT, KLPT, HSK, DSH, TestDaF, ect.)
        REQUIREMENT section:
            Score range:
                0: Not required in the JD
                1: Required in the JD
    TECHNICAL SKILLS section:
        Evaluated based on the relevance of the techinical skills to the job (programming languages, frameworks, databases, cloud technologies and other techinical skills).
        Score range:
            from 0 to 25: Poor match
            from 25 to 50: Fair match
            from 50 to 80: Good match
            from 80 to 100: Excellent match
    PROJECTS section:
        For each project, evaluated based on the relevance, the level of difficulty and the duration of the projects to the job descriptions.
        For each project, prioritize the relevance, then the level of difficulty, then the duration.
        RELEVANCE section: 
            Evaluated based on the relevance of the projects to the job.
            For this section, you must consider how closely the project's domain, technologies, and core tasks align with the job requirements.
            Projects demonstrating direct application of skills and experience related to the required technical competencies, frameworks, programming languages and other key areas mentioned in the job description must get higher scores.
            Score range:
                from 0 to 25: Poor match
                from 25 to 50: Fair match
                from 50 to 80: Good match
                from 80 to 100: Excellent match
        LEVEL OF DIFFICULTY section:
            Evaluated based on the level of difficulty of the projects.
            For this section, you must consider the complexity of the projects, the technologies used, and the size of the projects.
            Score range:
                from 50 to 60: simple projects
                from 60 to 70: medium projects
                from 70 to 80: intermediate projects
                from 80 to 90: complex projects
                from 90 to 100: highly complex projects
        DURATION section:
            Evaluated based on the duration of the projects.
            For this section, you must consider the duration of the projects.
            Score range:
                from 50 to 60: 0 to 3 months
                from 60 to 75: 3 to 6 months
                from 75 to 90: 6 to 12 months
                from 90 to 100: more than 12 months
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        HumanMessagePromptTemplate.from_template("""{input_data_cv_matching}"""),
    ]
)

# create the prompt template history_jd
chat_template_history_jd = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=("""
This is my Job Description. 
Given a job description, identify and summarize the baseline knowledge requirements for applicants. 
Highlight key areas such as educational background, programming proficiency, technical experience and knowledge, language and communication skills, personal qualities, and any specific experience or priority considerations. Provide a structured summary that can be used to evaluate if applicants meet the minimum requirements to proceed to the interview stage. Remember this for the next step."""
            )
        ),
        HumanMessagePromptTemplate.from_template("This is Job Description: {jd_summary}"),
    ]
)

# create the prompt template summary_jd
chat_template_summary_jd = ChatPromptTemplate.from_messages(
    [
        SystemMessage(
            content=("""To enhance your prompt for summarizing job descriptions (JDs) and extracting minimal requirements, the goal is to guide the response towards generating summaries that closely align with the format CVs typically present technical skills and other qualifications. This can improve the matching process between CVs and JD summaries by focusing on the structured extraction of skills and qualifications that candidates are likely to list on their CVs. Here's a revised version of your prompt:
Given the job description, our objective is to condense and structure it into four distinct sections with a strategic emphasis on the distribution. This approach aims to facilitate a more effective match with candidates' CVs by aligning the summary's format with common CV presentations, especially regarding technical skills. Please summarize as follows:
    Job Responsibilities: Concisely outline the core duties and projects involved in the role. Focus on what the candidate will primarily engage in, using action-oriented language that matches the phrasing candidates often use to describe their experiences in CVs.
    Required Hard Skills: This is the most crucial section. Please list the essential technical skills, educational background, and any specialized knowledge required for the job. Structure this information in bullet points or numbered lists, reflecting how candidates typically itemize their skills in CVs. Also, include relevant software, tools, and technologies, ensuring that this section comprehensively covers the technical qualifications needed.
    Experience Requirements: Detail the desired level of experience and specific types of previous work or projects that are significant for the role. Use clear, quantifiable criteria (e.g., "3+ years of experience in...") to mirror the direct way candidates state their work history and accomplishments in CVs.
    Soft Skills in Context: Enumerate the soft skills crucial for success in the role, such as teamwork, communication, and problem-solving abilities. Phrase these in a way that reflects how they might be demonstrated or applied in a work setting, aligning with how candidates might describe these skills in their CVs.
    Additional Notes: Include any preferred qualifications or aspects not covered in the main sections. This may involve certifications, languages, or personal attributes that would be a plus, offering a holistic view of the ideal candidate.
"""
            )
        ),
        HumanMessagePromptTemplate.from_template("""This is Job Description: 
{jd}. 
Analytic and REMEMBER this for the next step."""),
    ]
)
