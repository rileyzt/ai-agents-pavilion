import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gradio import Editor
from PIL import Image
import numpy as np
from accounts import *

def resume_analysis(ui_text, ui_image):
    vectorizer = TfidfVectorizer()
    df = pd.DataFrame({'resume': [ui_text]})
    vectors = vectorizer.fit_transform(df['resume'])
    similar_indices = cosine_similarity(vectors[0]).argsort()[-2:-1]
    return str(similar_indices)

def candidate_selection(ui_text, ui_image):
    selected_candidate = resume_analysis(ui_text, ui_image)
    reason = "This resume was chosen over others due to its high similarity in key strengths and differentiators."
    return f"{selected_candidate}\n{reason}"

demo = {
    'title': 'AI-Powered HR Agent Demo',
    'subtitle': 'Analyze a Resume and Get Selection',
    'components': [
        Editor(label='Resume', value='', inline=True, allow_growth=True),
        Editor(label='Image', value='', inline=True, allow_growth=True)
    ],
    'function': [candidate_selection]
}

interface = gradio.Component(demo)