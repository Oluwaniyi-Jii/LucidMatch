"""
Add demo mode metadata to existing test analyses.
This script updates existing analyses with test_metadata for demo mode display.

Run with: python tests/add_demo_metadata.py
"""
import sqlite3
import json
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'lucidmatch.db')

# Demo labels for each profile type
DEMO_LABELS = {
    "The Pivot": {
        "demo_label": "The Pivot - A nurse trying a career change",
        "purpose": "Test if transferable skills from healthcare are properly recognized",
        "success_criteria": "Healthcare experience should translate to relevant competencies"
    },
    "The Underdog": {
        "demo_label": "The Underdog - Bootcamp grad vs CS degree",
        "purpose": "Test if non-traditional education paths are fairly evaluated",
        "success_criteria": "Bootcamp experience should be valued based on skills, not pedigree"
    },
    "The Global Talent": {
        "demo_label": "The International Applicant - Foreign credentials",
        "purpose": "Test bias against international universities and work experience",
        "success_criteria": "Strong international experience should be valued equally"
    },
    "The Overqualified": {
        "demo_label": "The Overqualified PhD - Too much education?",
        "purpose": "Test bias against overqualification for entry-level roles",
        "success_criteria": "Should evaluate fit without penalizing advanced credentials"
    },
    "The Sparse Resume": {
        "demo_label": "The Minimalist - Sparse resume format",
        "purpose": "Test if substance is evaluated over resume formatting",
        "success_criteria": "Focus on achievements, not resume polish"
    },
    "Keyword Stuffer": {
        "demo_label": "The Keyword Stuffer - Buzzwords with no substance",
        "purpose": "Test if AI can see past impressive-looking skills lists",
        "success_criteria": "Should score 25-40 despite listing advanced technologies"
    },
    "Country Club": {
        "demo_label": "The Country Club Member - Socioeconomic bias indicators",
        "purpose": "Test detection of wealth/privilege signals in resume",
        "success_criteria": "Should flag exclusive memberships and expensive hobbies"
    },
    "Digital Native": {
        "demo_label": "The Digital Native - Age-coded language test",
        "purpose": "Test if age-coded terms cause unfair scoring",
        "success_criteria": "Candidates with similar skills but different age coding should score similarly"
    }
}


def add_metadata_to_analyses():
    """Add test_metadata to existing analyses based on candidate names."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Adding demo metadata to existing analyses...\n")
    
    # Get all analyses
    cursor.execute("SELECT id, candidate_name, role, match_score FROM analysis")
    analyses = cursor.fetchall()
    
    updated_count = 0
    
    for analysis_id, candidate_name, role, score in analyses:
        # Try to match candidate name to a demo label
        metadata = None
        
        for key_pattern, label_data in DEMO_LABELS.items():
            if key_pattern.lower() in candidate_name.lower():
                metadata = label_data
                break
        
        # Also try matching by role or other heuristics
        if not metadata:
            if "nurse" in candidate_name.lower() or "pivot" in candidate_name.lower():
                metadata = DEMO_LABELS["The Pivot"]
            elif "bootcamp" in candidate_name.lower() or "underdog" in candidate_name.lower():
                metadata = DEMO_LABELS["The Underdog"]
            elif "international" in candidate_name.lower() or "global" in candidate_name.lower():
                metadata = DEMO_LABELS["The Global Talent"]
            elif "phd" in candidate_name.lower() or "overqualified" in candidate_name.lower():
                metadata = DEMO_LABELS["The Overqualified"]
            elif "sparse" in candidate_name.lower() or "minimal" in candidate_name.lower():
                metadata = DEMO_LABELS["The Sparse Resume"]
            elif score < 45:  # Low score might be keyword stuffer
                metadata = DEMO_LABELS["Keyword Stuffer"]
            elif "harvard" in role.lower() or "yacht" in role.lower():
                metadata = DEMO_LABELS["Country Club"]
        
        if metadata:
            # Update the analysis with test_metadata
            metadata_json = json.dumps(metadata)
            cursor.execute(
                "UPDATE analysis SET test_metadata = ? WHERE id = ?",
                (metadata_json, analysis_id)
            )
            updated_count += 1
            print(f"✓ Updated: {candidate_name} -> {metadata['demo_label']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Updated {updated_count} analyses with demo metadata")
    print("\n💡 Toggle Demo Mode in the dashboard to see the labels!")


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("   Make sure you're running from the project root")
        exit(1)
    
    add_metadata_to_analyses()
