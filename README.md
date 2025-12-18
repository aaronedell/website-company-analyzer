# Website Company Analyzer

A CLI tool that comprehensively analyzes company websites and generates detailed executive summaries using AWS Bedrock's Nova Pro model.

📋 **[View Architecture Diagram](ARCHITECTURE.md)**

## Features

- 🔍 **Comprehensive Web Crawling**: Automatically discovers and analyzes entire website structure
- 🗺️ **Sitemap Analysis**: Parses XML sitemaps to find all available pages
- 📋 **Metadata Discovery**: Reads robots.txt, humans.txt, llms.txt, and other metadata files
- 🎯 **Smart URL Categorization**: Intelligently categorizes pages (about, products, blog, etc.)
- 🤖 **AI-Powered Analysis**: Uses AWS Bedrock Nova Pro for intelligent content analysis
- 📊 **Dual Summaries**: Generates both executive and detailed summaries
- 💾 **JSON Export**: Saves structured analysis data for further processing
- 🖥️ **CLI Interface**: Easy-to-use command-line interface with multiple output options

## Prerequisites

- Python 3.7+
- AWS Account with Bedrock access
- AWS credentials configured

### AWS Setup

1. **Create AWS Account**: If you don't have one, sign up at [aws.amazon.com](https://aws.amazon.com)

2. **Enable Bedrock Access**: 
   - Go to AWS Bedrock console
   - Request access to Nova Pro model (us.amazon.nova-pro-v1:0)
   - Wait for approval (usually instant for most accounts)

3. **Get AWS Credentials**:
   - Go to [AWS IAM Console](https://console.aws.amazon.com/iam/home#/security_credentials)
   - Create new access key
   - Note down Access Key ID and Secret Access Key

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/website-company-analyzer.git
   cd website-company-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure AWS credentials**:
   ```bash
   cp .env.example .env
   # Edit .env file with your AWS credentials
   ```

## Usage

### Basic Usage
```bash
python analyzer.py https://example.com
```

### CLI Options
```bash
python analyzer.py <URL> [OPTIONS]

Options:
  -o, --output FILE     Specify output file path
  -v, --verbose        Show detailed progress
  --json-only          Output only JSON format
  -h, --help           Show help message
```

### Examples

**Analyze a website with verbose output:**
```bash
python analyzer.py https://stripe.com -v
```

**Save to specific file:**
```bash
python analyzer.py https://shopify.com -o shopify_analysis.json
```

**Get JSON output only:**
```bash
python analyzer.py https://aws.amazon.com --json-only
```

## Output Format

The tool generates comprehensive analysis with enhanced metadata:

### Console Output
```
🌐 Website: https://example.com
📊 URLs Discovered: 45
📄 Priority Pages Analyzed: 12
📋 Metadata Files: robots.txt, sitemap.xml, humans.txt
```

### Executive Summary
- Core business description
- Key products/services
- Target market
- Business model
- Notable differentiators

### Detailed Summary
- Specific product features and pricing
- Market positioning
- Customer success stories
- Technology stack
- Company culture insights
- Recent developments
- Content themes from blog/resources

### JSON Metadata
```json
{
  "url": "https://example.com",
  "total_urls_discovered": 45,
  "priority_urls_analyzed": [...],
  "metadata_files_found": ["robots.txt", "sitemap.xml"],
  "url_categories": {
    "blog": 15,
    "products": 8,
    "about": 3
  }
}
```

## Configuration

### Environment Variables

Create a `.env` file with your AWS credentials:

```env
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
```

### Alternative: AWS Profile

Instead of access keys, you can use AWS profiles:

```env
AWS_PROFILE=your_profile_name
AWS_REGION=us-east-1
```

## Troubleshooting

### Common Issues

**"ModuleNotFoundError: No module named 'boto3'"**
```bash
pip install -r requirements.txt
```

**"Error creating Bedrock client"**
- Check your AWS credentials in `.env` file
- Ensure you have Bedrock access enabled
- Verify the AWS region supports Nova Pro model

**"ValidationException: Malformed input request"**
- This usually indicates an AWS region issue
- Try changing `AWS_REGION` to `us-east-1`

**"Could not fetch main page content"**
- The website might be blocking automated requests
- Some sites require JavaScript rendering (not supported)
- Check if the URL is accessible in your browser

### AWS Costs

- Nova Pro model costs approximately $0.80 per 1M input tokens
- Typical website analysis uses 2,000-5,000 tokens
- Cost per analysis: ~$0.002-$0.004 (less than half a cent)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/website-company-analyzer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/website-company-analyzer/discussions)
- 📧 **Email**: your.email@example.com
