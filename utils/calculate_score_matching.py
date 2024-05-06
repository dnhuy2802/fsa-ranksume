def calculate_education_score(education):
    if education['major'] == None:
        return 12
    elif int(education['graduation_status']) == 0:
        return int(education['major_relevance_score'])
    else:
        return int(education['major_relevance_score']) * 1.5


def calculate_language_score(languages):
    n = len(languages)
    if n == 0:
        return 12
    language_score_list = [(int(languages[i]['proficiency'])*12 + int(languages[i]['certification'])*5 + int(languages[i]['required'])*5) for i in range(n)]
    language_score = language_score_list[0] + sum(language_score_list[1:])*0.2
    return language_score if language_score <= 100 else 100


def calculate_quantity_score(projects):
    n = len(projects)
    if n in [1, 2]:
        return 0.45
    quantity_score = 0.45 + 0.05 * n
    return quantity_score if quantity_score <= 0.9 else 0.9


def calculate_experience_score(projects, config_score: dict):
    # Ingredient of experience score
    relevance_score_w = config_score["experience_score_config"]["relevance_score_w"]
    difficulty_score_w = config_score["experience_score_config"]["difficulty_score_w"]
    duration_score_w = config_score["experience_score_config"]["duration_score_w"]

    # Quantity score
    S_quantity = calculate_quantity_score(projects)

    # Quality score
    scores = []
    S_quality = 0
    for project in projects:
        s1 = float(project['relevance_score'])
        s2 = float(project['difficulty_score'])
        s3 = float(project['duration_score'])
        scores.append(relevance_score_w * s1 + difficulty_score_w * s2 + duration_score_w * s3)
    total_score = sum(scores)
    for score in scores:
        S_quality += score * (score / total_score)
    
    # Experience score
    experience_score = S_quantity * S_quality

    return experience_score


def calculate_matching_score(matched_result: dict, config_score: dict):
    # Education score weight
    W_education_score = config_score["education_score_config"]["W_education_score"]
    # Language score weight
    W_language_score = config_score["language_score_config"]["W_language_score"]
    # Technical score weight
    W_technical_score = config_score["technical_score_config"]["W_technical_score"]
    # Expreience score weight
    W_experience_score = config_score["experience_score_config"]["W_experience_score"]

    # Education score
    education = matched_result['education']
    education_score = calculate_education_score(education)

    # Language score
    languages = matched_result['language_skills']
    language_score = calculate_language_score(languages)

    # Technical score
    technical_score = float(matched_result["technical_skills"]["technical_score"])
    
    # Experience score
    projects = matched_result['projects']
    experience_score = calculate_experience_score(projects, config_score)

    # Overall score
    overall_score = W_education_score * education_score + W_language_score * language_score + W_technical_score * technical_score + W_experience_score * experience_score

    return {"education_score": education_score, "language_score": language_score, "technical_score": technical_score, "expreience_score": round(experience_score, 2), "overall_score": round(overall_score, 2)}