# 📝 AI Content Summarizer

> An intelligent web application that uses Google Gemini AI to generate concise summaries of long-form content.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](YOUR_RENDER_URL_HERE)
[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-green)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 🌟 Features

- 🤖 **AI-Powered Summarization** using Google Gemini
- 📝 **Multiple Input Methods**: Text input or file upload
- 🎨 **Multiple Summary Styles**: Bullet points, executive, academic, social media
- 💾 **Summary History**: Save and manage all your summaries
- 📊 **Export Options**: PDF, Word, Markdown formats
- 📱 **Responsive Design**: Works on all devices
- 🚀 **Fast & Efficient**: Get summaries in seconds

## 🖼️ Screenshots

### Main Interface
![Main Interface](screenshots/main.png)

### Summary Result
![Summary Result](screenshots/result.png)

### History Dashboard
![History](screenshots/history.png)

## 🚀 Live Demo

Try it out: [**Live Demo**](YOUR_RENDER_URL_HERE)

## 🛠️ Technologies Used

- **Backend**: Python, Flask
- **AI**: Google Gemini API
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Export**: ReportLab (PDF), python-docx (Word)
- **Deployment**: Render.com

## 📋 Prerequisites

- Python 3.11+
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/content-summarizer.git
cd content-summarizer
```

### 2. Install dependencies

```bash
pip install -r requirements-deploy.txt
```

### 3. Set up environment variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_ID=gemini-flash-latest
MAX_TOKENS=1024
TEMPERATURE=0.5
```

### 4. Run the application

```bash
python app.py
```

Open your browser to: `http://localhost:5000`

## 📖 Usage

### Web Interface

1. **Choose Input Method**:
   - Paste text directly, or
   - Upload a `.txt` or `.md` file

2. **Select Summary Style**:
   - Standard
   - Bullet Points
   - Executive Summary
   - Academic
   - Social Media

3. **Generate Summary**: Click the button and wait a few seconds

4. **View & Export**: Copy, download as PDF/Word, or save to history

### Command Line

```bash
# Summarize text
python main.py --text "Your content here..."

# Summarize file
python main.py --file article.txt
```

## 🗂️ Project Structure

```
content-summarizer/
├── app.py                  # Flask web application
├── main.py                 # CLI interface
├── src/
│   ├── config.py          # Configuration management
│   ├── summarizer.py      # Core AI summarization
│   ├── validator.py       # Input validation
│   ├── database.py        # Database operations
│   └── export.py          # Export functionality
├── templates/
│   └── index.html         # Web interface
├── static/
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript
├── tests/                 # Unit & property tests
├── requirements-deploy.txt
└── README.md

```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

### Quick Deploy to Render:

1. Push code to GitHub
2. Connect repository to Render
3. Add `GEMINI_API_KEY` environment variable
4. Deploy!

## 📊 Features Breakdown

### Summary Styles

- **Standard**: Balanced, comprehensive summary
- **Bullet Points**: Key points in list format
- **Executive**: Business-focused, action-oriented
- **Academic**: Formal, research-oriented
- **Social Media**: Casual, engaging, short

### Export Formats

- **PDF**: Professional formatted document
- **Word**: Editable .docx file
- **Markdown**: Plain text with formatting
- **Copy**: One-click clipboard copy

### History Management

- View all past summaries
- Search and filter
- Delete unwanted entries
- Re-export previous summaries

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/yourprofile)
- Email: your.email@example.com

## 🙏 Acknowledgments

- Google Gemini AI for the powerful summarization capabilities
- Flask community for the excellent web framework
- All contributors and testers

## 📞 Support

If you have any questions or issues, please:
- Open an issue on GitHub
- Contact me via email
- Check the [documentation](DEPLOYMENT_GUIDE.md)

---

⭐ If you found this project helpful, please give it a star!

**Industrial Training Project** | **2024-2025**
