from fastapi import APIRouter, HTTPException
from .models import RevitInput, SearchResult, DetailUpload
from .dataService import known_details
from .matchService import matcher

router = APIRouter()

@router.post("/search", response_model=SearchResult)
def search_endpoint(query: RevitInput):
    best_detail = None
    best_score = -1.0
    best_reason = ""

    # Threshold to say "We found something"
    THRESHOLD = 0.6

    for detail in known_details:
        score, reason = matcher.calculate_match(query, detail)

        if score > best_score:
            best_score = score
            best_detail = detail
            best_reason = reason

    if best_score < THRESHOLD:
        return SearchResult(
            suggested_detail="None",
            confidence=0.0,
            reason=f"No close match. Best was ({best_score}): {best_reason}"
        )

    return SearchResult(
        suggested_detail=best_detail,
        confidence=best_score,
        reason=best_reason
    )

@router.post("/upload")
def upload_endpoint(item: DetailUpload):
    if item.detail_name not in known_details:
        known_details.append(item.detail_name)
        return {"status": "success", "message": f"Added {item.detail_name}"}
    return {"status": "exists", "message": "Detail already exists"}

@router.delete("/delete")
def delete_endpoint(detail_name: str):
    if detail_name in known_details:
        known_details.remove(detail_name)
        return {"status": "success", "message": "Deleted"}
    raise HTTPException(status_code=404, detail="Not found")

@router.get("/list")
def list_endpoint():
    return known_details