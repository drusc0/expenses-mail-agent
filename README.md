# LLM Practice Project

This project is a practice implementation for working with various Large Language Models (LLMs) including OpenAI, Google Gemini, and Meta Llama. It provides a modular structure for experimenting with different LLM capabilities and building applications that leverage these models.

## Project Structure

```
llm-pract/
├── src/
│   ├── agents/     # LLM agent implementations
│   ├── core/       # Core functionality and utilities
│   ├── email/      # Email-related functionality
│   ├── models/     # Data models and schemas
│   ├── main.py     # Main application entry point
│   └── containers.py # Dependency injection containers
├── requirements.txt # Project dependencies
└── env.template    # Environment variables template
```

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Gmail account with Chase email access (for email agent functionality)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/drusc0/expenses-mail-agent.git
   cd llm-pract
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp env.template .env
   ```
   Then edit the `.env` file and add your API tokens:
   - `OPENAI_TOKEN`: Your OpenAI API token
   - `GOOGLE_GEMINI_TOKEN`: Your Google Gemini API token
   - `META_LLAMA_TOKEN`: Your Meta Llama API token
   - `ENV`: Set to "development" or "production"
   - `DEBUG`: Set to "True" or "False"
   - `DOCKERIZED`: Set to "True" if running in Docker

## Usage

The project currently implements an email agent that can analyze Chase credit card expenses. Here's how to use it:

1. Ensure you have set up your environment variables as described above.

2. Run the email agent:
   ```bash
   python -m src.agents.email_agent
   ```

The agent will:
- Fetch Chase credit card expenses from your Gmail
- Summarize expenses by month
- Generate a spending analysis using Google's Gemini model

## Features

- Support for multiple LLM providers (OpenAI, Google Gemini, Meta Llama)
- Modular architecture for easy extension
- Email integration capabilities for expense tracking
- Agent-based system for complex tasks
- Automated expense analysis and summarization
- Configurable LLM models and parameters

## Development

The project uses dependency injection for better modularity and testability. The main components are organized in the following structure:

- `agents/`: Contains implementations of different LLM agents
  - `email_agent.py`: Handles email-based expense analysis
- `core/`: Core functionality and utilities
  - `settings.py`: Configuration management
  - `logging.py`: Logging utilities
- `email/`: Email-related functionality
- `models/`: Data models and schemas

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions, please:
1. Check the existing issues
2. Create a new issue with a detailed description of your problem
3. Include relevant logs and error messages
