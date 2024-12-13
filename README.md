# Jolly Street Journal 🗞️

A modern news portal that transforms serious news articles into engaging comic-style summaries with AI-generated images. The application fetches the latest news from either The New York Times or The Guardian, processes them using AI to create comic-style summaries, and generates matching comic-strip style images.


![Demo](jolly-street-demo.gif)


## Features

- **Dynamic News Source Selection**: Choose between The New York Times Top Stories or The Guardian as your news source
- **AI-Powered Comic Summaries**: Utilizes Claude AI to create engaging comic-style headers and summaries
- **Comic-Style Image Generation**: Generates four unique XKCD-style images for each article using Replicate AI
- **Responsive Grid Layout**: Modern, clean interface with a responsive grid for article previews
- **Interactive Article Views**: Click any article to view its full comic summary with a 2x2 grid of generated images
- **Automatic Content Updates**: Background job fetches and processes fresh news articles every 30 minutes
- **Hover Interactions**: View the AI prompts used to generate each image by hovering over them

## Tech Stack

- **Backend**: Python/Flask with SQLite database
- **Frontend**: Vanilla JavaScript with Bootstrap 5
- **AI Services**:
  - Claude AI (Anthropic) for comic summaries
  - Replicate AI for image generation
- **News APIs**:
  - The New York Times Top Stories API
  - The Guardian API

## Setup Instructions

1. **Clone the Repository**
```bash
git clone [repository-url]
cd jolly-street-journal
```

2. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure API Keys**
Create a `.env` file in the project root with the following keys:
```
NYTIMES_API_KEY=your_nytimes_api_key
GUARDIAN_API_KEY=your_guardian_api_key
CLAUDE_API_KEY=your_claude_api_key
REPLICATE_API_KEY=your_replicate_api_key
```

4. **Initialize Database**
