import json
import pandas as pd

def clean_data():
    # Load raw data
    with open('raw_data.json', 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    df = pd.DataFrame(raw_data)
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['company_name'], keep='first')
    
    # Handle missing values
    df['company_name'] = df['company_name'].fillna('Unknown')
    df['location'] = df['location'].fillna('Not Specified')
    df['category'] = df['category'].fillna('Electronics & Components')
    df['rating'] = df['rating'].fillna('No Rating')
    
    # Standardize location (remove extra spaces, lowercase state)
    df['location'] = df['location'].str.strip().str.title()
    
    # Standardize company name
    df['company_name'] = df['company_name'].str.strip()
    
    # Save cleaned data
    df.to_json('cleaned_data.json', orient='records', indent=2)
    print(f"Cleaned {len(df)} records. Saved to cleaned_data.json")
    
    return df

if __name__ == "__main__":
    clean_data()