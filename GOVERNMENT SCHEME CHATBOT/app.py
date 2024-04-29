from flask import Flask, render_template, request, jsonify,redirect, url_for
import json
import mysql.connector
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib
import requests
app = Flask(__name__)

# Establish MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345678",
    database="schemes"
)

# Create a cursorp
cursor = db.cursor()

# Create a MySQL table to store the dataset
def create_dataset_table():
    cursor.execute("CREATE TABLE IF NOT EXISTS dataset (id INT AUTO_INCREMENT PRIMARY KEY, category VARCHAR(255), question TEXT, response TEXT)")
    db.commit()

create_dataset_table()

# Read data from MySQL table
def read_data_from_mysql():
    cursor.execute("SELECT * FROM dataset")
    columns = [col[0] for col in cursor.description]  # Get column names
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# Call this function whenever you need to access the dataset
dataset = read_data_from_mysql()


# Tokenization, stopwords removal, and stemming
stop_words = set(stopwords.words('english'))
ps = PorterStemmer()

# Function to calculate semantic similarity between two words using WordNet
def calculate_word_similarity(word1, word2):
    synset1 = wordnet.synsets(word1)
    synset2 = wordnet.synsets(word2)
    if synset1 and synset2:
        return max(s1.wup_similarity(s2) for s1 in synset1 for s2 in synset2)
    else:
        return 0.0  # If no synsets found, return a low similarity score

# Function to calculate semantic similarity between two sentences using NLTK
def calculate_sentence_similarity(sentence1, sentence2):
    tokens1 = word_tokenize(sentence1)
    tokens2 = word_tokenize(sentence2)
    synset_pairs = [(word1, word2) for word1 in tokens1 for word2 in tokens2]
    similarities = [calculate_word_similarity(word1, word2) for word1, word2 in synset_pairs]
    return sum(similarities) / max(len(tokens1), len(tokens2))

# Set to keep track of suggested questions
suggested_questions_set = set()

# WH words
wh_words = {'what', 'when', 'where', 'who', 'whom', 'whose', 'which', 'why', 'how'}
# List of words from the dataset for spell-checking
dataset_words = set(word.lower() for item in dataset for word in word_tokenize(item['question']))

# Function to find the closest matching word
def get_closest_word(word, dataset_words):
    closest_match = difflib.get_close_matches(word, dataset_words, n=1, cutoff=0.8)
    if closest_match:
        return closest_match[0]
    else:
        return None

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    filtered_tokens = [get_closest_word(token, dataset_words) or token for token in tokens if token not in stop_words and token.isalnum()]
    return filtered_tokens

# Function to fetch government schemes from India Government Schemes API
def fetch_government_schemes(query):
    try:
        # India Government Schemes API endpoint
        url = f"https://indian-government-schemes.p.rapidapi.com/scheme/{query}"
        headers = {
            "X-RapidAPI-Host": "indian-government-schemes.p.rapidapi.com",
            "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Extract relevant information from the response
            schemes = data['data']
            # Extract scheme names
            scheme_names = [scheme['scheme_name'] for scheme in schemes]
            return scheme_names
        else:
            return "Error: Unable to fetch data from India Government Schemes"
    except Exception as e:
        return f"Error: {e}"

# Function to calculate TF-IDF vectors
def calculate_tfidf_vectors(corpus):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return tfidf_matrix, vectorizer

# Calculate TF-IDF vectors for dataset questions
dataset_questions = [item['question'] for item in dataset]
tfidf_matrix, vectorizer = calculate_tfidf_vectors(dataset_questions)

def get_suggestions(query, dataset_questions, tfidf_matrix, vectorizer):
    # Calculate TF-IDF vector for the user query
    query_vector = vectorizer.transform([query])

    # Calculate cosine similarity between the user query and dataset questions
    similarities = cosine_similarity(query_vector, tfidf_matrix)

    # Sort dataset questions based on cosine similarity
    sorted_indices = similarities.argsort()[0][::-1]
    sorted_questions = [dataset_questions[i] for i in sorted_indices]

    # Provide suggestions based on the most similar dataset questions
    suggested_questions = sorted_questions[:5]  # Adjust the number of suggestions as needed

    return suggested_questions

def get_response(query):
    query_keywords = preprocess_text(query)
    best_matches = []
    global category_words

    # Initializing category_words with an empty string if it's not yet defined
    if 'category_words' not in globals():
        category_words = ''

    # Check for specific greetings and farewells
    if any(word in query_keywords for word in ['your', 'name']):
        return "I'm a chatbot designed to assist you. You can call me whatever you like!"
    elif any(word in query_keywords for word in ['hi', 'hey']):
        return "Hi! What can I help you with right now?"
    elif any(word in query_keywords for word in ['hello']):
        return "Hello! What can I help you with right now?"
    elif any(word in query_keywords for word in ['bye', 'goodbye']):
        return "Goodbye! Have a great day!"
    elif any(word in query_keywords for word in ['thank you', 'thanks', 'you']):
        return "You're welcome! If you need any further assistance, feel free to ask."
    elif any(word in query_keywords for word in ['thank']):
        return "You're welcome! If you need any further assistance, feel free to ask."
    elif any(word in query_keywords for word in ['love']):
        return "Thank you for expressing your feelings, but as an AI language model, I don't have emotions like humans do. However, I'm here to assist you with any questions or help you might need. How can I assist you today?"

    # Check if the query contains WH words
    wh_query_words = [word for word in query_keywords if word in wh_words]
    if all(token.isdigit() for token in query_keywords):  # If query contains only numeric values
        for item in dataset:
            if item.get('category', '') == category_words:  # Ensure the dataset item belongs to the 'farmer' category
                question_keywords = preprocess_text(item['question'])
                if any(word in question_keywords for word in query_keywords):
                    best_matches.append((item['question'], item['response'], len(query_keywords)))

    elif len(query_keywords) == 1:  # Single keyword query
        category_words = query_keywords[0]
        single_keyword = query_keywords[0].lower()
        for item in dataset:
            question_keywords = preprocess_text(item['question'])
            if single_keyword in question_keywords and len(question_keywords) == 1:
                best_matches.append((item['question'], item['response'], 1))

    elif wh_query_words:  # If query contains WH words
        for item in dataset:
            question_keywords = preprocess_text(item['question'])
            question_wh_words = [word for word in question_keywords if word in wh_words]
            if any(word in question_keywords for word in wh_query_words) and len(
                    question_wh_words) == len(wh_query_words):
                best_matches.append((item['question'], item['response'], len(wh_query_words)))
                break

    elif len(query_keywords) == 2 and query_keywords:  # Single keyword query
        single_keyword = query_keywords[0].lower()
        for item in dataset:
            question_keywords = preprocess_text(item['question'])
            if single_keyword in question_keywords and len(question_keywords) == 2:
                best_matches.append((item['question'], item['response'], 2))

    else:  # Multiple keyword query
        min_match_count = 3  # Minimum number of keyword matches
        for item in dataset:
            question_keywords = preprocess_text(item['question'])
            match_count = sum(1 for keyword in query_keywords if keyword.lower() in question_keywords)
            if match_count >= min_match_count:
                best_matches.append((item['question'], item['response'], match_count))
                break

    if best_matches:
        best_matches.sort(key=lambda x: x[2], reverse=True)  # Sort by match count
        return [match[:2] for match in best_matches]  # Return only the question and response
    else:
        # If no exact match found, get suggestions from dataset questions that match the user query
        suggested_questions = []
        loop = 0
        for item in dataset:
            # Check if the question is not already suggested and doesn't contain numeric characters
            if item['question'] not in suggested_questions_set and not any(
                    char.isdigit() for char in item['question']):
                question_keywords = preprocess_text(item['question'])
                match_count = sum(1 for keyword in query_keywords if keyword.lower() in question_keywords)
                question_wh_words = [word for word in question_keywords if word in wh_words]
                if match_count > 0 and len(question_wh_words) == len(wh_query_words) and loop < 6:
                    suggested_questions.append(item['question'])
                    suggested_questions_set.add(item['question'])  # Add the suggested question to the set
                    loop += 1
        
        if suggested_questions:
            return f"I'm sorry, I couldn't find a suitable response for that.<br>You may want to consider these questions:<br>{'<br>'.join(suggested_questions)}"
        else:
         # Check if the user query contains relevant keywords before calling the API
            with open('government_keywords.json', 'r') as f:
                government_keywords = json.load(f)['keywords']

            if any(keyword in query.lower() for keyword in government_keywords):
                # Fetch government schemes from India Government Schemes API if relevant keywords are present
                government_schemes = fetch_government_schemes(query)
                if government_schemes:
                    return government_schemes
                else:
                    return "No relevant government schemes found."
            else:
                return "I can't understand your query, try to ask somthing differnt.."
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_data_page')
def add_data_page():
    return render_template('add_data.html')

@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/logout')
def logout():
    return render_template('index.html')

# Route to handle form submission and add data to the database
@app.route('/add_data', methods=['POST', 'GET'])
def add_data():
    if request.method == 'POST':
        question = request.form['question']
        response = request.form['response']
        category = request.form.get('category')  # Optional category field
        if question and response:
            sql = "INSERT INTO dataset (question, response, category) VALUES (%s, %s, %s)"
            cursor.execute(sql, (question, response, category))
            db.commit()
            read_data_from_mysql()
            return render_template('add_data.html')
    return 'Error: Please provide both question and response.'

# Route to handle login submission
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Query to check if user exists in the database
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()

    # Check if user exists and password matches
    if user:
        # Redirect to success page if credentials are correct
        return render_template('add_data.html')
    else:
        # Display error message if credentials are incorrect
        return render_template('login.html', error='Invalid username or password.')


@app.route('/get_response', methods=['POST'])
def get_bot_response():
    user_query = request.form['user_query']
    bot_responses = get_response(user_query)
    print(category_words)
    
    # Remove keyword-matched questions from the list of responses
    if bot_responses and isinstance(bot_responses, list):
        bot_responses = [response[1] for response in bot_responses]
    
    return jsonify({'response': bot_responses})


if __name__ == '__main__':
    app.run(debug=True)
