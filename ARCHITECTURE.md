# Architecture Diagram

```
┌─────────────────┐
│   User Input    │
│      (URL)      │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Python CLI     │
│    Script       │
│   (analyzer.py) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐       ┌─────────────────┐
│  Metadata       │──────▶│  robots.txt     │
│  Discovery      │       │  sitemap.xml    │
│                 │       │  humans.txt     │
└─────────┬───────┘       │  llms.txt, etc. │
          │               └─────────────────┘
          ▼
┌─────────────────┐       ┌─────────────────┐
│  Sitemap        │──────▶│  XML Parsing    │
│  Analysis       │       │  URL Extraction │
└─────────┬───────┘       └─────────────────┘
          │
          ▼
┌─────────────────┐       ┌─────────────────┐
│  URL Discovery  │──────▶│  Target Website │
│  & Crawling     │       │   (all pages)   │
│ requests +      │       └─────────────────┘
│ BeautifulSoup   │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  URL            │
│  Categorization │
│ (smart sorting) │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Priority       │
│  Selection      │
│ (top 15 pages)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  Content        │
│  Processing     │
│ (text cleanup)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│   AWS Bedrock   │
│   Nova Pro      │
│  (AI Analysis)  │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│ Executive &     │
│ Detailed        │
│ Summaries       │
└─────────┬───────┘
          │
          ▼
┌─────────────────┐
│  JSON Output    │
│ analysis_*.json │
└─────────────────┘
```

## Enhanced Data Flow

1. **User Input**: Provides target website URL
2. **CLI Script**: Orchestrates the comprehensive analysis process
3. **Metadata Discovery**: Finds and reads robots.txt, sitemap.xml, humans.txt, llms.txt, etc.
4. **Sitemap Analysis**: Parses XML sitemaps to extract all available URLs
5. **URL Discovery**: Combines sitemap URLs with DOM-discovered links
6. **URL Categorization**: Intelligently sorts URLs by type (about, products, blog, etc.)
7. **Priority Selection**: Selects top 15 most important pages for analysis
8. **Content Processing**: Cleans and prepares text from all selected pages
9. **AWS Bedrock**: Generates AI-powered comprehensive summaries using Nova Pro
10. **Output**: Saves structured analysis with metadata as JSON file

## Enhanced Components

- **Input**: Website URL (command line argument)
- **Metadata Parser**: Discovers robots.txt, sitemap.xml, humans.txt, llms.txt, ai.txt, security.txt
- **Sitemap Parser**: XML parsing with recursive sitemap index support
- **URL Categorizer**: Smart classification of pages by content type
- **Priority Selector**: Intelligent selection of most valuable pages
- **Scraper**: requests + BeautifulSoup for content extraction
- **AI Engine**: AWS Bedrock Nova Pro model
- **Output**: JSON file with comprehensive analysis and metadata
