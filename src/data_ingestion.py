import os
import numpy as np
import pickle
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_documents(directory):
    """
    Load documents from the specified directory.
    
    Parameters:
    - directory: Path to the directory containing text files.
    
    Returns:
    - documents: A list of document contents.
    - filenames: A list of corresponding filenames.
    """
    documents = []
    filenames = []
    
    try:
        logger.info(f"Loading documents from directory: {directory}")
        
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        for filename in os.listdir(directory):
            if filename.endswith(".txt"):
                filepath = os.path.join(directory, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        documents.append(content)
                        filenames.append(filename)
                    else:
                        logger.warning(f"Empty document skipped: {filename}")
        
        if not documents:
            raise ValueError("No documents were loaded. Check the directory for valid text files.")
        
        logger.info(f"Loaded {len(documents)} documents successfully.")
    except Exception as e:
        logger.error(f"Error loading documents: {str(e)}")
        raise
    
    return documents, filenames

def preprocess_documents(documents):
    """
    Preprocess the documents by converting them to lowercase and stripping unnecessary characters.
    
    Parameters:
    - documents: A list of document contents.
    
    Returns:
    - processed_docs: A list of preprocessed document contents.
    """
    try:
        logger.info("Preprocessing documents...")
        if not documents:
            raise ValueError("No documents provided for preprocessing.")
        
        processed_docs = [doc.lower().replace('\n', ' ').replace('\r', '').strip() for doc in documents]
        
        if not processed_docs:
            raise ValueError("Preprocessing resulted in empty documents. Check preprocessing steps.")
        
        logger.info("Documents preprocessed successfully.")
        return processed_docs
    except Exception as e:
        logger.error(f"Error preprocessing documents: {str(e)}")
        raise

def vectorize_documents(documents, n_components=100):
    """
    Vectorize the documents using TF-IDF and reduce dimensionality with SVD.
    
    Parameters:
    - documents: A list of preprocessed document contents.
    - n_components: Number of components for SVD (default is 100).
    
    Returns:
    - vectorizer: The TF-IDF vectorizer used to transform documents.
    - svd: The SVD model used for dimensionality reduction.
    - reduced_vectors: The matrix of reduced document vectors.
    """
    try:
        logger.info("Vectorizing documents using TF-IDF...")
        
        if not documents:
            raise ValueError("No documents provided for vectorization.")
        
        vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words='english')
        vectors = vectorizer.fit_transform(documents)
        
        logger.info(f"Reducing dimensionality to {n_components} components with SVD...")
        if vectors.shape[1] < n_components:
            raise ValueError(f"Number of components ({n_components}) cannot exceed the number of features ({vectors.shape[1]})")
        
        svd = TruncatedSVD(n_components=n_components)
        reduced_vectors = svd.fit_transform(vectors)
        
        logger.info("Documents vectorized and reduced successfully.")
        return vectorizer, svd, reduced_vectors
    except Exception as e:
        logger.error(f"Error during vectorization or dimensionality reduction: {str(e)}")
        raise

def save_preprocessed_data(vectorizer, svd, vectors, filenames, directory):
    """
    Save the preprocessed data (vectorizer, SVD model, vectors, filenames) to the specified directory.
    
    Parameters:
    - vectorizer: The TF-IDF vectorizer.
    - svd: The SVD model.
    - vectors: The matrix of reduced document vectors.
    - filenames: A list of filenames corresponding to the document vectors.
    - directory: Path to the directory where the data will be saved.
    """
    try:
        logger.info(f"Saving preprocessed data to directory: {directory}")
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        
        np.save(os.path.join(directory, 'reduced_vectors.npy'), vectors)
        np.save(os.path.join(directory, 'filenames.npy'), np.array(filenames))
        
        with open(os.path.join(directory, 'vectorizer.pkl'), 'wb') as f:
            pickle.dump(vectorizer, f)
        
        with open(os.path.join(directory, 'svd.pkl'), 'wb') as f:
            pickle.dump(svd, f)
        
        logger.info("Preprocessed data saved successfully.")
    except Exception as e:
        logger.error(f"Error saving preprocessed data: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        data_directory = "./data/raw"
        save_directory = "./data/processed"
        
        logger.info("Starting document processing pipeline...")
        documents, filenames = load_documents(data_directory)
        preprocessed_docs = preprocess_documents(documents)
        vectorizer, svd, vectors = vectorize_documents(preprocessed_docs)
        save_preprocessed_data(vectorizer, svd, vectors, filenames, save_directory)
        
        logger.info("Document processing pipeline completed successfully.")
    
    except Exception as e:
        logger.error(f"An error occurred during the document processing pipeline: {str(e)}")
