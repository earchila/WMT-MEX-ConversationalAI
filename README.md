# Agent Development Kit (ADK) Samples

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

<img src="https://github.com/google/adk-docs/blob/main/docs/assets/agent-development-kit.png" alt="Agent Development Kit Logo" width="150">

Welcome to the ADK Sample Agents repository! This collection provides ready-to-use agents built on top of the [Agent Development Kit](https://google.github.io/adk-docs/), designed to accelerate your development process. These agents cover a range of common use cases and complexities, from simple conversational bots to complex multi-agent workflows.

## ✨ Getting Started 
This repo contains ADK sample agents for both **Python** and **Java.** Navigate to the **[Python](python/)** and **[Java](java/)** subfolders to see language-specific setup instructions, and learn more about the available sample agents. 

To learn more, check out the [ADK Documentation](https://google.github.io/adk-docs/), and the GitHub repositories for [ADK Python](https://github.com/google/adk-python) and [ADK Java](https://github.com/google/adk-java). 

## Important Environment Setup Notes

When working with ADK agents, especially those interacting with Google Cloud services like Vertex AI, you might encounter situations where environment variables need to be managed carefully.

*   **`CODE_INTERPRETER_ID` for Vertex AI Extensions:** If you are using Vertex AI Code Interpreter extensions, `adk` may create a new extension every time it runs if it doesn't find an existing `CODE_INTERPRETER_ID` environment variable. These extensions are persistent Google Cloud resources and are not automatically deleted. To reuse an existing extension, capture its resource name (printed in the console during creation) and set it as the `CODE_INTERPRETER_ID` in your agent's `.env` file. Refer to the specific agent's `README.md` (e.g., `python/agents/README.md` for Python agents) for detailed instructions on managing this.

## 🌳 Repository Structure
```bash
├── python
│   ├── agents
│   │   ├── data_science_v2
│   └── README.md
└── README.md
```

## 📄 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/google/adk-samples/blob/main/LICENSE) file for details.

## Disclaimers

This is not an officially supported Google product. This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security).

This project is intended for demonstration purposes only. It is not intended for use in a production environment.