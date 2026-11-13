import re
import json
from typing import Dict, Any, Optional
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NaturalLanguageQueryParser:
    """
    Advanced natural language query parser that uses LLM to extract structured data
    from natural language insurance claim queries.
    """
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        base_url = os.getenv('OPENAI_BASE_URL')
        self.client = OpenAI(api_key=self.api_key, base_url=base_url) if base_url else OpenAI(api_key=self.api_key)
        self.model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        
        # Common medical procedures and their variations
        self.procedure_patterns = {
            'cataract surgery': ['cataract', 'cataract surgery', 'eye surgery', 'lens replacement'],
            'heart surgery': ['heart surgery', 'cardiac surgery', 'bypass surgery', 'angioplasty'],
            'knee replacement': ['knee replacement', 'knee surgery', 'arthroplasty'],
            'appendectomy': ['appendectomy', 'appendix removal', 'appendicitis surgery'],
            'dental treatment': ['dental', 'dental treatment', 'tooth', 'oral surgery'],
            'cosmetic surgery': ['cosmetic', 'plastic surgery', 'aesthetic surgery'],
            'emergency treatment': ['emergency', 'emergency treatment', 'urgent care']
        }
        
        # Common locations
        self.location_patterns = {
            'Pune': ['pune', 'puna'],
            'Mumbai': ['mumbai', 'bombay'],
            'Delhi': ['delhi', 'new delhi'],
            'Bangalore': ['bangalore', 'bengaluru'],
            'Chennai': ['chennai', 'madras'],
            'Hyderabad': ['hyderabad'],
            'Kolkata': ['kolkata', 'calcutta']
        }
    
    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured format.
        
        Args:
            query: Natural language query string
            
        Returns:
            Dictionary with structured claim data
        """
        try:
            # First try regex-based parsing for common patterns
            structured_data = self._regex_parse(query)
            
            # If regex parsing is incomplete, use LLM
            if not self._is_complete(structured_data):
                structured_data = self._llm_parse(query, structured_data)
            
            # Validate and clean the data
            validated_data = self._validate_and_clean(structured_data)
            
            return validated_data
            
        except Exception as e:
            print(f"❌ Error parsing query: {str(e)}")
            return self._get_default_data()
    
    def _regex_parse(self, query: str) -> Dict[str, Any]:
        """Extract basic information using regex patterns"""
        query_lower = query.lower()
        
        # Extract age
        age_match = re.search(r'(\d+)\s*(?:years?\s*old|y\.?o\.?|age)', query_lower)
        age = int(age_match.group(1)) if age_match else None
        
        # Extract gender
        gender = None
        if re.search(r'\b(male|man|boy|he|his)\b', query_lower):
            gender = 'male'
        elif re.search(r'\b(female|woman|girl|she|her)\b', query_lower):
            gender = 'female'
        
        # Extract procedure
        procedure = None
        for proc, patterns in self.procedure_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                procedure = proc
                break
        
        # Extract location
        location = None
        for loc, patterns in self.location_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                location = loc
                break
        
        # Extract policy duration
        duration_match = re.search(r'(\d+)\s*(?:months?|mo\.?|policy\s*duration)', query_lower)
        policy_duration = int(duration_match.group(1)) if duration_match else None
        
        return {
            'age': age,
            'gender': gender,
            'procedure': procedure,
            'location': location,
            'policy_duration_months': policy_duration
        }
    
    def _llm_parse(self, query: str, partial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to parse complex queries and fill missing information"""
        
        prompt = f"""
        You are an insurance claim parser. Extract structured information from the following natural language query.
        
        QUERY: "{query}"
        
        PARTIAL DATA ALREADY EXTRACTED: {partial_data}
        
        Please extract the following information and return ONLY a JSON object:
        - age: numeric age of the patient
        - gender: "male" or "female"
        - procedure: the medical procedure being claimed (be specific)
        - location: city where treatment will be performed
        - policy_duration_months: how long the policy has been active in months
        
        If information is not available, use null. For procedure, choose the most specific medical term.
        
        Return ONLY valid JSON, no other text:
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                llm_data = json.loads(json_match.group())
                
                # Merge with partial data, preferring LLM results
                merged_data = {**partial_data, **llm_data}
                return merged_data
            else:
                return partial_data
                
        except Exception as e:
            print(f"❌ LLM parsing failed: {str(e)}")
            return partial_data
    
    def _is_complete(self, data: Dict[str, Any]) -> bool:
        """Check if all required fields are present"""
        required_fields = ['age', 'gender', 'procedure', 'location', 'policy_duration_months']
        return all(data.get(field) is not None for field in required_fields)
    
    def _validate_and_clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the parsed data"""
        
        # Ensure age is reasonable
        if data.get('age'):
            data['age'] = max(1, min(120, int(data['age'])))
        
        # Ensure gender is valid
        if data.get('gender'):
            data['gender'] = data['gender'].lower()
            if data['gender'] not in ['male', 'female']:
                data['gender'] = 'male'  # default
        
        # Ensure procedure is valid
        if data.get('procedure'):
            data['procedure'] = data['procedure'].lower()
        
        # Ensure location is valid
        if data.get('location'):
            data['location'] = data['location'].title()
        
        # Ensure policy duration is reasonable
        if data.get('policy_duration_months'):
            data['policy_duration_months'] = max(1, min(120, int(data['policy_duration_months'])))
        
        return data
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Return default data structure"""
        return {
            'age': 40,
            'gender': 'male',
            'procedure': 'general treatment',
            'location': 'Pune',
            'policy_duration_months': 12
        }

# Backward compatibility function
def parse_query(query: str) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    parser = NaturalLanguageQueryParser()
    return parser.parse_query(query)

# Test function
def test_parser():
    """Test the natural language query parser"""
    parser = NaturalLanguageQueryParser()
    
    test_queries = [
        "I'm a 45-year-old male who needs cataract surgery in Pune. My policy is 24 months old.",
        "Female patient, 32 years old, wants dental treatment in Mumbai. Policy duration 6 months.",
        "Emergency heart surgery needed for 55-year-old man in Delhi. Policy active for 18 months.",
        "Knee replacement surgery for 65-year-old male in Chennai. 30-month policy.",
        "Cosmetic surgery request from 28-year-old female in Bangalore. 12-month policy."
    ]
    
    print("🧪 TESTING NATURAL LANGUAGE QUERY PARSER")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query}")
        result = parser.parse_query(query)
        print(f"✅ Parsed Result: {json.dumps(result, indent=2)}")
    
    print("\n" + "=" * 60)
    print("✅ PARSER TESTING COMPLETE")

if __name__ == "__main__":
    test_parser()
