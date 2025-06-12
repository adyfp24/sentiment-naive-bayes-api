from flask import Flask, request, jsonify, render_template
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import pipeline
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
from yt_comment_scapper import get_youtube_comments
from collections import Counter
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from wordcloud import WordCloud
import traceback

app = Flask(__name__)

# Configure matplotlib to avoid GUI issues
plt.switch_backend('Agg')

# Load sentiment analysis model
try:
    pretrained = "mdhugol/indonesia-bert-sentiment-classification"
    model = AutoModelForSequenceClassification.from_pretrained(pretrained)
    tokenizer = AutoTokenizer.from_pretrained(pretrained)
    sentiment_analysis = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)
    label_index = {'LABEL_0': 'positive', 'LABEL_1': 'neutral', 'LABEL_2': 'negative'}
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {str(e)}")
    sentiment_analysis = None

# Download NLTK resources with error handling
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Indonesian stopwords with some additions
stop_words = set(stopwords.words('indonesian') + [
    'yg', 'aja', 'ya', 'ga', 'gak', 'nya', 'nih', 'sih', 
    'dong', 'deh', 'ah', 'eh', 'weh', 'wkwk', 'wkwkwk',
    'lu', 'gue', 'gw', 'lo', 'mah', 'sih', 'deh', 'dong'
])

def preprocess_text(text):
    """Clean and preprocess Indonesian text with fallback"""
    if not isinstance(text, str):
        return ""
    
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^\w\s]|[\d_]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    try:
        tokens = word_tokenize(text)
    except:
        # Fallback to simple regex tokenizer if word_tokenize fails
        tokens = re.findall(r'\b\w{3,}\b', text)
    
    tokens = [word for word in tokens if word not in stop_words and len(word) > 2]
    return ' '.join(tokens)

def generate_wordcloud(text):
    """Generate word cloud image with error handling"""
    try:
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=100,
            collocations=False
        ).generate(text)
        
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error generating wordcloud: {e}")
        return ""

def generate_sentiment_chart(sentiment_counts):
    """Generate sentiment distribution chart (thread-safe)"""
    try:
        plt.figure(figsize=(6, 4))
        labels = list(sentiment_counts.keys())
        values = list(sentiment_counts.values())
        
        bars = plt.bar(labels, values, color=['green', 'blue', 'red'])
        plt.title('Distribusi Sentimen')
        plt.ylabel('Jumlah Komentar')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        img.seek(0)
        return base64.b64encode(img.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error generating chart: {e}")
        return ""

@app.route('/', methods=['GET'])
def index():
    """Main page with form"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_youtube_comments():
    """Endpoint for YouTube comment analysis"""
    if not sentiment_analysis:
        return render_template('error.html', error_message="Model analisis sentimen tidak tersedia")
    
    try:
        youtube_url = request.form.get('youtube_url')
        if not youtube_url or 'youtube.com' not in youtube_url:
            return render_template('index.html', error="URL YouTube tidak valid")
        
        # Scrape YouTube comments with error handling
        try:
            comments = get_youtube_comments(youtube_url, max_comments=100)
            if not comments:
                return render_template('index.html', error="Tidak bisa mendapatkan komentar atau video tidak memiliki komentar")
        except Exception as e:
            print(f"Error scraping comments: {e}")
            return render_template('index.html', error="Gagal mengambil komentar dari YouTube")
        
        # Process comments and analyze sentiment
        results = []
        all_text = ""
        sentiment_counts = Counter({'positive': 0, 'neutral': 0, 'negative': 0})
        
        for comment in comments[:200]:  # Limit to 200 comments for performance
            try:
                processed_text = preprocess_text(comment)
                if not processed_text:
                    continue
                    
                result = sentiment_analysis(processed_text[:512])[0]  # Truncate to 512 tokens
                sentiment = label_index[result['label']]
                score = result['score']
                
                results.append({
                    'original_text': comment[:200] + '...' if len(comment) > 200 else comment,
                    'processed_text': processed_text[:200] + '...' if len(processed_text) > 200 else processed_text,
                    'sentiment': sentiment,
                    'score': f"{score:.2f}"
                })
                
                sentiment_counts[sentiment] += 1
                if sentiment == 'positive':
                    all_text += processed_text + " "
            except Exception as e:
                print(f"Error processing comment: {e}")
                continue
        
        if not results:
            return render_template('index.html', error="Tidak ada komentar yang bisa diproses")
        
        # Generate visualizations
        wordcloud_img = generate_wordcloud(all_text) if all_text else ""
        sentiment_chart = generate_sentiment_chart(sentiment_counts)
        
        # Prepare data for template
        total_comments = len(results)
        positive_percent = (sentiment_counts['positive'] / total_comments) * 100 if total_comments > 0 else 0
        neutral_percent = (sentiment_counts['neutral'] / total_comments) * 100 if total_comments > 0 else 0
        negative_percent = (sentiment_counts['negative'] / total_comments) * 100 if total_comments > 0 else 0
        
        return render_template('results.html',
            youtube_url=youtube_url,
            total_comments=total_comments,
            results=results[:10],
            wordcloud_img=wordcloud_img,
            sentiment_chart=sentiment_chart,
            positive_count=sentiment_counts['positive'],
            neutral_count=sentiment_counts['neutral'],
            negative_count=sentiment_counts['negative'],
            positive_percent=f"{positive_percent:.1f}",
            neutral_percent=f"{neutral_percent:.1f}",
            negative_percent=f"{negative_percent:.1f}"
        )
    
    except Exception as e:
        traceback.print_exc()
        return render_template('error.html', error_message=f"Terjadi kesalahan sistem: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5500, debug=False)  # debug=False for production