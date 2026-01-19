#####
How to Run
This application requires two terminal windows running simultaneously (one for the backend API, one for the frontend UI).

Prerequisites
Python 3.9 or higher
pip
1. Installation
Navigate to the project folder and install dependencies:

///bash
pip install -r requirements.txt
///
2. Start the Backend
Open your first terminal and run:

///bash
python -m backend.main
///
You should see: Uvicorn running on http://0.0.0.0:8000

3. Start the Frontend
Open a second terminal and run:

///bash
streamlit run frontend/app.py
///
Your browser will automatically open to http://localhost:8501.

####
Rating Algo
Unlike simple string matching, this algorithm calculates a Confidence Score (0.0 to 1.0) based on context and specific functionality.

1. Zero-Based Scoring
We do not start with a match. Every comparison starts at a Confidence Score of 0.0. The score is built up incrementally as evidence (keywords) matches.

2. Normalization
Before matching, inputs are normalized to handle Revit-specific quirks:

Synonyms: Exterior → External, Conc → Concrete, Footing → Foundation.
Splitting: Core-Shaft is split into Core and Shaft.
3. Building the Score (The Weights)
If keywords match, points are added to the score:

Host Match (+35%): Does the detail mention the host element (e.g., "Wall")?
Adjacent Match (+35%): Does the detail mention the adjacent element (e.g., "Slab")?
Exposure Match (+10%): Does the detail match the condition (e.g., "Internal")?
Neutral Functionality (+20%): Awarded if no specific functional mismatches occur.
4. Handling Penalties (Functional Logic)
The algorithm explicitly handles "Functional Keywords" (e.g., Waterproofing, Firestop, Insulation).

Scenario A: Perfect Match (Bonus)
Input: "External Wall Waterproofing"
Detail: "External Wall Waterproofing Detail"
Result: Full score.
Scenario B: The "Missing Requirement" Penalty (Major Cut)
Input: "External Wall Waterproofing" (User explicitly wants waterproofing)
Detail: "External Wall Detail" (Generic)
Result: -0.25 Penalty (-0.2 - 0.05). The detail is structurally correct but fails the specific functional requirement.
Scenario C: The "Unrequested Specificity" Penalty (Minor Cut)
Input: "External Wall" (Generic request)
Detail: "External Wall Waterproofing"
Result: No score added ( -0.2 penalty)


####
API Endpoints
The Backend exposes a REST API that can be used by other services or Revit plugins directly.

Method	Endpoint	Description
POST	/search	Inputs Host/Adjacent/Exposure, returns Suggested Detail + Score.
POST	/upload	Adds a new Detail string to the in-memory database.
DELETE	/delete	Removes a Detail string from the database.
GET	/list	Returns all known details.


