# medisort
A simple Python GUI tool for rapid manual sorting/tagging of large collections of images or videos into custom folders. 

## Features

- 📁 Sort both images and videos with the same interface
- ⚡ Fast preview rendering for quick decisions
- 📂 Automatic folder creation for your categories
- 🖱️ Simple drag-and-drop alternative with button categorization

## Installation

### Quick Setup
1. Clone or download this repository
2. Open terminal in the project directory
3. Run:
   pip install -e .

## Alternative Installation
   pip install pillow opencv-python

## Usage

1. **Launch the application**:
   python main.py

2. **Application Workflow**:

        Select media type (Images or Videos)

        Choose source folder containing your media

        Define categories (comma-separated, e.g., "Good, Bad, Skip", etc)

        Click "Start Sorting"

3. **Sorting Interface**:

        Click the category you want your media place into

        Files move automatically to category folders

## License
MIT License