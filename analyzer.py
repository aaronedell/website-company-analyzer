#!/usr/bin/env python3
"""
Website Company Analyzer CLI
A tool that comprehensively analyzes company websites and generates executive summaries using AI.
Supports AWS Bedrock (Nova Pro) and local LLMs via Ollama.
"""

import os
import sys
import json
import requests
import argparse
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse, urlencode
from dotenv import load_dotenv
import boto3
from bs4 import BeautifulSoup
import re
from collections import defaultdict
from Wappalyzer import Wappalyzer, WebPage

# Load environment variables
load_dotenv()

# Technology name mappings for human-readable output
TECH_MAPPINGS = {
    # Cloud Hosting Providers
    'Amazon EC2': 'AWS',
    'Amazon S3': 'AWS S3',
    'Amazon CloudFront': 'AWS CloudFront',
    'AWS Certificate Manager': 'AWS',
    'Amazon ALB': 'AWS',
    'Amazon ELB': 'AWS',
    'AWS Elastic Beanstalk': 'AWS Elastic Beanstalk',
    'Amazon Web Services': 'AWS',
    'Google Cloud': 'Google Cloud Platform (GCP)',
    'Google Cloud CDN': 'GCP',
    'Google App Engine': 'GCP App Engine',
    'Firebase': 'Firebase (GCP)',
    'Microsoft Azure': 'Microsoft Azure',
    'Azure CDN': 'Azure CDN',
    'DigitalOcean': 'DigitalOcean',
    'Linode': 'Linode',
    'Vultr': 'Vultr',
    'Hetzner': 'Hetzner Cloud',
    'Oracle Cloud': 'Oracle Cloud',

    # Modern Hosting Platforms
    'Vercel': 'Vercel',
    'Netlify': 'Netlify',
    'Cloudflare': 'Cloudflare',
    'Cloudflare Pages': 'Cloudflare Pages',
    'Cloudflare Workers': 'Cloudflare Workers',
    'Railway': 'Railway',
    'Render': 'Render',
    'Fly.io': 'Fly.io',
    'Heroku': 'Heroku',
    'PlanetScale': 'PlanetScale',
    'Supabase': 'Supabase',
    'Neon': 'Neon',

    # CDN Providers
    'Cloudflare CDN': 'Cloudflare',
    'Fastly': 'Fastly',
    'Akamai': 'Akamai',
    'BunnyCDN': 'BunnyCDN',
    'KeyCDN': 'KeyCDN',

    # Traditional Hosting
    'GoDaddy': 'GoDaddy',
    'Bluehost': 'Bluehost',
    'HostGator': 'HostGator',
    'SiteGround': 'SiteGround',
    'DreamHost': 'DreamHost',
    'Namecheap': 'Namecheap',

    # Specialized Platforms
    'GitHub Pages': 'GitHub Pages',
    'GitLab Pages': 'GitLab Pages',
    'WordPress': 'WordPress',
    'Wix': 'Wix',
    'Squarespace': 'Squarespace',
    'Shopify': 'Shopify',
    'Webflow': 'Webflow',

    # Web Servers
    'Nginx': 'Nginx',
    'Apache': 'Apache',
    'Microsoft IIS': 'Microsoft IIS',
    'LiteSpeed': 'LiteSpeed',
    'Caddy': 'Caddy',

    # Frameworks
    'Next.js': 'Next.js',
    'React': 'React',
    'Vue.js': 'Vue.js',
    'Angular': 'Angular',
    'Svelte': 'Svelte',
    'Nuxt.js': 'Nuxt.js',
    'Gatsby': 'Gatsby',
    'Django': 'Django',
    'Flask': 'Flask',
    'Ruby on Rails': 'Ruby on Rails',
    'Laravel': 'Laravel',
    'Express': 'Express.js',
    'FastAPI': 'FastAPI',
}

# Categories for organizing technologies
TECH_CATEGORIES = {
    'hosting': ['AWS', 'GCP', 'Azure', 'Vercel', 'Netlify', 'Cloudflare', 'Railway', 'Render',
                'Fly.io', 'Heroku', 'DigitalOcean', 'Linode', 'Vultr', 'Hetzner', 'Oracle Cloud',
                'GitHub Pages', 'GitLab Pages', 'WordPress', 'Wix', 'Squarespace', 'Shopify', 'Webflow',
                'GoDaddy', 'Bluehost', 'HostGator', 'SiteGround', 'DreamHost', 'Namecheap'],
    'cdn': ['Cloudflare', 'Fastly', 'Akamai', 'BunnyCDN', 'KeyCDN', 'AWS CloudFront', 'Azure CDN'],
    'server': ['Nginx', 'Apache', 'Microsoft IIS', 'LiteSpeed', 'Caddy'],
    'framework': ['Next.js', 'React', 'Vue.js', 'Angular', 'Svelte', 'Nuxt.js', 'Gatsby',
                  'Django', 'Flask', 'Ruby on Rails', 'Laravel', 'Express.js', 'FastAPI'],
    'database': ['PlanetScale', 'Supabase', 'Neon', 'Firebase'],
}

# AI Provider Classes
class AIProvider:
    """Base class for AI providers"""
    def generate(self, prompt):
        raise NotImplementedError

class BedrockProvider(AIProvider):
    """AWS Bedrock Nova Pro provider"""
    def __init__(self):
        try:
            self.client = boto3.client(
                service_name="bedrock-runtime",
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
        except Exception as e:
            print(f"Error creating Bedrock client: {e}")
            print("Please ensure your AWS credentials are configured correctly.")
            sys.exit(1)

    def generate(self, prompt):
        """Generate response using AWS Bedrock Nova Pro"""
        try:
            body = json.dumps({
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {
                    "maxTokens": 3000,
                    "temperature": 0.1
                }
            })

            response = self.client.invoke_model(
                body=body,
                modelId="amazon.nova-pro-v1:0",
                accept="application/json",
                contentType="application/json"
            )

            response_body = json.loads(response.get('body').read())
            return response_body['output']['message']['content'][0]['text']
        except Exception as e:
            print(f"Bedrock error: {str(e)}")
            return None

class OllamaProvider(AIProvider):
    """Ollama local LLM provider"""
    def __init__(self, model="llama3.2:3b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"

        # Test connection
        try:
            response = requests.get(f"{base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                print(f"Warning: Could not connect to Ollama at {base_url}")
                print("Make sure Ollama is running: brew services start ollama")
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("Make sure Ollama is running: brew services start ollama")
            sys.exit(1)

    def generate(self, prompt):
        """Generate response using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1
                }
            }

            response = requests.post(self.api_url, json=payload, timeout=120)
            if response.status_code == 200:
                result = response.json()
                return result['response']
            else:
                print(f"Ollama error: {response.status_code}")
                print(response.text)
                return None
        except Exception as e:
            print(f"Ollama error: {str(e)}")
            return None

def create_ai_provider(provider_type="bedrock", ollama_model="llama3.2:3b"):
    """Factory function to create AI provider"""
    if provider_type == "ollama":
        return OllamaProvider(model=ollama_model)
    else:
        return BedrockProvider()

def detect_technologies(url, verbose=False):
    """Detect technologies used on a website and categorize them"""
    try:
        if verbose:
            print("🔍 Detecting technologies...")

        # Create Wappalyzer instance
        wappalyzer = Wappalyzer.latest()

        # Fetch webpage
        webpage = WebPage.new_from_url(url)

        # Analyze technologies
        detected = wappalyzer.analyze_with_versions_and_categories(webpage)

        # Simplify and categorize
        simplified_techs = {
            'hosting': set(),
            'cdn': set(),
            'server': set(),
            'framework': set(),
            'database': set(),
            'other': set()
        }

        for tech_name in detected.keys():
            # Map to simplified name
            simplified_name = TECH_MAPPINGS.get(tech_name, tech_name)

            # Categorize
            categorized = False
            for category, tech_list in TECH_CATEGORIES.items():
                if any(t in simplified_name or simplified_name in t for t in tech_list):
                    simplified_techs[category].add(simplified_name)
                    categorized = True
                    break

            if not categorized:
                simplified_techs['other'].add(simplified_name)

        # Convert sets to sorted lists and remove empty categories
        result = {k: sorted(list(v)) for k, v in simplified_techs.items() if v}

        if verbose and result:
            print(f"   Found {sum(len(v) for v in result.values())} technologies")

        return result

    except Exception as e:
        if verbose:
            print(f"   Warning: Technology detection failed: {str(e)}")
        return {}

def get_page_content(url, max_chars=8000):
    """Get and parse page content with better error handling"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            return text[:max_chars]
        return None
    except Exception as e:
        print(f"Error fetching {url}: {str(e)}")
        return None

def discover_metadata_files(base_url):
    """Discover and analyze metadata files like robots.txt, sitemap.xml, etc."""
    domain = urlparse(base_url).netloc
    metadata_files = {
        'robots.txt': f"https://{domain}/robots.txt",
        'sitemap.xml': f"https://{domain}/sitemap.xml",
        'sitemap_index.xml': f"https://{domain}/sitemap_index.xml",
        'humans.txt': f"https://{domain}/humans.txt",
        'llms.txt': f"https://{domain}/llms.txt",
        'ai.txt': f"https://{domain}/ai.txt",
        'security.txt': f"https://{domain}/.well-known/security.txt"
    }
    
    found_metadata = {}
    for name, url in metadata_files.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                found_metadata[name] = {
                    'url': url,
                    'content': response.text[:2000]  # First 2000 chars
                }
        except:
            continue
    
    return found_metadata

def parse_sitemap(sitemap_url):
    """Parse XML sitemap and extract all URLs"""
    urls = []
    try:
        response = requests.get(sitemap_url, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # Handle sitemap index files
            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    # Recursively parse sub-sitemaps
                    urls.extend(parse_sitemap(loc.text))
            
            # Handle regular sitemap URLs
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc is not None:
                    urls.append(loc.text)
                    
    except Exception as e:
        print(f"Error parsing sitemap {sitemap_url}: {str(e)}")
    
    return urls

def discover_all_urls(base_url, soup):
    """Comprehensively discover all URLs from multiple sources"""
    domain = urlparse(base_url).netloc
    all_urls = set()
    
    # 1. Extract URLs from main page DOM
    if soup:
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == domain:
                all_urls.add(full_url)
    
    # 2. Parse sitemaps
    sitemap_urls = [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml"
    ]
    
    for sitemap_url in sitemap_urls:
        try:
            response = requests.get(sitemap_url, timeout=10)
            if response.status_code == 200:
                sitemap_urls_found = parse_sitemap(sitemap_url)
                all_urls.update(sitemap_urls_found)
                print(f"Found {len(sitemap_urls_found)} URLs in sitemap")
                break
        except:
            continue
    
    return list(all_urls)

def categorize_urls(urls):
    """Categorize URLs by type for intelligent analysis"""
    categories = {
        'homepage': [],
        'about': [],
        'products': [],
        'services': [],
        'blog': [],
        'case_studies': [],
        'testimonials': [],
        'pricing': [],
        'contact': [],
        'team': [],
        'careers': [],
        'news': [],
        'resources': [],
        'other': []
    }
    
    for url in urls:
        url_lower = url.lower()
        path = urlparse(url).path.lower()
        
        if path in ['/', '/home', '/index']:
            categories['homepage'].append(url)
        elif any(keyword in path for keyword in ['about', 'company', 'who-we-are']):
            categories['about'].append(url)
        elif any(keyword in path for keyword in ['product', 'solution']):
            categories['products'].append(url)
        elif any(keyword in path for keyword in ['service', 'offering']):
            categories['services'].append(url)
        elif any(keyword in path for keyword in ['blog', 'article', 'post']):
            categories['blog'].append(url)
        elif any(keyword in path for keyword in ['case-stud', 'success', 'customer']):
            categories['case_studies'].append(url)
        elif any(keyword in path for keyword in ['testimonial', 'review']):
            categories['testimonials'].append(url)
        elif any(keyword in path for keyword in ['pricing', 'price', 'plan']):
            categories['pricing'].append(url)
        elif any(keyword in path for keyword in ['contact', 'reach']):
            categories['contact'].append(url)
        elif any(keyword in path for keyword in ['team', 'people', 'staff']):
            categories['team'].append(url)
        elif any(keyword in path for keyword in ['career', 'job', 'hiring']):
            categories['careers'].append(url)
        elif any(keyword in path for keyword in ['news', 'press']):
            categories['news'].append(url)
        elif any(keyword in path for keyword in ['resource', 'download', 'guide']):
            categories['resources'].append(url)
        else:
            categories['other'].append(url)
    
    return categories

def select_priority_urls(categorized_urls, max_urls=15):
    """Select the most important URLs for analysis"""
    priority_urls = []
    
    # Priority order and limits per category
    priority_categories = [
        ('homepage', 1),
        ('about', 2),
        ('products', 3),
        ('services', 2),
        ('pricing', 2),
        ('case_studies', 2),
        ('blog', 3),
        ('team', 1),
        ('resources', 1)
    ]
    
    for category, limit in priority_categories:
        urls = categorized_urls.get(category, [])[:limit]
        priority_urls.extend(urls)
        if len(priority_urls) >= max_urls:
            break
    
    return priority_urls[:max_urls]

def analyze_website(url, verbose=False, provider_type="bedrock", ollama_model="llama3.2:3b"):
    """Comprehensively analyze website and generate summary"""
    if verbose:
        print(f"🔍 Analyzing website: {url}")

    # Detect technologies first
    technologies = detect_technologies(url, verbose=verbose)

    # Get main page content and DOM
    main_content = get_page_content(url)
    if not main_content:
        print("❌ Could not fetch main page content")
        return None
    
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser') if response.status_code == 200 else None
    except:
        soup = None
    
    # Discover metadata files
    if verbose:
        print("📋 Discovering metadata files...")
    metadata = discover_metadata_files(url)
    if verbose and metadata:
        print(f"   Found: {', '.join(metadata.keys())}")
    
    # Discover all URLs
    if verbose:
        print("🕷️  Discovering all URLs...")
    all_urls = discover_all_urls(url, soup)
    if verbose:
        print(f"   Found {len(all_urls)} total URLs")
    
    # Categorize URLs
    categorized_urls = categorize_urls(all_urls)
    if verbose:
        for category, urls in categorized_urls.items():
            if urls:
                print(f"   {category}: {len(urls)} URLs")
    
    # Select priority URLs for analysis
    priority_urls = select_priority_urls(categorized_urls)
    if verbose:
        print(f"📊 Selected {len(priority_urls)} priority URLs for analysis")
    
    # Collect content from priority pages
    all_content = [f"MAIN PAGE CONTENT:\n{main_content}"]
    
    # Add metadata content
    if metadata:
        metadata_content = []
        for name, data in metadata.items():
            metadata_content.append(f"{name.upper()}:\n{data['content']}")
        all_content.append(f"METADATA FILES:\n" + "\n\n".join(metadata_content))
    
    # Collect content from priority URLs
    for i, page_url in enumerate(priority_urls, 1):
        if verbose:
            print(f"   📄 Analyzing page {i}/{len(priority_urls)}: {urlparse(page_url).path}")
        content = get_page_content(page_url, max_chars=4000)
        if content:
            all_content.append(f"PAGE: {page_url}\n{content}")
    
    # Combine all content
    combined_content = "\n\n" + "="*50 + "\n\n".join(all_content)

    # Create AI provider and generate summary
    if verbose:
        provider_name = f"Ollama ({ollama_model})" if provider_type == "ollama" else "AWS Bedrock (Nova Pro)"
        print(f"🤖 Using AI provider: {provider_name}")

    ai_provider = create_ai_provider(provider_type=provider_type, ollama_model=ollama_model)

    prompt = f"""
    Analyze the following comprehensive website content and create two detailed summaries about this company:

    Website: {url}
    Total URLs discovered: {len(all_urls)}
    Pages analyzed: {len(priority_urls) + 1}
    
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
    A comprehensive analysis including:
    - Specific product features and pricing details
    - Market positioning and competitive advantages
    - Customer success stories or case studies mentioned
    - Technology stack or methodologies used
    - Company culture, team, or leadership insights
    - Recent developments, partnerships, or initiatives
    - Any unique processes or proprietary approaches
    - Content themes and focus areas from blog/resources

    Keep both summaries professional and factual.
    """

    summary = ai_provider.generate(prompt)

    return {
        'url': url,
        'total_urls_discovered': len(all_urls),
        'priority_urls_analyzed': priority_urls,
        'metadata_files_found': list(metadata.keys()),
        'url_categories': {k: len(v) for k, v in categorized_urls.items() if v},
        'technologies': technologies,
        'analysis': summary
    }

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Comprehensively analyze company websites and generate executive summaries',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
AI Provider Options:
  --provider bedrock    Use AWS Bedrock Nova Pro (requires AWS credentials)
  --provider ollama     Use local Ollama LLM (default: llama3.2:3b)
  --ollama-model MODEL  Specify Ollama model (e.g., llama3.2:3b, llama3.2:1b)

Examples:
  # Use AWS Bedrock (default)
  python analyzer.py https://stripe.com

  # Use local Ollama with default model
  python analyzer.py https://stripe.com --provider ollama

  # Use local Ollama with specific model
  python analyzer.py https://stripe.com --provider ollama --ollama-model llama3.2:1b
        """
    )
    parser.add_argument('url', help='Website URL to analyze')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--json-only', action='store_true', help='Output only JSON, no formatted text')
    parser.add_argument('--provider', choices=['bedrock', 'ollama'], default='bedrock',
                       help='AI provider to use (default: bedrock)')
    parser.add_argument('--ollama-model', default='llama3.2:3b',
                       help='Ollama model to use (default: llama3.2:3b)')

    args = parser.parse_args()

    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    result = analyze_website(url, args.verbose, provider_type=args.provider, ollama_model=args.ollama_model)
    
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
            print("COMPREHENSIVE WEBSITE ANALYSIS")
            print("="*80)
            print(f"🌐 Website: {result['url']}")
            print(f"📊 URLs Discovered: {result['total_urls_discovered']}")
            print(f"📄 Priority Pages Analyzed: {len(result['priority_urls_analyzed'])}")
            if result['metadata_files_found']:
                print(f"📋 Metadata Files: {', '.join(result['metadata_files_found'])}")

            # Display detected technologies
            if result.get('technologies'):
                print("\n🔧 DETECTED TECHNOLOGIES:")
                for category, techs in result['technologies'].items():
                    if techs:
                        category_label = category.upper().replace('_', ' ')
                        print(f"   {category_label}: {', '.join(techs)}")

            print("\n" + "-"*80)
            print(result['analysis'])
            print("\n" + "="*80)
            print(f"💾 Analysis saved to: {output_file}")
    else:
        print("❌ Analysis failed. Please check the URL and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()
