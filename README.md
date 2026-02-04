# Universal Sentiment Analysis Platform

A powerful web-based sentiment analysis tool that works with any social media platform. Analyze comments from YouTube, Instagram, Twitter, Facebook, TikTok, and more!

## 🌟 Features

- **Multi-Platform Support**: Works with any social media platform
- **Real-Time Analysis**: Instant sentiment classification (Positive/Negative/Neutral)
- **Beautiful Dashboard**: Interactive charts and visualizations
- **No API Keys Required**: Just paste comments or upload CSV
- **Export Results**: Download analysis as CSV
- **Demo Mode**: Try it out with sample data

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## 📖 How to Use

### Option 1: Paste Comments Directly

1. Go to the home page
2. Enter a title for your analysis (optional)
3. Paste your comments (one per line) in the text area
4. Click "Analyze Comments"
5. View results on the dashboard!

### Option 2: Upload CSV File

1. Prepare a CSV file with comments (one per line)
2. Click "Upload CSV" button
3. Select your file
4. View results automatically!

### Option 3: Try Demo

1. Click "Try Demo" button
2. See sample analysis with pre-loaded comments

## 📊 Dashboard Features

- **Sentiment Statistics**: View counts for Positive, Negative, and Neutral comments
- **Bar Chart**: Visual distribution of sentiments
- **Pie Chart**: Percentage breakdown
- **Comment Filtering**: Filter and read comments by sentiment
- **Export**: Download results as CSV file

## 🎯 Supported Platforms

You can analyze comments from:
- YouTube
- Instagram
- Twitter/X
- Facebook
- TikTok
- Reddit
- LinkedIn
- Any other platform!

Just copy the comments and paste them into the app.

## 🛠️ Technical Details

### Architecture

```
Frontend (HTML/CSS/JS) → Flask API → Sentiment Engine (VADER) → Results
```

### Components

- **Flask Backend**: REST API for sentiment analysis
- **VADER Model**: Pre-trained sentiment analysis model
- **Text Processor**: Comprehensive text cleaning pipeline
- **Chart.js**: Interactive data visualizations

### Project Structure

```
sma/
├── app.py                 # Flask application
├── sentiment_engine.py    # Sentiment analysis logic
├── text_processor.py      # Text cleaning utilities
├── model_pickle           # Pre-trained VADER model
├── requirements.txt       # Python dependencies
├── templates/
│   ├── index.html        # Home page
│   └── dashboard.html    # Results dashboard
└── static/
    ├── css/
    │   └── style.css     # Styles
    └── js/
        ├── app.js        # Main page logic
        └── dashboard.js  # Dashboard logic
```

## 🔧 Configuration

The app runs on `http://localhost:5000` by default. To change the port, edit `app.py`:

```python
app.run(debug=True, port=YOUR_PORT)
```

## 📝 CSV Format

Your CSV file should have comments in the first column:

```csv
comment
This is amazing!
Great content
Not bad
```

Or simply one comment per line:

```
This is amazing!
Great content
Not bad
```

## 🎨 Customization

### Change Theme Colors

Edit `static/css/style.css` and modify the CSS variables:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    /* ... more colors */
}
```

## 🐛 Troubleshooting

### "Module not found" error

Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Port already in use

Change the port in `app.py` or kill the process using port 5000.

### Charts not displaying

Make sure you have internet connection (Chart.js loads from CDN).

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## 💡 Tips

- For best results, clean your comments before analysis (remove URLs, excessive punctuation)
- The app works best with English text
- Larger datasets (100+ comments) provide more meaningful insights
- Use the export feature to save and share your analysis

## 🎯 Use Cases

- **Content Creators**: Analyze audience feedback on videos/posts
- **Businesses**: Monitor customer sentiment on social media
- **Marketers**: Track campaign performance
- **Researchers**: Study public opinion on topics
- **Community Managers**: Understand community sentiment

## 📞 Support

For issues or questions, please create an issue on GitHub or contact the developer.

---

**Built with ❤️ for content creators and businesses**
