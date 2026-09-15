import re
from collections import defaultdict
from .medical_data_loader import load_master_records, normalize
from .department_mapper import departments_for

EMERGENCY_TERMS={"chest pain","severe breathing difficulty","difficulty breathing","unconscious","loss of consciousness","stroke","severe bleeding","seizure","suicidal"}

def _tokens(text):
    return set(re.findall(r"[a-z0-9]+", normalize(text)))

def retrieve(query, limit=5):
    records=load_master_records()
    q=normalize(query)
    qt=_tokens(q)
    results=[]
    for record in records:
        score=0.0; matched=[]
        name=normalize(record.get("name",""))
        aliases=[normalize(a) for a in record.get("aliases",[])]
        symptoms=[normalize(s) for s in record.get("symptoms",[])]

        if name and name in q:
            score+=12; matched.append(record.get("name"))
        for alias in aliases:
            if alias and alias in q:
                score+=9; matched.append(alias)
        for symptom in symptoms:
            st=_tokens(symptom)
            if not st: continue
            if symptom in q:
                score+=6+min(len(st),3); matched.append(symptom)
            else:
                overlap=len(qt & st)
                # Avoid scoring generic one-word overlaps such as "pain" equally for every disease.
                if overlap:
                    coverage=overlap/len(st)
                    if len(st)==1:
                        score+=1.5
                    elif coverage>=0.5:
                        score+=overlap*2.0; matched.append(symptom)
                    elif overlap>=2:
                        score+=overlap*1.0; matched.append(symptom)

        if score>0:
            results.append({
                "id":record["id"],"name":record["name"],
                "description":record.get("description"),
                "body_system":record.get("body_system"),
                "matched_features":list(dict.fromkeys(matched))[:8],
                "score":round(score,2),
                "recommended_departments":departments_for(record.get("body_system"))
            })
    results.sort(key=lambda x:(x["score"],len(x["matched_features"])),reverse=True)
    return results[:limit]

def triage(query):
    text=normalize(query); matched=[t for t in EMERGENCY_TERMS if t in text]
    return ({"urgency":"high","message":"The information provided may require urgent clinical assessment.","matched_alert_terms":matched}
            if matched else
            {"urgency":"routine","message":"This result is informational and does not establish a diagnosis.","matched_alert_terms":[]})

def analyze(query,limit=5):
    matches=retrieve(query,limit)
    # Rank departments by evidence score, instead of preserving whichever disease happened to appear first.
    department_scores=defaultdict(float)
    for match in matches:
        for dep in match["recommended_departments"]:
            department_scores[dep]+=match["score"]
    ranked=[d for d,_ in sorted(department_scores.items(),key=lambda x:x[1],reverse=True)]
    if not ranked: ranked=["General Medicine"]
    return {
        "query":query,"knowledge_base_records":len(load_master_records()),
        "triage":triage(query),"possible_conditions":matches,
        "recommended_departments":ranked[:3],
        "department_scores":dict(sorted(department_scores.items(),key=lambda x:x[1],reverse=True)[:5]),
        "clinical_note":"Possible matches are generated from the Neo Nano knowledge base and require qualified clinical assessment."
    }
