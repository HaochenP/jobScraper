import spacy
from spacy.matcher import PhraseMatcher
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor




#
#print(annotations)


def skill_extractor():

    nlp = spacy.load("en_core_web_lg")
    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)
    return skill_extractor

def extract_words(skill_extractor, text):
    annotations = skill_extractor.annotate(text)
    skill_list = []
    for match in annotations['results']['full_matches']:
        skill_list.append(match['doc_node_value'])

    for match in annotations['results']['ngram_scored']:
        skill_list.append(match['doc_node_value'])
    return list(set(skill_list))

if __name__ == '__main__':
    from spacy.matcher import PhraseMatcher
    from skillNer.general_params import SKILL_DB
    from skillNer.skill_extractor_class import SkillExtractor
    job_description = """
    Keywords: C#, .Net, Entity Framework, HTML, CSS, Javascript, React, Vue, Angular, JQuery, Bootstrap, SQL, MSSQL, MySQL, Software Developer, .Net Developer, C# Developer, Web Developer, ASP.Net, MVC, Exeter, Barnstaple, Tiverton, Taunton, Bristol, Bideford, Cullompton, C#, .Net, Entity Framework, HTML, CSS, Javascript, React, Vue, Angular, JQuery, Bootstrap, SQL, MSSQL, MySQL, Software Developer, .Net Developer, C# Developer, Web Developer, ASP.Net, MVC, Exeter, Barnstaple, Tiverton, Taunton, Bristol, Bideford, Cullompton - Due to promotion, we are looking for a C# .Net Software Developer to join our team of 5 creating bespoke, internal systems for our brands and businesses. If you are an experienced C# Software Developer looking to grow your career within an awesome team, we'd love to hear from you!
    """
    skill_extractor = skill_extractor()
    skill_list = extract_words(skill_extractor)
    print(skill_list)