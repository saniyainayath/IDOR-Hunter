# IDORHunter Walkthrough

This walkthrough demonstrates how to use the IDORHunter tool to identify Insecure Direct Object Reference (IDOR) vulnerabilities in web applications using real vulnerable applications.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Testing Environment Setup](#testing-environment-setup)
- [Testing Against Vulnerable Applications](#testing-against-vulnerable-applications)
  - [DVWA (Damn Vulnerable Web Application)](#dvwa-damn-vulnerable-web-application)
  - [VAmPI (Vulnerable API)](#vampi-vulnerable-api)
  - [OWASP Juice Shop](#owasp-juice-shop)
- [Understanding Results](#understanding-results)
- [Report Analysis](#report-analysis)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Python 3.x installed
- Target vulnerable web applications running
- Network connectivity to target applications
- Basic understanding of IDOR vulnerabilities

## Installation

1. Clone or download the IDOR-Miner repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage

The IDORHunter tool tests for IDOR vulnerabilities by iterating through ID values and analyzing response patterns.

### Command Line Arguments

- `--url`: Target URL with `{id}` placeholder
- `--range`: ID range to test (e.g., 1-10)
- `--method`: HTTP method (GET/POST) - default: GET
- `-H`: HTTP headers (can be used multiple times)
- `--output`: Output file for report

### Basic Syntax

```bash
python idorhunter.py --url "http://target.com/endpoint/{id}" --range 1-10
```

## Testing Environment Setup

For this walkthrough, we'll test against three popular vulnerable applications running on an Ubuntu machine (IP: 192.168.56.107):

- **DVWA**: Port 8000 - Traditional web application vulnerabilities
- **VAmPI**: Port 5002 - API-focused vulnerabilities  
- **OWASP Juice Shop**: Port 3000 - Modern web application vulnerabilities

## Testing Against Vulnerable Applications

### DVWA (Damn Vulnerable Web Application)

#### Test 1: SQL Injection Module IDOR

```bash
python idor-miner.py \
  --url "http://192.168.56.107:8000/vulnerabilities/sqli/?id={id}&Submit=Submit" \
  --range 1-10 \
  -H "Cookie: PHPSESSID=7sdejj9i7nqj0fhq724vkv1ok5; security=low"
```

**Expected Results:**
- The tool will discover IDOR vulnerabilities where different user IDs return different data
- Status 200 responses with varying content lengths indicate successful data access

![IDOR Detection Process](idor.png)

![IDOR Vulnerabilities Found](idorfound.png)

#### Test 2: User Information Endpoint

```bash
python idor-miner.py \
  --url "http://192.168.56.107:8000/vulnerabilities/fi/?page=include.php&id={id}" \
  --range 1-5 \
  -H "Cookie: PHPSESSID=your_session_id; security=low"
```

### VAmPI (Vulnerable API)

#### Test 1: User Enumeration

```bash
python idor-miner.py \
  --url "http://192.168.56.107:5002/users/{id}" \
  --range 1-20 \
  --method GET
```

#### Test 2: Books Endpoint

```bash
python idor-miner.py \
  --url "http://192.168.56.107:5002/books/{id}" \
  --range 1-15 \
  --method GET
```

#### Test 3: User Posts/Content

```bash
python idor-miner.py \
  --url "http://192.168.56.107:5002/posts/{id}" \
  --range 1-25 \
  --method GET
```

### OWASP Juice Shop

#### Test 1: User Profiles

```bash
python idor-miner.py \
  --url "http://192.168.56.107:3000/api/Users/{id}" \
  --range 1-25 \
  --method GET
```

#### Test 2: Product Reviews

```bash
python idor-miner.py \
  --url "http://192.168.56.107:3000/api/Reviews/{id}" \
  --range 1-50 \
  --method GET
```

#### Test 3: Products Endpoint

```bash
python idor-miner.py \
  --url "http://192.168.56.107:3000/api/Products/{id}" \
  --range 1-30 \
  --method GET
```

#### Test 4: Complaints/Feedback

```bash
python idor-miner.py \
  --url "http://192.168.56.107:3000/api/Complaints/{id}" \
  --range 1-20 \
  --method GET
```

## Understanding Results

### Vulnerability Indicators

The tool identifies potential IDOR vulnerabilities based on:

1. **HTTP 200 Status Codes**: Successful access to resources
2. **Varying Response Lengths**: Different data returned for different IDs
3. **Consistent Patterns**: Multiple IDs returning similar successful responses

### Safe/Protected Indicators

- **HTTP 401/403**: Access denied (properly protected)
- **HTTP 404**: Resource not found
- **Consistent Response Patterns**: Same response for all tested IDs

### Example Output Analysis

```
[!] IDOR Found: ID 1 returned 200 (size: 1234 bytes)
[!] IDOR Found: ID 2 returned 200 (size: 1456 bytes)  
[!] IDOR Found: ID 3 returned 200 (size: 1123 bytes)
[✓] ID 4: 404 (Protected)
[!] IDOR Found: ID 5 returned 200 (size: 1334 bytes)
```

This indicates IDs 1, 2, 3, and 5 are vulnerable (different response sizes suggest different user data), while ID 4 is properly protected.

## Report Analysis

### Generated Report Structure

The tool generates a detailed report containing:

- **Scan timestamp and target information**
- **Summary of vulnerable IDs found**
- **List of protected/safe IDs**
- **Detailed response information for each ID tested**
- **Recommendations for remediation**

### Sample Report Section

```
============================================================
IDOR-Miner Scan Report
============================================================
Scan Time: 2025-12-14 10:30:45
Target URL: http://192.168.56.107:8000/vulnerabilities/sqli/?id={id}&Submit=Submit

SUMMARY
-------
Total Vulnerable IDs: 8
Total Protected IDs: 2

VULNERABLE IDs FOUND:
- ID 1: Status 200, Size 1234 bytes
- ID 2: Status 200, Size 1456 bytes
[...]
```

## Troubleshooting

### Common Issues and Solutions

#### Connection Timeouts
```
[!] Error testing ID 1: HTTPConnectionPool(...): Max retries exceeded
```

**Solutions:**
- Verify target application is running
- Check network connectivity: `ping 192.168.56.107`
- Ensure correct IP address and port
- Verify firewall settings

#### Authentication Issues
```
[!] All IDs returning 401/403
```

**Solutions:**
- Check if authentication headers are required
- Verify session cookies are valid and not expired
- Use browser developer tools to capture required headers

#### Network Configuration
```
[!] Server may be unreachable
```

**Solutions:**
- For VirtualBox: Check host-only adapter configuration
- Verify VM network settings (bridged/host-only/NAT)
- Ensure target services are bound to correct interfaces

### PowerShell vs Bash Syntax

**Windows PowerShell:**
```powershell
python idor-miner.py --url "http://target.com/api/{id}" --range 1-10 -H "Authorization: Bearer token"
```

**Linux/Mac Bash:**
```bash
python3 idor-miner.py \
  --url "http://target.com/api/{id}" \
  --range 1-10 \
  -H "Authorization: Bearer token"
```

### Running on Different Platforms

#### Transferring to Ubuntu/Linux:

1. **Create simple web server on Windows:**
   ```powershell
   python -m http.server 8080
   ```

2. **Download on Ubuntu:**
   ```bash
   mkdir ~/idor-miner
   cd ~/idor-miner
   wget http://YOUR_WINDOWS_IP:8080/idor-miner.py
   wget http://YOUR_WINDOWS_IP:8080/requirements.txt
   ```

3. **Install dependencies and run:**
   ```bash
   pip3 install -r requirements.txt
   python3 idor-miner.py --url "http://localhost:8000/vuln/{id}" --range 1-10
   ```

## Best Practices

1. **Start with small ranges** (1-10) before testing larger ranges
2. **Use proper authentication** headers when testing authenticated endpoints  
3. **Respect rate limits** - add delays between requests if needed
4. **Test incrementally** - verify connectivity before running full scans
5. **Document findings** - save reports for analysis and remediation planning

## Conclusion

The IDOR-Miner tool provides an automated way to discover Insecure Direct Object Reference vulnerabilities across different types of web applications and APIs. By testing against multiple vulnerable applications, you can understand how IDOR vulnerabilities manifest in different contexts and improve your security testing methodology.
