from scenarios.models import ScenarioDocument
from scenarios.services.guards import detect_external_instruction, event


def retrieve_documents(scenario, message, submitted_documents, defenses):
    retrieved = []
    risk_events = []

    seed_docs = list(ScenarioDocument.objects.filter(scenario=scenario)[:5])
    for doc in seed_docs:
        content = doc.content
        doc_events = detect_external_instruction(content)
        risk_events.extend(doc_events)
        if defenses.get("instructionDataSeparation") and doc_events:
            content = "[已清理的非可信文档指令] " + content.replace("RAG_INJECTION_TRAINING_FLAG", "[TRAINING_FLAG_REDACTED]")
            risk_events.append(event("rag_document_sanitized", "medium", "rag_doc", "已隔离污染文档中的伪指令。", "sanitized", doc.title))
        retrieved.append({
            "title": doc.title,
            "content": content[:700],
            "isPoisoned": doc.is_poisoned,
            "metadata": doc.metadata,
        })

    for index, item in enumerate(submitted_documents or []):
        title = item.get("title") or f"学员文档 {index + 1}"
        content = item.get("content", "")[:2000]
        doc_events = detect_external_instruction(content)
        risk_events.extend(doc_events)
        if defenses.get("instructionDataSeparation") and doc_events:
            content = content.replace("RAG_INJECTION_TRAINING_FLAG", "[TRAINING_FLAG_REDACTED]")
        retrieved.append({"title": title, "content": content[:700], "isPoisoned": bool(doc_events), "metadata": {"source": "submitted"}})

    return retrieved, risk_events
