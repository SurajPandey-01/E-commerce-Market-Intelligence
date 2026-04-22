from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import json
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data from JSON file (local storage)
DATA_FILE = 'cleaned_data.json'

def load_companies_from_file():
    """Load companies from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading file: {e}")
    return []

def save_companies_to_file(data):
    """Save companies to JSON file"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False

@app.get("/")
def read_root():
    return {"message": "Electronics & Components API is running", "backend": "JSON File Storage"}

@app.post("/load-data")
def load_data_to_db():
    """Load cleaned data into memory"""
    try:
        data = load_companies_from_file()
        return {"status": "success", "records_loaded": len(data), "message": f"Loaded {len(data)} companies from cleaned_data.json"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/companies")
def get_companies(
    location: str = Query(None),
    category: str = Query(None),
    skip: int = Query(0),
    limit: int = Query(10)
):
    """Get companies with optional filters"""
    try:
        companies = load_companies_from_file()
        
        # Apply filters
        filtered_companies = companies
        if location:
            filtered_companies = [c for c in filtered_companies if location.lower() in c.get('location', '').lower()]
        if category:
            filtered_companies = [c for c in filtered_companies if category.lower() in c.get('category', '').lower()]
        
        # Apply pagination
        total = len(filtered_companies)
        paginated = filtered_companies[skip:skip + limit]
        
        return {"total": total, "data": paginated}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/companies/search")
def search_companies(query: str = Query(...)):
    """Search companies by name"""
    try:
        companies = load_companies_from_file()
        query_lower = query.lower()
        
        results = [c for c in companies if query_lower in c.get('company_name', '').lower()][:20]
        
        return {"data": results}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/stats")
def get_stats():
    """Get basic statistics"""
    try:
        companies = load_companies_from_file()
        
        # Get unique locations
        locations = list(set(c.get('location', 'Not Specified') for c in companies))
        
        return {
            "total_companies": len(companies),
            "unique_locations": len(locations),
            "locations": sorted(locations)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
@app.get("/recommend")
def recommend_suppliers(category: str):
    try:
        companies = load_companies_from_file()

        # Filter by category
        filtered = [c for c in companies if category.lower() in c.get("category", "").lower()]

        # Convert rating to numeric
        def get_rating(c):
            try:
                return float(c.get("rating", "0").split()[0])
            except:
                return 0

        # Sort by rating
        top_suppliers = sorted(filtered, key=get_rating, reverse=True)[:5]

        return {"recommendations": top_suppliers}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    print("="*60)
    print("Starting Electronics & Components API")
    print("Backend: JSON File Storage (Local)")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8000) 