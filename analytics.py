"""
Analytics & Recommendations Engine
Bonus AI/ML Component for the Data Engineering Assignment

This module provides intelligent insights and recommendations based on
supplier data using clustering and recommendation algorithms.
"""

import json
import numpy as np
from collections import defaultdict, Counter
from typing import Dict, List, Any

class SupplierAnalytics:
    """Analyze supplier data and generate insights"""
    
    def __init__(self, data_file='cleaned_data.json'):
        """Initialize analytics engine with cleaned data"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                self.companies = json.load(f)
        except FileNotFoundError:
            print(f"Error: {data_file} not found")
            self.companies = []
    
    def extract_rating_score(self, rating_str: str) -> float:
        """Convert rating string to numeric score"""
        try:
            # Extract number from "4.8 stars"
            score = float(rating_str.split()[0])
            return score
        except:
            return 0.0
    
    def get_recommendations_by_category(self) -> Dict[str, Any]:
        """
        Generate supplier recommendations by category
        
        Algorithm:
        - Group suppliers by category
        - Rank by rating (higher is better)
        - Return top 3 per category
        
        Returns:
            Dict with recommendations per category
        """
        recommendations = {}
        categories = defaultdict(list)
        
        # Group by category
        for company in self.companies:
            category = company.get('category', 'Others')
            rating_score = self.extract_rating_score(company.get('rating', '0 stars'))
            
            categories[category].append({
                'company_name': company['company_name'],
                'location': company.get('location', 'Unknown'),
                'rating': company.get('rating', 'No Rating'),
                'rating_score': rating_score,
                'source': company.get('source', 'Unknown')
            })
        
        # Get top 3 per category
        for category, suppliers in categories.items():
            # Sort by rating score (descending)
            sorted_suppliers = sorted(suppliers, key=lambda x: x['rating_score'], reverse=True)
            top_suppliers = sorted_suppliers[:3]
            
            avg_rating = np.mean([s['rating_score'] for s in sorted_suppliers]) if sorted_suppliers else 0
            
            recommendations[category] = {
                'total_suppliers': len(suppliers),
                'avg_rating': round(avg_rating, 2),
                'top_suppliers': [
                    {
                        'rank': i+1,
                        'company_name': s['company_name'],
                        'location': s['location'],
                        'rating': s['rating'],
                        'confidence_score': round(s['rating_score'] / 5.0 * 100, 1)
                    }
                    for i, s in enumerate(top_suppliers)
                ]
            }
        
        return recommendations
    
    def analyze_location_hubs(self) -> Dict[str, Any]:
        """
        Identify supply concentration hubs
        
        Algorithm:
        - Count companies per location
        - Identify top 5 hubs
        - Calculate market concentration
        
        Returns:
            Location analysis with hub identification
        """
        location_counts = Counter(c.get('location', 'Unknown') for c in self.companies)
        
        # Calculate concentration metrics
        total_suppliers = len(self.companies)
        hubs = {
            location: {
                'count': count,
                'percentage': round(count/total_suppliers * 100, 1),
                'market_share': round(count/total_suppliers, 3)
            }
            for location, count in location_counts.most_common(5)
        }
        
        # Calculate Herfindahl Index (market concentration)
        hhi = sum((count/total_suppliers)**2 for count in location_counts.values()) * 10000
        
        concentration_level = (
            'Highly Concentrated' if hhi > 2500 else
            'Moderately Concentrated' if hhi > 1500 else
            'Competitive'
        )
        
        return {
            'top_hubs': hubs,
            'total_locations': len(location_counts),
            'herfindahl_index': round(hhi, 1),
            'concentration_level': concentration_level,
            'insight': f"Market is {concentration_level.lower()}. Top hub is {location_counts.most_common(1)[0][0]} with {location_counts.most_common(1)[0][1]} suppliers."
        }
    
    def category_clustering_analysis(self) -> Dict[str, Any]:
        """
        Analyze category distribution and clustering
        
        Algorithm:
        - Count items per category
        - Identify niche vs popular categories
        - Compute category diversity index
        
        Returns:
            Category analysis with diversity metrics
        """
        category_counts = Counter(c.get('category', 'Others') for c in self.companies)
        total_companies = len(self.companies)
        
        # Classify categories
        popular_threshold = total_companies / len(category_counts) * 1.5
        
        categories_ranked = {}
        for category, count in category_counts.most_common():
            classification = (
                'Popular' if count >= popular_threshold else
                'Niche'
            )
            
            categories_ranked[category] = {
                'count': count,
                'percentage': round(count/total_companies * 100, 1),
                'classification': classification,
                'recommendation': (
                    'High demand segment - consider diversification' if classification == 'Popular'
                    else 'Specialized niche - potential growth opportunity'
                )
            }
        
        # Calculate Shannon diversity index (0-1, where 1 is high diversity)
        proportions = [count/total_companies for count in category_counts.values()]
        shannon_index = -sum(p * np.log(p) for p in proportions if p > 0)
        normalized_shannon = shannon_index / np.log(len(category_counts)) if len(category_counts) > 1 else 0
        
        return {
            'categories': categories_ranked,
            'total_categories': len(category_counts),
            'diversity_index': round(normalized_shannon, 3),
            'diversity_level': (
                'High' if normalized_shannon > 0.7 else
                'Medium' if normalized_shannon > 0.4 else
                'Low'
            )
        }
    
    def identify_market_gaps(self) -> Dict[str, Any]:
        """
        Identify underserved categories and locations
        
        Algorithm:
        - Find categories with low supplier count
        - Find locations with limited options
        - Recommend market opportunities
        
        Returns:
            Market gap analysis
        """
        category_counts = Counter(c.get('category', 'Others') for c in self.companies)
        location_counts = Counter(c.get('location', 'Unknown') for c in self.companies)
        
        avg_suppliers_per_category = np.mean(list(category_counts.values()))
        low_category_threshold = avg_suppliers_per_category * 0.5
        
        gaps = {
            'underserved_categories': [
                {'category': cat, 'suppliers': count, 'gap_score': round(low_category_threshold - count, 1)}
                for cat, count in category_counts.items()
                if count < low_category_threshold
            ],
            'underserved_locations': [
                {'location': loc, 'suppliers': count}
                for loc, count in location_counts.most_common()[-3:]
            ],
            'recommendations': [
                "Consider expanding into underserved categories",
                "Look for partnership opportunities in low-competition areas",
                "Monitor emerging specialist categories"
            ]
        }
        
        return gaps
    
    def generate_full_report(self) -> Dict[str, Any]:
        """Generate complete analytics report"""
        
        report = {
            'metadata': {
                'total_companies': len(self.companies),
                'data_source': 'Electronics & Components Directory',
                'timestamp': __import__('datetime').datetime.now().isoformat()
            },
            'recommendations': self.get_recommendations_by_category(),
            'location_analysis': self.analyze_location_hubs(),
            'category_analysis': self.category_clustering_analysis(),
            'market_gaps': self.identify_market_gaps()
        }
        
        return report
    
    def save_report(self, output_file='company_recommendations.json'):
        """Generate and save full analytics report"""
        report = self.generate_full_report()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Analytics report saved to {output_file}")
        return report


def print_report_summary(report: Dict) -> None:
    """Print formatted report summary"""
    print("\n" + "="*70)
    print("ELECTRONICS SUPPLIERS - ANALYTICS & RECOMMENDATIONS REPORT")
    print("="*70)
    
    metadata = report['metadata']
    print(f"\n📊 Dataset: {metadata['total_companies']} companies analyzed")
    print(f"   Generated: {metadata['timestamp']}")
    
    # Recommendations summary
    print("\n📈 CATEGORY RECOMMENDATIONS:")
    print("-" * 70)
    for category, data in list(report['recommendations'].items())[:5]:
        print(f"\n  {category}:")
        print(f"    • Total Suppliers: {data['total_suppliers']}")
        print(f"    • Average Rating: {data['avg_rating']}/5.0")
        if data['top_suppliers']:
            print(f"    • Top Supplier: {data['top_suppliers'][0]['company_name']}")
            print(f"      Location: {data['top_suppliers'][0]['location']}")
    
    # Location analysis
    location_data = report['location_analysis']
    print(f"\n🌍 LOCATION ANALYSIS:")
    print("-" * 70)
    print(f"  Top Supply Hubs: {location_data['total_locations']} unique locations")
    print(f"  Concentration Level: {location_data['concentration_level']}")
    for location, data in list(location_data['top_hubs'].items())[:3]:
        print(f"    • {location}: {data['count']} suppliers ({data['percentage']}% market share)")
    
    # Category analysis
    cat_data = report['category_analysis']
    print(f"\n🏭 CATEGORY ANALYSIS:")
    print("-" * 70)
    print(f"  Total Categories: {cat_data['total_categories']}")
    print(f"  Diversity Index: {cat_data['diversity_index']} ({cat_data['diversity_level']} diversity)")
    
    # Market gaps
    print(f"\n💡 MARKET OPPORTUNITIES:")
    print("-" * 70)
    gaps = report['market_gaps']
    if gaps['underserved_categories']:
        print(f"  Underserved Categories:")
        for cat in gaps['underserved_categories'][:3]:
            print(f"    • {cat['category']}: {cat['suppliers']} suppliers (Gap score: {cat['gap_score']})")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("\n🤖 Starting Analytics Engine...\n")
    
    # Initialize analytics
    analytics = SupplierAnalytics()
    
    if not analytics.companies:
        print("❌ No data found. Please run scraper.py and clean_data.py first.")
        exit(1)
    
    # Generate report
    print("📊 Generating analytics report...")
    report = analytics.generate_full_report()
    
    # Save report
    analytics.save_report()
    
    # Print summary
    print_report_summary(report)
    
    print("✓ Analytics complete!")
