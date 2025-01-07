
# AI Travel Planning Assistant with Tavily and LangGraph

The **AI Travel Planning Assistant** is an open-source tool designed for creating personalized travel itineraries. Built with **Tavily's search and extract capabilities** and powered by **LangGraph**, it delivers comprehensive travel plans tailored to individual preferences. Perfect for both simple getaways and complex multi-city trips, this tool leverages advanced AI-driven workflows to provide detailed, practical travel itineraries.

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Running the Tool Locally](#running-the-tool-locally)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
   - [Running the Application](#running-the-application)
4. [Running the Tool in LangGraph Studio](#running-the-tool-in-langgraph-studio)
5. [Customization](#customization)
6. [Future Directions](#future-directions)

---

## Overview

The **AI Travel Planning Assistant** uses advanced AI to create personalized travel itineraries. Built with **Tavily's search and extract capabilities** and powered by **LangGraph**, it processes your preferences and requirements to generate detailed travel plans. The tool excels at handling various scenarios, from city breaks to multi-destination trips, and can adapt to different travel styles and requirements.

---
![workflow](https://i.imgur.com/92E2kcj.jpeg)

---

## Key Features

1. **Personalized Travel Preferences**: Input detailed preferences including:
   - Destination and dates
   - Budget range
   - Travel style (luxury, budget, adventure, etc.)
   - Activity preferences
   - Special requirements (accessibility, dietary)

2. **Smart Information Gathering**: 
   - Real-time destination research
   - Activity and accommodation options
   - Local transportation details
   - Weather-appropriate planning
   - Seasonal considerations

3. **Intelligent Content Organization**:
   - Category-based information clustering
   - Price range matching
   - Activity type grouping
   - Location-based organization

4. **Comprehensive Itinerary Generation**:
   - Daily schedules
   - Activity timing
   - Transportation logistics
   - Meal recommendations
   - Budget tracking
   - Alternative options

5. **Multi-Format Output**:
   - Detailed PDF itineraries
   - Markdown format support
   - Clear section organization
   - Practical information inclusion

---

## Running the Tool Locally

### Prerequisites

- Python 3.11 or later: [Python Installation Guide](https://www.tutorialsteacher.com/python/install-python)
- Tavily API Key - [Sign Up](https://tavily.com/)
- Anthropic API Key - [Sign Up](https://console.anthropic.com/settings/keys)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/travel-planner.git
   cd travel-planner
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Set Up API Keys**:
   Configure your API keys in a `.env` file:
   ```bash
   TAVILY_API_KEY={Your Tavily API Key here}
   ANTHROPIC_API_KEY={Your Anthropic API Key here}
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**:
   ```bash
   python app.py
   ```

6. **Open the App**:
   ```bash
   http://localhost:5000
   ```

---

## Running the Tool in LangGraph Studio

### Prerequisites

1. **Download LangGraph Studio**:
   - For macOS, download from [here](https://langgraph-studio.vercel.app/api/mac/latest)
   - Currently supports macOS only

2. **Install Docker**:
   - Install [Docker Desktop](https://docs.docker.com/engine/install/)
   - Requires Docker Compose version 2.22.0 or higher

### Setup Process

1. **Clone and Configure**:
   ```bash
   git clone https://github.com/yourusername/travel-planner.git
   cd travel-planner
   ```

2. **Environment Setup**:
   ```bash
   touch .env
   # Add your API keys to the .env file
   ```

3. **Launch Studio**:
   - Open LangGraph Studio
   - Select the travel-planner directory

---

## Customization

The tool's modular structure allows for various customizations:

- **Extend Travel Styles**: Add new travel categories and preferences
- **Custom Activities**: Include specialized activity types
- **Output Formats**: Modify PDF/Markdown templates
- **Language Support**: Add multilingual capabilities
- **Additional APIs**: Integrate weather, booking, or transportation services

---

## Future Directions

Potential enhancements and extensions:

- **Real-time Pricing**: Live accommodation and activity pricing
- **Booking Integration**: Direct booking capabilities
- **Weather Integration**: Real-time weather data incorporation
- **Interactive Maps**: Visual route planning and activity mapping
- **Group Planning**: Collaborative itinerary creation
- **Mobile App**: Native mobile application development

---

## Contributing

Contributions are welcome! Please feel free to submit pull requests, create issues, or suggest improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


