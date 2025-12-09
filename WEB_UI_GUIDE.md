# Web UI Guide

## 🚀 Quick Start

### 1. Start the Web Server

```bash
python app.py
```

### 2. Open Your Browser

Navigate to: **http://localhost:5000**

The server will automatically open and you'll see a beautiful web interface!

## ✨ Features

### Text Input Mode
- Paste or type your content directly into the text area
- Perfect for quick summarization of copied text
- No file needed

### File Upload Mode
- Upload `.txt` or `.md` files
- Drag and drop support
- Handles large documents

### Summary Results
- Clean, readable summary display
- Detailed metadata:
  - Original length (characters)
  - Summary length (characters)
  - Compression percentage
  - Model used
  - Timestamp
- One-click copy to clipboard

## 🎨 Interface

The web UI features:
- **Modern gradient design** with purple theme
- **Responsive layout** - works on desktop, tablet, and mobile
- **Tab-based input** - switch between text and file input
- **Real-time feedback** - loading indicators and error messages
- **Smooth animations** - professional user experience

## 🔧 Configuration

The web UI uses the same `.env` configuration as the CLI:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL_ID=gemini-flash-latest
MAX_TOKENS=1024
TEMPERATURE=0.5
```

## 📝 Usage Examples

### Example 1: Summarize Pasted Text
1. Click on "📝 Text Input" tab
2. Paste your article or content
3. Click "🚀 Generate Summary"
4. View and copy the summary

### Example 2: Upload a File
1. Click on "📄 File Upload" tab
2. Click to select a file or drag and drop
3. Click "🚀 Generate Summary"
4. View and copy the summary

## 🌐 Network Access

The server runs on `0.0.0.0:5000`, which means:
- **Local access**: http://localhost:5000
- **Network access**: http://192.168.0.106:5000 (your local IP)
- Other devices on your network can access it too!

## 🛑 Stopping the Server

Press `CTRL+C` in the terminal where the server is running.

## 🔒 Security Notes

- This is a **development server** - not for production use
- For production, use a proper WSGI server like Gunicorn or uWSGI
- The server accepts connections from any IP on your network
- Keep your API key secure in the `.env` file

## 🐛 Troubleshooting

### Port Already in Use
If port 5000 is already taken, edit `app.py` and change:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
to a different port like `5001`.

### API Key Errors
Make sure your `.env` file has a valid `GEMINI_API_KEY`.

### File Upload Issues
- Ensure files are UTF-8 encoded
- Maximum file size: 16MB
- Supported formats: `.txt`, `.md`

## 📱 Mobile Friendly

The interface is fully responsive and works great on:
- 📱 Smartphones
- 📱 Tablets
- 💻 Laptops
- 🖥️ Desktops

## 🎯 API Endpoints

For developers who want to integrate:

### POST /summarize
Summarize content via API

**Form Data:**
- `input_method`: "text" or "file"
- `content`: text content (if input_method=text)
- `file`: uploaded file (if input_method=file)

**Response:**
```json
{
  "success": true,
  "summary": "The summarized text...",
  "metadata": {
    "original_length": 1555,
    "summary_length": 683,
    "compression": "56.1%",
    "model_used": "gemini-flash-latest",
    "timestamp": "2025-12-06 00:31:51"
  }
}
```

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "summarizer_initialized": true
}
```

## 🎨 Customization

Want to customize the look? Edit `templates/index.html`:
- Change colors in the `<style>` section
- Modify the gradient: `background: linear-gradient(...)`
- Update text and labels
- Add your own branding

Enjoy your new web UI! 🎉
