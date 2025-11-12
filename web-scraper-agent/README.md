# Business Web Scraper Agent

A Python-based AI agent that uses AWS Bedrock AgentCore and Strands Agents SDK to automatically scrape business information from websites. The agent uses the built-in Browser Tool to navigate websites and extract key business details.

## Features

- **Automated Web Browsing**: Uses Bedrock AgentCore's managed browser to navigate websites
- **Intelligent Information Extraction**: Automatically extracts:
  - ABN (Australian Business Number)
  - Email addresses
  - Phone numbers (Australian format)
  - Physical addresses
  - Business descriptions
- **Multi-Page Scraping**: Browses multiple pages (Home, About, Contact) for comprehensive information
- **Validation Tools**: Includes ABN validation using checksum algorithm
- **Powered by Claude**: Uses Claude Sonnet for intelligent reasoning and decision-making

## Architecture

```
Business Website
       ↓
AgentCore Browser Tool (Managed Chrome Browser)
       ↓
Strands Agent (Claude Sonnet)
       ↓
Custom Extraction Tools
       ↓
Structured Business Data
```

## Prerequisites

### AWS Requirements

1. **AWS Account** with access to:
   - Amazon Bedrock
   - Amazon Bedrock AgentCore

2. **IAM Permissions**:
   - `BedrockAgentCoreFullAccess`
   - `AmazonBedrockFullAccess`
   - `CloudWatchFullAccess` (optional, for logging)

3. **AWS Credentials** configured locally:
   ```bash
   aws configure
   ```

4. **Region Support**:
   - Recommended: `us-west-2` or `us-east-1`
   - Check [AWS Regional Services](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) for AgentCore availability

### Python Requirements

- Python 3.10 or higher
- pip or uv package manager

## Installation

### Option 1: Using pip

1. **Clone the repository** (or navigate to this directory):
   ```bash
   cd web-scraper-agent
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Option 2: Using uv (faster)

1. **Install uv** (if not already installed):
   ```bash
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

## Configuration

1. **Copy the example environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env`** with your settings:
   ```bash
   # AWS Configuration
   AWS_REGION=us-west-2
   AWS_PROFILE=default  # Optional: if using named profiles

   # Target website (optional - can be provided at runtime)
   TARGET_WEBSITE=https://example.com.au
   ```

3. **Ensure AWS credentials are configured**:
   ```bash
   aws sts get-caller-identity  # Verify credentials
   ```

## Usage

### Basic Usage

Run the agent with interactive prompt:

```bash
python agent.py
```

You'll be prompted to enter a business website URL.

### With Environment Variable

Set the target website in `.env`:

```bash
TARGET_WEBSITE=https://example.com.au
python agent.py
```

### Example Session

```
================================================================================
Business Web Scraper Agent
Powered by AWS Bedrock AgentCore + Strands Agents
================================================================================

Initializing agent in region: us-west-2
Agent initialized successfully!

Enter business website URL: https://example-business.com.au

Scraping business information from: https://example-business.com.au
This may take a moment as the agent browses the website...

================================================================================
RESULTS
================================================================================

{
  "abn": "51824753556",
  "emails": [
    "contact@example-business.com.au",
    "info@example-business.com.au"
  ],
  "phones": [
    "+61 2 9876 5432",
    "1300 123 456"
  ],
  "addresses": [
    "123 Business Street, Sydney, NSW 2000"
  ],
  "business_description": "Leading provider of business solutions in Australia...",
  "pages_visited": [
    "https://example-business.com.au/",
    "https://example-business.com.au/about",
    "https://example-business.com.au/contact"
  ]
}

Results saved to: business_info.json
```

## Project Structure

```
web-scraper-agent/
├── agent.py              # Main agent script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment configuration template
├── README.md            # This file
└── tools/               # Custom tools directory
    ├── __init__.py
    └── validation.py    # Validation utilities (ABN, email, phone)
```

## How It Works

### 1. Agent Initialization

The `BusinessScraperAgent` initializes with:
- **AgentCore Browser**: Managed Chrome browser in AWS
- **Claude Sonnet Model**: Advanced reasoning for intelligent scraping
- **Custom Tools**:
  - `extract_business_info`: HTML parsing and regex extraction
  - `summarize_business_data`: Consolidates findings from multiple pages
  - `validate_abn`: Validates Australian Business Numbers

### 2. Scraping Process

```python
# The agent follows this workflow:
1. Navigate to homepage
2. Identify relevant pages (About, Contact, etc.)
3. Visit and extract information from each page
4. Parse HTML for:
   - ABN patterns (11-digit numbers with optional spaces)
   - Email patterns (standard regex)
   - Phone patterns (Australian formats)
   - Address patterns (Australian states and postcodes)
   - Business descriptions (meta tags and about sections)
5. Consolidate findings from all pages
6. Return structured JSON
```

### 3. Custom Tools

**extract_business_info**:
- Parses HTML using BeautifulSoup
- Uses regex patterns for Australian data formats
- Extracts meta descriptions and about sections

**summarize_business_data**:
- Consolidates data from multiple pages
- Removes duplicates
- Chooses best description (longest)

**validate_abn** (in tools/validation.py):
- Implements ABN checksum algorithm
- Weighted sum divisible by 89

## Advanced Usage

### Using Additional Validation Tools

Import and use validation tools in your code:

```python
from tools.validation import validate_abn, format_business_data

# Validate ABN
is_valid = validate_abn("51824753556")

# Format results nicely
formatted = format_business_data(result)
print(formatted)
```

### Customizing the Agent

Modify `agent.py` to:

1. **Add more tools**:
   ```python
   from tools.validation import validate_abn

   self.agent = Agent(
       tools=[
           self.browser_tool.browser,
           extract_business_info,
           summarize_business_data,
           validate_abn  # Add validation
       ]
   )
   ```

2. **Change the model**:
   ```python
   self.agent = Agent(
       tools=[...],
       model="anthropic.claude-3-haiku-20240307-v1:0"  # Faster, cheaper
   )
   ```

3. **Customize extraction patterns**:
   Edit the regex patterns in `extract_business_info` function

## Troubleshooting

### Issue: "Module not found" errors

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Access Denied" from AWS

**Solution**: Check IAM permissions and AWS credentials:
```bash
aws sts get-caller-identity
aws bedrock list-foundation-models --region us-west-2
```

### Issue: "AgentCore Browser not available in region"

**Solution**: Change `AWS_REGION` in `.env` to a supported region (us-west-2 or us-east-1)

### Issue: "No information found"

**Solution**:
- Website may block automated browsers
- Try different pages or websites
- Check if ABN is displayed on the site
- Some sites may require JavaScript rendering

## Cost Considerations

- **Bedrock AgentCore Browser**: Charged per browser session minute
- **Claude Sonnet invocations**: Charged per token (input/output)
- **Typical scraping session**: 2-5 minutes, costs ~$0.10-0.50

See [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) for current rates.

## Limitations

- **Geographic Focus**: Optimized for Australian businesses (ABN, phone formats)
- **Rate Limiting**: Some websites may block or rate-limit automated access
- **JavaScript**: Complex JavaScript-heavy sites may not render fully
- **Authentication**: Cannot handle login-required pages

## Extending the Agent

### Adding Support for Other Countries

Modify regex patterns in `extract_business_info`:

```python
# For US businesses - EIN instead of ABN
ein_pattern = r'\bEIN:?\s*(\d{2}-?\d{7})\b'

# For UK phone numbers
uk_phone_pattern = r'\b(?:\+44|0)\d{10}\b'
```

### Adding More Data Extraction

```python
@tool
def extract_social_media(html_content: str) -> List[str]:
    """Extract social media links from HTML."""
    soup = BeautifulSoup(html_content, 'lxml')
    social_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if any(domain in href for domain in ['facebook.com', 'twitter.com', 'linkedin.com']):
            social_links.append(href)

    return social_links
```

## Resources

- [Strands Agents Documentation](https://strandsagents.com/latest/documentation/)
- [AWS Bedrock AgentCore User Guide](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/)
- [AWS Bedrock AgentCore Browser Tool](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/browser-tool.html)
- [Sample Repository](https://github.com/aws-samples/sample-bedrock-agentcore-with-strands-and-nova)

## License

This project is provided as-is for demonstration purposes.

## Support

For issues with:
- **Strands Agents**: [GitHub Issues](https://github.com/strands-agents/sdk-python/issues)
- **AWS Bedrock**: AWS Support or AWS Forums
- **This code**: Open an issue in the repository
