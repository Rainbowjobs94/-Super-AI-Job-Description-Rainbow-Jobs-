# Super AI Job Description - Rainbow Jobs

Community Guardian Agent (Physical-23) for multi-platform community management.

## Overview

This project implements a Community Guardian agent that monitors and manages community health across multiple platforms. The agent tracks content, enforces community guidelines, and identifies trends to maintain a healthy community environment. It also features a functional HTML hub space for the AI, enabling chat interactions, building project archives, and uploading or fixing files within the repository.

## Agent Configuration

- **Agent ID**: Physical-23
- **Mode**: Community Guardian
- **Communication Style**: Community-focused
- **Health Score**: 0.75 (Healthy)

### Connected Platforms

| Platform  | Status  |
|-----------|---------|
| Twitch    | Active  |
| Facebook  | Active  |
| Instagram | Active  |
| YouTube   | Active  |
| LTF       | Active  |

## Project Structure

```
.
├── config/
│   ├── agent.json            # Core agent configuration
│   ├── platforms.json         # Platform connection settings
│   └── community_rules.json  # Community guidelines and thresholds
├── src/
│   ├── guardian/
│   │   └── community_guardian.py  # Main guardian logic and health monitoring
│   ├── platforms/
│   │   └── platform_connector.py  # Platform integration layer
│   └── content/
│       └── content_manager.py     # Content library and trend tracking
├── data/                          # Generated reports and data
└── README.md
```

## AI Operator Hub

The repository includes a functional HTML hub space that serves as an interface for the AI agent. Features include:
- **Chatting:** Interact with the Community Guardian AI to get status updates, generate reports, or build repository archives.
- **File Management:** Read, edit, and save files directly within the repository.
- **Uploading:** Securely upload files to specified paths within the project.

Start the hub by running:
```bash
python -m src.hub
```
Access it via a web browser at `http://127.0.0.1:5000`.

## Usage

Run the community guardian status report:

```bash
python -m src.guardian.community_guardian
```

## Community Health Thresholds

| Level     | Threshold   |
|-----------|-------------|
| Excellent | >= 0.9      |
| Healthy   | >= 0.7      |
| Warning   | >= 0.5      |
| At Risk   | >= 0.3      |
| Critical  | < 0.3       |

## Key Metrics

- **Active Streams**: 1
- **Content Library**: 3 items
- **Narrative Elements**: 7
- **Identified Trends**: 3
- **Performance Records**: 0
