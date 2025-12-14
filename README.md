# IDORHunter 🏹

Simple tool to hunt for Insecure Direct Object Reference (IDOR) vulnerabilities in web applications.

## What It Does

Tests if you can access other users' data by changing ID parameters in URLs.

## Installation
```bash
pip install -r requirements.txt
```

## Usage

### Basic Example
```bash
python idorhunter.py --url "http://juice-shop.local/api/users/{id}" --range 1-20
```

### With Authentication
```bash
python idorhunter.py \
  --url "http://api.local/orders/{id}" \
  --range 1-50 \
  -H "Authorization: Bearer your_token_here" \
  -o report.txt
```

### With Cookies
```bash
python idorhunter.py \
  --url "http://dvwa.local/vulnerabilities/idor/?id={id}" \
  --range 1-10 \
  -H "Cookie: PHPSESSID=abc123; security=low"
```

## Output

The tool will:
- Test each ID in the range
- Report which IDs return 200 OK (vulnerable)
- Generate a text report with PoC curl commands
- Exit with code 1 if vulnerabilities found

## Project Details

- **Language**: Python 3
- **Dependencies**: requests only
- **Lines of Code**: ~170
- **Time to Build**: 4-6 hours

## Testing Targets

Works with:
- OWASP Juice Shop (`/api/users/{id}`, `/api/orders/{id}`)
- DVWA (any page with id parameter)
- Custom vulnerable APIs

## Limitations

- Only tests numeric IDs (not UUIDs yet)
- No GraphQL support
- Basic 200/403 detection only

## License

MIT