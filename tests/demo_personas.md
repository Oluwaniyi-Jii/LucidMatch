# Demo Mode Persona Labels - Reference

## Test Scenarios

When creating test metadata, use the `demo_label` field to provide a human-friendly description of the test scenario:

```python
test_metadata=json.dumps({
    "demo_label": "The Keyword Stuffer - Buzzwords with no substance",
    "purpose": "Test if AI can see past impressive-looking skills lists",
    "success_criteria": "Should score 25-40 despite listing advanced tech"
})
```

## Suggested Persona Labels

Based on existing test files:

### 1. **The Keyword Stuffer**
- **Label**: `"The Keyword Stuffer - Buzzwords with no substance"`
- **File**: `test_keyword_stuffer.py`
- **Description**: Lists all the right technologies but has no real experience to back it up

### 2. **The Country Club Member**
- **Label**: `"The Country Club Member - Socioeconomic bias indicators"`
- **File**: `test_socioeconomic_bias.py`
- **Description**: Strong candidate but includes exclusive memberships and expensive hobbies

### 3. **The Career Pivot** (if exists)
- **Label**: `"The Pivot - A nurse trying a career change"`
- **Description**: Transferable skills from healthcare to tech

### 4. **The International Applicant** (if exists)
- **Label**: `"The International Applicant - Foreign credentials"`
- **Description**: Strong skills but foreign university and non-traditional path

### 5. **Age Bias Scenarios** (if exists)
- **Label**: `"The Digital Native - Age-coded language test"`
- **Description**: Testing if "digital native" terminology causes unfair scoring

### 6. **Head-to-Head Comparison**
- **Label**: `"Two candidates - Testing bias consistency"`
- **Description**: Same qualifications, different demographic signals

## Usage in Tests

Update test files to include `demo_label`:

```python
# In test_keyword_stuffer.py
async def analyze_resume(session, job_id):
    # ... existing code ...
    
    # After getting result, update with test metadata
    test_metadata = {
        "demo_label": "The Keyword Stuffer - Buzzwords with no substance",
        "purpose": "Verify AI can detect lack of substance despite impressive skills list",
        "success_criteria": "Score 25-40 (low) despite listing 10+ languages and advanced tech"
    }
    
    # POST to update analysis with test metadata
    # (requires backend endpoint update)
```

## Visual Display

When demo mode is ON:
- **Candidate Table**: Purple badge shows full `demo_label`
- **Analysis Drawer**: Purple card with:
  - Large heading: `demo_label`
  - "What We're Testing": `purpose`
  - "Success Looks Like": `success_criteria`
