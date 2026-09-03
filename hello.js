openssl s_client \
  -connect hvault.staging.echonet:443 \
  -servername hvault.staging.echonet \
  -CAfile ~/.certs/keychain.bundle.20231124.pem \
  </dev/null 2>&1 | grep -E "Verify return code|verify error|subject=|issuer="


python -c "import os; print('REQUESTS_CA_BUNDLE=', os.getenv('REQUESTS_CA_BUNDLE')); print('SSL_CERT_FILE=', os.getenv('SSL_CERT_FILE'))"

{
  "name": "Python Debugger: Flask",
  "type": "debugpy",
  "request": "launch",
  "module": "flask",

  "env": {
    "REQUESTS_CA_BUNDLE": "${env:HOME}/.certs/keychain.bundle.20231124.pem",
    "SSL_CERT_FILE": "${env:HOME}/.certs/keychain.bundle.20231124.pem",
    "PIP_CERT": "${env:HOME}/.certs/keychain.bundle.20231124.pem"
  }
}
