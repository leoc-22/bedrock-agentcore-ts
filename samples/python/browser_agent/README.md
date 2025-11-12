# Browser-based Business Intelligence Agent

This sample demonstrates how to pair the **Bedrock Agentcore runtime** with the
[`strands-agent`](https://pypi.org/project/strands-agent/) orchestration
library to build a small agent that can browse a business website and extract a
handful of contact details.

The agent accepts a target business URL, navigates the site with the Bedrock
browser tool, and summarizes the most relevant information:

* Australian Business Number (ABN)
* Email addresses
* Phone numbers
* Mailing or physical addresses
* A short description of the business

## Prerequisites

* Python 3.10+
* An AWS account with access to Amazon Bedrock Agents (preview) and the browser
  tool enabled for your account.
* AWS credentials configured in one of the standard ways (environment
  variables, shared credentials file, AWS SSO, etc.).
* A Bedrock Agent that has the browser tool enabled. Capture its `agentId` and
  `agentAliasId`; you will supply them to the sample when running it.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

The dependencies include the Bedrock Agent runtime client, Beautiful Soup for
HTML parsing, and the `strands-agent` orchestration framework.

## Configuration

Set the following environment variables or pass their values as CLI arguments:

* `AWS_REGION` – the AWS Region where your Bedrock Agent is deployed.
* `BEDROCK_AGENT_ID` – the Bedrock Agent ID.
* `BEDROCK_AGENT_ALIAS_ID` – the Bedrock Agent alias ID.

You can also supply AWS credential profile information by setting
`AWS_PROFILE`.

## Running the sample

```bash
python main.py \
  --url "https://example-business.com" \
  --agent-id "$BEDROCK_AGENT_ID" \
  --agent-alias-id "$BEDROCK_AGENT_ALIAS_ID"
```

The agent will orchestrate several browser tool calls to follow obvious
navigation links such as “About”, “Contact”, and “Services”. Once it has
collected relevant HTML content, it extracts key business attributes using a
simple regex/heuristic parser and prints a structured JSON payload to stdout.

## Notes

* The sample only performs shallow navigation (two hops) and uses simple
  heuristics; it is meant to illustrate the plumbing between Bedrock Agentcore,
  the browser tool, and `strands-agent`.
* You can adjust the number of pages visited with the `--max-pages` flag if you
  want the agent to crawl a little more aggressively.
* Parsing ABNs and addresses is locale-specific; tweak the extraction patterns
  in `main.py` to support additional regions or formats.
