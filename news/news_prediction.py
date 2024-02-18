import pandas as pd
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import db_util
import time

# Load spaCy model
nlp = spacy.load("en_core_web_sm")
#nlp = spacy.load("en_core_web_trf")

# Preprocessing function using spaCy
def preprocess(text):
    doc = nlp(text)
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])


def predict_news(df):
    # Ensure all text transformations applied during training are mirrored here
    transform_topic = lambda topic: topic.lower().replace(" ", "_").replace("/", "_").replace("&", "").replace("'", "")

    # Initialize a list to store predictions
    predictions = []

    for index, row in df.iterrows():
        #start_time = time.time()  # Capture the start time
        topic = transform_topic(row['topic'])
        
        # Construct model and vectorizer filenames based on the topic
        model_filename = f'models/{topic}_classifier.joblib'
        vectorizer_filename = f'models/{topic}_tfidf_vectorizer.joblib'
        
        #print(f"Starting prediction for record {index} with topic '{topic}'...")  # Print statement indicating start
              
        try:
        	
            # Load the model and vectorizer
            loaded_model = joblib.load(model_filename)
            loaded_tfidf = joblib.load(vectorizer_filename)
            
            # Preprocess the title and transform it using the loaded TF-IDF vectorizer
            processed_title = preprocess(row['title'])  # Ensure preprocess function is defined
            transformed_title = loaded_tfidf.transform([processed_title])
            
            # Predict the class for the title
            prediction = loaded_model.predict(transformed_title)
            predictions.append(prediction[0])  # Assuming prediction is a list-like object
            
            #end_time = time.time()  # Capture the end time
            #print(f"Completed prediction for record {index}. Time taken: {end_time - start_time:.2f} seconds")  # Print time taken
            condidence_df = pd.read_csv('model_results.csv')
        except Exception as e:
            print(f"Error predicting for row {index}: {e}")
            predictions.append(None)  # Append None or a default value if prediction fails

    # Add the predictions as a new column to the DataFrame
    df['prediction'] = predictions
    df['confidence'] = condidence_df['accuracy']
    
    return df


def main():
    # Load your dataset
    df = db_util.get_news_all()
    pred_df = predict_news(df)
    pred_df.to_csv('prediction.csv')
    db_util.update_prediction(df)
   

# Check if the script is executed directly and call main
if __name__ == '__main__':
    main()