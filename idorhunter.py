#!/usr/bin/env python3
"""
IDORHunter: Simple Access Control Vulnerability Scanner
Tests if different IDs can access resources they shouldn't
"""

import requests
import argparse
import sys
from datetime import datetime
from urllib.parse import urlparse

# Disable SSL warnings for lab environments
requests.packages.urllib3.disable_warnings()

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_banner():
    print(f"{Colors.BLUE}")
    print("=" * 50)
    print("  IDOR-Miner - Simple Access Control Tester")
    print("=" * 50)
    print(f"{Colors.RESET}\n")

def test_idor(url, id_range, headers=None, method="GET"):
    """
    Test for IDOR vulnerabilities by trying different IDs
    """
    vulnerable_ids = []
    safe_ids = []
    
    start_id, end_id = map(int, id_range.split('-'))
    total = end_id - start_id + 1
    
    print(f"[*] Testing {total} IDs from {start_id} to {end_id}...")
    print(f"[*] Target: {url}\n")
    
    # Parse headers if provided
    header_dict = {}
    if headers:
        for h in headers:
            key, value = h.split(':', 1)
            header_dict[key.strip()] = value.strip()
    
    for test_id in range(start_id, end_id + 1):
        # Replace {id} placeholder with current test ID
        test_url = url.replace('{id}', str(test_id))
        
        try:
            # Make request
            if method.upper() == "GET":
                response = requests.get(test_url, headers=header_dict, 
                                       verify=False, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(test_url, headers=header_dict, 
                                        verify=False, timeout=5)
            else:
                print(f"{Colors.RED}[!] Unsupported method: {method}{Colors.RESET}")
                return
            
            # Check if successful
            if response.status_code == 200:
                size = len(response.content)
                print(f"{Colors.RED}[!] IDOR Found: ID {test_id} returned {response.status_code} (size: {size} bytes){Colors.RESET}")
                vulnerable_ids.append({
                    'id': test_id,
                    'status': response.status_code,
                    'size': size,
                    'url': test_url
                })
            elif response.status_code in [401, 403]:
                safe_ids.append(test_id)
                print(f"{Colors.GREEN}[✓] ID {test_id}: {response.status_code} (Protected){Colors.RESET}")
            else:
                safe_ids.append(test_id)
                print(f"[·] ID {test_id}: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"{Colors.YELLOW}[!] Error testing ID {test_id}: {str(e)}{Colors.RESET}")
            continue
    
    return vulnerable_ids, safe_ids

def generate_report(url, vulnerable_ids, safe_ids, output_file):
    """
    Generate a simple text report
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = f"""
{'=' * 60}
IDOR-Miner Scan Report
{'=' * 60}
Scan Time: {timestamp}
Target URL: {url}

SUMMARY
-------
Total Vulnerable IDs: {len(vulnerable_ids)}
Total Protected IDs: {len(safe_ids)}

"""
    
    if vulnerable_ids:
        report += "VULNERABLE IDs (IDOR DETECTED)\n"
        report += "-" * 60 + "\n"
        for vuln in vulnerable_ids:
            report += f"  ID: {vuln['id']}\n"
            report += f"  Status: {vuln['status']}\n"
            report += f"  Response Size: {vuln['size']} bytes\n"
            report += f"  PoC: curl '{vuln['url']}'\n"
            report += "\n"
    else:
        report += "✓ No IDOR vulnerabilities found! All IDs properly protected.\n\n"
    
    if safe_ids:
        report += f"\nProtected IDs: {', '.join(map(str, safe_ids[:20]))}"
        if len(safe_ids) > 20:
            report += f"... ({len(safe_ids) - 20} more)"
        report += "\n"
    
    report += "\n" + "=" * 60 + "\n"
    
    # Print to console
    print("\n" + report)
    
    # Save to file
    if output_file:
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"{Colors.GREEN}[✓] Report saved to: {output_file}{Colors.RESET}")

def main():
    parser = argparse.ArgumentParser(
        description='IDOR-Miner: Test for Insecure Direct Object Reference vulnerabilities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python idor-miner.py --url "http://juice-shop.local/api/users/{id}" --range 1-20
  python idor-miner.py --url "http://dvwa.local/profile.php?id={id}" --range 1-50 -H "Cookie: PHPSESSID=abc123"
  python idor-miner.py --url "http://api.local/orders/{id}" --range 100-200 --method GET -o report.txt
        """
    )
    
    parser.add_argument('--url', required=True, 
                       help='Target URL with {id} placeholder (e.g., http://site.com/api/users/{id})')
    parser.add_argument('--range', required=True, 
                       help='ID range to test (e.g., 1-100)')
    parser.add_argument('-H', '--header', action='append', 
                       help='HTTP header (e.g., "Authorization: Bearer token")')
    parser.add_argument('--method', default='GET', 
                       help='HTTP method (default: GET)')
    parser.add_argument('-o', '--output', 
                       help='Output file for report (optional)')
    
    args = parser.parse_args()
    
    # Validate URL has {id} placeholder
    if '{id}' not in args.url:
        print(f"{Colors.RED}[!] Error: URL must contain {{id}} placeholder{Colors.RESET}")
        sys.exit(1)
    
    print_banner()
    
    # Run the test
    vulnerable_ids, safe_ids = test_idor(
        args.url, 
        args.range, 
        args.header,
        args.method
    )
    
    # Generate report
    output_file = args.output if args.output else f"idor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    generate_report(args.url, vulnerable_ids, safe_ids, output_file)
    
    # Exit code based on findings
    if vulnerable_ids:
        print(f"\n{Colors.RED}[!] SECURITY ISSUE: Found {len(vulnerable_ids)} IDOR vulnerabilities!{Colors.RESET}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}[✓] No IDOR vulnerabilities detected.{Colors.RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()