import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import faiss

# Global vectorizer that will be fitted once
vectorizer = None
is_fitted = False

def embed_chunks(chunks, fit_vectorizer=False):
    """
    Create embeddings using TF-IDF vectorization.
    This avoids the TensorFlow/Keras compatibility issues.
    
    Args:
        chunks: List of text chunks
        fit_vectorizer: If True, fit the vectorizer on these chunks
    """
    global vectorizer, is_fitted
    
    if not chunks:
        return np.array([])
    
    if fit_vectorizer or vectorizer is None:
        # Initialize and fit the vectorizer
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=1.0
        )
        embeddings = vectorizer.fit_transform(chunks)
        is_fitted = True
        print(f"🔧 Fitted vectorizer with {len(vectorizer.get_feature_names_out())} features")
    else:
        # Use the fitted vectorizer to transform
        if not is_fitted:
            raise ValueError("Vectorizer must be fitted before transforming")
        embeddings = vectorizer.transform(chunks)
    
    # Convert to dense array
    return embeddings.toarray()

def embed_query(query_text):
    """
    Embed a single query text using the fitted vectorizer.
    This is the correct way to embed queries for search.
    """
    global vectorizer, is_fitted
    
    if not is_fitted or vectorizer is None:
        raise ValueError("Vectorizer must be fitted before embedding queries")
    
    # Transform the query using the fitted vectorizer
    query_embedding = vectorizer.transform([query_text])
    return query_embedding.toarray()[0]

def embed_claim_query(claim_data):
    """
    Create a comprehensive query embedding from claim data.
    This combines all relevant information for better retrieval.
    """
    # Build a comprehensive query string
    query_parts = []
    
    if claim_data.get('procedure'):
        query_parts.append(claim_data['procedure'])
    
    # Add medical context based on procedure
    procedure = claim_data.get('procedure', '').lower()
    if 'cataract' in procedure:
        query_parts.extend(['eye surgery', 'lens', 'ophthalmology', 'waiting period'])
    elif 'heart' in procedure:
        query_parts.extend(['cardiac', 'cardiovascular', 'heart surgery', 'waiting period'])
    elif 'knee' in procedure:
        query_parts.extend(['orthopedic', 'joint replacement', 'arthroplasty'])
    elif 'dental' in procedure:
        query_parts.extend(['dental', 'oral', 'exclusion'])
    elif 'cosmetic' in procedure:
        query_parts.extend(['cosmetic', 'plastic surgery', 'exclusion'])
    elif 'emergency' in procedure:
        query_parts.extend(['emergency', 'urgent', 'immediate'])
    
    # Add policy duration context
    duration = claim_data.get('policy_duration_months', 0)
    if duration < 24:
        query_parts.append('waiting period')
    if duration < 12:
        query_parts.append('new policy')
    
    # Add location context
    if claim_data.get('location'):
        query_parts.append(claim_data['location'])
    
    # Combine all parts
    comprehensive_query = ' '.join(query_parts)
    print(f"🔍 Comprehensive query: {comprehensive_query}")
    
    return embed_query(comprehensive_query)

def build_faiss_index(embeddings):
    """
    Build FAISS index for similarity search.
    """
    if len(embeddings) == 0:
        return None
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    return index
