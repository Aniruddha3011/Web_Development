from fpdf import FPDF
import os

class ProjectPDF(FPDF):
    def header(self):
        # Logo placeholder (can be text for now)
        self.set_font('Arial', 'B', 15)
        self.set_text_color(67, 79, 235) # A nice blue
        self.cell(0, 10, 'Universal Sentiment Analysis Platform', 0, 1, 'R')
        self.set_draw_color(67, 79, 235)
        self.line(10, 22, 200, 22)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Project Documentation - SMA', 0, 0, 'C')

    def chapter_title(self, num, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(230, 235, 255)
        self.set_text_color(30, 30, 100)
        self.cell(0, 10, f'{num}. {title}', 0, 1, 'L', 1)
        self.ln(5)

    def section_header(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, body)
        self.ln(5)

    def add_bullet(self, text):
        self.set_x(15)
        self.set_font('Arial', '', 11)
        self.cell(5, 6, chr(149), 0, 0)
        self.multi_cell(0, 6, text)
        self.ln(2)

# Create PDF
pdf = ProjectPDF()
pdf.set_auto_page_break(auto=True, margin=20)

# --- PAGE 1: INTRODUCTION ---
pdf.add_page()
pdf.chapter_title(1, "Project Introduction & Goal")
pdf.chapter_body(
    "The SMA (Social Media Analytics) Project is a robust sentiment analysis system designed to interpret human "
    "emotions across digital platforms. In today's digital age, millions of comments are generated every minute. "
    "Our platform provides a simple, automated way to categorize these comments into Positive, Negative, or Neutral "
    "sentiments."
)
pdf.section_header("Key Objectives:")
pdf.add_bullet("Provide content creators with insight into audience feedback.")
pdf.add_bullet("Help businesses monitor brand reputation in real-time.")
pdf.add_bullet("Enable academic or market research through large-scale comment analysis.")
pdf.add_bullet("Create a 'Brand Suitability Score' to help influencers understand their profile health.")

pdf.ln(10)
pdf.chapter_body(
    "This documentation serves as a guide for the presentation, explaining how the backend, frontend, and "
    "Machine Learning components work together to deliver actionable insights."
)

# --- PAGE 2: ARCHITECTURE & FOLDERS ---
pdf.add_page()
pdf.chapter_title(2, "System Architecture - Where is Everything?")
pdf.chapter_body(
    "The project is structured logically into components that handle different tasks. Here is the breakdown "
    "of what each file does and where it is located:"
)

pdf.section_header("Core Backend Files:")
pdf.add_bullet("app.py: The Flask server. It handles web requests (API endpoints) and connects everything.")
pdf.add_bullet("sentiment_engine.py: The logic engine that performs the actual sentiment calculation.")
pdf.add_bullet("comment_fetcher.py: The scraper module. It uses libraries like Instaloader and BeautifulSoup to get comments.")
pdf.add_bullet("creator_analytics.py: Specialized logic for analyzing a creator's entire profile across multiple links.")

pdf.section_header("Machine Learning & Processing:")
pdf.add_bullet("model_pickle: This is the actual PRE-TRAINED ML MODEL. It is stored as a binary file.")
pdf.add_bullet("text_processor.py: A heavy-duty cleaning script that prepares messy internet text for the ML model.")

pdf.section_header("Frontend (The UI):")
pdf.add_bullet("templates/: Contains HTML files like 'index.html' (Home) and 'dashboard.html' (Results).")
pdf.add_bullet("static/: Stores the CSS for styling and Javascript (app.js, dashboard.js) for interactive charts.")

# --- PAGE 3: DATA ACQUISITION & FETCHING ---
pdf.add_page()
pdf.chapter_title(3, "How it Fetches Comments (Data Acquisition)")
pdf.chapter_body(
    "One of the project's most powerful features is the automated retrieval of comments directly from a URL, "
    "streamlining the data collection process across different social media platforms."
)

pdf.section_header("Step-by-Step Fetching Process:")
pdf.chapter_body(
    "The 'comment_fetcher.py' script uses a variety of techniques to gather data. Here is how it handles "
    "different platforms:"
)

pdf.add_bullet("YouTube: Extracts the Video ID from the link and uses a downloader to get the latest 200+ comments.")
pdf.add_bullet("Reddit: Appends '.json' to the Reddit post URL. This allows us to read the public data directly "
               "without needing a developer account.")
pdf.add_bullet("Instagram: Uses the 'instaloader' library to identify post shortcodes. If anonymous access is "
               "blocked, it notifies the user to paste comments manually, ensuring the tool never truly breaks.")

pdf.section_header("Why This Matters:")
pdf.chapter_body(
    "By automating the fetch process, users save hours of manual work. The system handles the formatting, "
    "leaving only raw text for the next step: Sentiment Analysis."
)

# --- PAGE 4: THE SENTIMENT ENGINE & VADER ---
pdf.add_page()
pdf.chapter_title(4, "The Intelligence: Sentiment Engine & VADER")
pdf.chapter_body(
    "This is the 'Heart' of the project. We use a Machine Learning algorithm called VADER "
    "(Valence Aware Dictionary and sEntiment Reasoner)."
)

pdf.section_header("Where is the Algorithm used?")
pdf.chapter_body(
    "The algorithm is used inside 'sentiment_engine.py'. When the app starts, it loads the 'model_pickle' "
    "file. This file contains the pre-programmed 'vocabulary' and 'rules' that VADER uses."
)

pdf.section_header("How the ML Model Works:")
pdf.add_bullet("Loading: The SentimentAnalyzer class in 'sentiment_engine.py' opens 'model_pickle' using Python's pickle library.")
pdf.add_bullet("Scoring: For every comment, it calculates a 'Compound Score' between -1 (Very Negative) and +1 (Very Positive).")
pdf.add_bullet("Classification: If the score > 0.05, it is Positive. If < -0.05, it is Negative. Otherwise, it is Neutral.")

pdf.section_header("The Cleaning Pipeline (text_processor.py):")
pdf.chapter_body(
    "Before the ML model sees a comment, we must 'clean' it. Our 'text_processor.py' script performs "
    "over 100 cleaning steps, including:"
)
pdf.add_bullet("Removing Emojis and Special Characters.")
pdf.add_bullet("Correcting slang and typos (e.g., 'don't' -> 'do not', 'lmao' -> 'laughing my ass off').")
pdf.add_bullet("Removing HTML tags and broken characters to ensure the Model gets high-quality text.")

# --- PAGE 5: FEATURES & DASHBOARD ---
pdf.add_page()
pdf.chapter_title(5, "Features & The Analysis Dashboard")
pdf.chapter_body(
    "Once the analysis is complete, the results are sent to a beautiful, interactive dashboard built with Chart.js."
)

pdf.section_header("Main Features:")
pdf.add_bullet("Sentiment Breakdown: Clear counts of how many people are happy vs unhappy.")
pdf.add_bullet("Visual Charts: Pie charts and Bar charts for quick visual understanding.")
pdf.add_bullet("Brand Suitability Score: A unique metric that calculates if a creator is 'safe' for brand advertisements.")
pdf.add_bullet("Comment Filtering: Users can click on 'Positive' to read ONLY the positive comments, helping "
               "creators find their best fans quickly.")

pdf.section_header("Creator Analytics:")
pdf.chapter_body(
    "In the 'Creator Mode', the platform can analyze multiple videos or posts at once to give a 'Creator Health Report'. "
    "This aggregates data across all links to provide a high-level summary of the audience sentiment."
)

# --- PAGE 6: CONCLUSION & SUMMARY ---
pdf.add_page()
pdf.chapter_title(6, "Presentation Summary & Talking Points")
pdf.chapter_body(
    "If you are presenting this project tomorrow, here are the key 'Simple' things you should say to the audience:"
)

pdf.section_header("Closing Talking Points:")
pdf.add_bullet("'This project bridges the gap between raw data and audience understanding.'")
pdf.add_bullet("'We don't just count comments; we understand their meaning using Machine Learning.'")
pdf.add_bullet("'Our system is 'Universal' because it can fetch data from any site using its smarter fetcher module.'")
pdf.add_bullet("'The core intelligence (VADER) allows us to detect subtle emotions even in informal social media language.'")

pdf.ln(10)
pdf.set_font('Arial', 'B', 12)
pdf.set_text_color(67, 79, 235)
pdf.cell(0, 10, "Thank you! Prepared for the SMA Project Presentation.", 0, 1, 'C')

# Export
output_path = 'Project_Explanation.pdf'
pdf.output(output_path, 'F')
print(f"Detailed PDF Created Successfully: {output_path}")
