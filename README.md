# AI in Narrative Game

## Quickstart
```bash
git clone https://github.com/kpuneethh/AI-in-narrative-game.git
cd AI-in-narrative-game
pip install pywebio openai
python interface_pywebio.py
```
- Open the link shown in the terminal to start the game.
- Make sure you have added your OpenAI API key in a `.env` file.

## Description
This project incorporates the OpenAI API into a text story game with different story branches and hidden options.

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/kpuneethh/AI-in-narrative-game.git
   cd AI-in-narrative-game
   ```

2. **Install required libraries:**
   ```bash
   pip install pywebio openai
   ```

3. **Add your OpenAI API key:**
   - Create a `.env` file in the project root.
   - Add the following line:
     ```
     OPENAI_API_KEY=your-api-key-here
     ```

4. **Run the project:**
   ```bash
   python interface_pywebio.py
   ```
   - After running, a local link will appear in your terminal.
   - Open that link in your browser to play the game.

## Requirements
- Python 3.x
- OpenAI API key
- pywebio Python library
- openai Python library
- A modern web browser (Chrome, Firefox, etc.)

## Notes
- This project is designed to be run locally and does not have a deployed live version.
- Make sure you have an active OpenAI account and valid API key to generate responses.
