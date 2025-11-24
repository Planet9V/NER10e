import prodigy
from prodigy.components.loaders import JSONL
from neo4j import GraphDatabase
import spacy

# Configuration
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_AUTH = ("neo4j", "neo4j@openspg")

def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)

def check_neo4j(driver, text):
    """Checks if the entity text exists in Neo4j and returns its labels."""
    query = "MATCH (n) WHERE n.name = $text RETURN labels(n) as labels LIMIT 1"
    try:
        with driver.session() as session:
            result = session.run(query, text=text).single()
            if result:
                return result["labels"]
    except Exception:
        pass
    return None

def get_cve_context(driver, cve_id):
    """Fetches EPSS/CISA info for a CVE from Neo4j (assuming it's loaded)."""
    query = """
    MATCH (c:CVE {name: $cve_id})
    RETURN c.epss_score as epss, c.cisa_kev as kev
    """
    try:
        with driver.session() as session:
            result = session.run(query, cve_id=cve_id).single()
            if result:
                return result
    except Exception:
        pass
    return None

@prodigy.recipe(
    "ner10.enrich",
    dataset=("The dataset to save to", "positional", None, str),
    source=("The source data as a JSONL file", "positional", None, str),
    lang=("The model language", "option", "l", str),
)
def ner10_enrich(dataset, source, lang="en"):
    """
    Custom NER recipe that enriches the annotation interface with Neo4j context.
    """
    # Load the spaCy model (or blank if starting fresh)
    try:
        nlp = spacy.load(lang)
    except OSError:
        nlp = spacy.blank(lang)

    driver = get_neo4j_driver()
    stream = JSONL(source)

    def add_context(stream):
        for task in stream:
            text = task.get("text", "")
            
            # Run the model to get suggested entities
            doc = nlp(text)
            spans = []
            html_context = "<div style='padding: 10px; border: 1px solid #ddd; background: #f9f9f9;'>"
            html_context += "<strong>Digital Twin Context:</strong><br/>"
            
            has_context = False
            
            for ent in doc.ents:
                # Add to spans for pre-annotation
                spans.append({
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "label": ent.label_
                })
                
                # Check Neo4j
                labels = check_neo4j(driver, ent.text)
                if labels:
                    html_context += f"✅ <b>{ent.text}</b>: {', '.join(labels)}<br/>"
                    has_context = True
                
                # Special handling for CVEs
                if "CVE-" in ent.text:
                    cve_data = get_cve_context(driver, ent.text)
                    if cve_data:
                        html_context += f"⚠️ <b>{ent.text}</b>: EPSS={cve_data['epss']} | KEV={cve_data['kev']}<br/>"
                        has_context = True
            
            html_context += "</div>"
            
            if has_context:
                task["html"] = html_context
            
            task["spans"] = spans
            yield task

    return {
        "view_id": "ner_manual", # Use manual interface but with pre-populated spans
        "dataset": dataset,
        "stream": add_context(stream),
        "config": {
            "lang": lang,
            "labels": ["EQUIPMENT", "SECTOR", "THREAT_ACTOR", "VULNERABILITY", 
                       "MALWARE", "ATTACK_PATTERN", "COGNITIVE_BIAS", 
                       "PERSONALITY_TRAIT", "EMOTION", "LOCATION", 
                       "ORGANIZATION", "SOFTWARE"] 
        }
    }
