#!/usr/bin/env python3
"""
Website Company Analyzer CLI
A tool that scrapes company websites and generates executive summaries using AWS Bedrock.
"""

import os
import sys
import json
import requests
import argparse
from urllib.parse import urljoin, urlparse
from dotenv import load_dotenv
import boto3
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

def create_bedrock_client():
    """Create AWS Bedrock client"""
    try:
        return boto3.client(
            service_name="bedrock-runtime",
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
    except Exception as e:
        print(f"Error creating Bedrock client: {e}")
        print("Please ensure your AWS credentials are configured correctly.")
        sys.exit(1)

def get_page_content(url):
    """Get and parse page content"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text[:5000]
        return None
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def find_key_pages(base_url, soup):
    """Find key pages like About, Products, etc."""
    key_pages = []
    if soup:
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text().lower()
            
            if any(keyword in text for keyword in ['about', 'company', 'products', 'services', 'case studies', 'blog']):
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    key_pages.append(full_url)
    
    return list(set(key_pages))[:5]

def call_bedrock(bedrock_client, prompt):
    """Call AWS Bedrock Nova Pro model"""
    try:
        body = json.dumps({
            "messages": [{"role": "user", "content": [{"text": prompt}]}],
            "inferenceConfig": {
                "maxTokens": 2000,
                "temperature": 0.1
            }
        })
        
        response = bedrock_client.invoke_model(
            body=body,
            modelId="us.amazon.nova-pro-v1:0",
            accept="application/json",
            contentType="application/json"
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body['output']['message']['content'][0]['text']
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        return None

def analyze_website(url, verbose=False):
    """Analyze website and generate summary"""
    if verbose:
        print(f"Analyzing website: {url}")
    
    main_content = get_page_content(url)
    if not main_content:
        print("Could not fetch main page content")
        return None
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser') if response.status_code == 200 else None
    except:
        soup = None
    
    key_pages = find_key_pages(url, soup)
    if verbose:
        print(f"Found key pages: {key_pages}")
    
    all_content = [main_content]
    for page_url in key_pages:
        content = get_page_content(page_url)
        if content:
            all_content.append(content)
    
    combined_content = "\n\n".join(all_content)
    bedrock_client = create_bedrock_client()
    
    prompt = f"""
    Analyze the following website content and create two summaries about this company:

    Website: {url}
    Content: {combined_content}

    Please provide:

    **EXECUTIVE SUMMARY:**
    A concise overview covering:
    1. What the company does (core business)
    2. Key products/services offered
    3. Target market/customers
    4. Business model (if apparent)
    5. Notable achievements or differentiators

    **DETAILED SUMMARY:**
    A more comprehensive analysis including:
    - Specific product features and pricing details
    - Market positioning and competitive advantages
    - Customer success stories or case studies mentioned
    - Technology stack or methodologies used
    - Company culture, team, or leadership insights
    - Recent developments, partnerships, or initiatives
    - Any unique processes or proprietary approaches

    Keep both summaries professional and factual.
    """
    
    summary = call_bedrock(bedrock_client, prompt)
    
    return {
        'url': url,
        'key_pages_analyzed': key_pages,
        'analysis': summary
    }

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='Analyze company websites and generate executive summaries')
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json-only', action='store_true', help='Output only JSON, no formatted text')
    
    args = parser.parse_args()
    
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    result = analyze_website(url, args.verbose)
    
    if result and result['analysis']:
        # Determine output file
        if args.output:
            output_file = args.output
        else:
            domain = urlparse(url).netloc.replace('.', '_')
            output_file = f"analysis_{domain}.json"
        
        # Save JSON
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        if args.json_only:
            print(json.dumps(result, indent=2))
        else:
            # Print formatted output
            print("\n" + "="*80)
            print("WEBSITE ANALYSIS")
            print("="*80)
            print(result['analysis'])
            print("\n" + "="*80)
            print(f"Analysis saved to: {output_file}")
    else:
        print("Analysis failed. Please check the URL and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
