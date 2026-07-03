# Super AI Job Description - Rainbow Jobs

Community Guardian Agent (Physical-23) for multi-platform community management.

## Overview

This project implements a Community Guardian agent that monitors and manages community health across multiple platforms. The agent tracks content, enforces community guidelines, and identifies trends to maintain a healthy community environment.

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

# Verification Test
