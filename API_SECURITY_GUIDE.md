# AutoU Email Classifier - API Security Guide

## 🔒 Authentication & Authorization

The AutoU Email Classifier now includes comprehensive security features to protect the API from unauthorized use.

### Authentication Methods

1. **JWT (JSON Web Tokens)** - Recommended for applications
2. **API Keys** - Legacy support for existing integrations
3. **Rate Limiting** - Automatic protection against abuse

## 🚀 Getting Started with JWT

### 1. Obtain Access Token

```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

### 2. Use Token for API Calls

```bash
curl -X POST "http://localhost:8000/api/classify/text" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Preciso de ajuda urgente com o sistema!"}'
```

## 🔑 Default Users

### Administrator
- **Username:** `admin`
- **Password:** `admin123`
- **Scopes:** `classify:read`, `classify:write`, `admin`

### API User
- **Username:** `api_user`
- **Password:** `apiuser123`
- **Scopes:** `classify:read`, `classify:write`

> ⚠️ **Production Warning**: Change default passwords in production!

## 📡 API Endpoints

### Public Endpoints (No Authentication)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/health` | GET | Health check |
| `/docs` | GET | API documentation |

### Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/token` | POST | Login and get JWT token |
| `/auth/me` | GET | Get current user info |

### Protected Endpoints (JWT Required)

| Endpoint | Method | Scopes Required | Description |
|----------|--------|-----------------|-------------|
| `/api/classify/text` | POST | `classify:read` | Classify text |
| `/api/classify/file` | POST | `classify:read` | Classify uploaded file |

### Legacy API Key Endpoints

| Endpoint | Method | Auth Method | Description |
|----------|--------|-------------|-------------|
| `/api/v1/classify` | POST | API Key | Classify text (legacy) |

## 🛡️ Security Features

### JWT Token Features
- **Expiration**: 24 hours (configurable)
- **Refresh tokens**: 7 days validity
- **Scopes**: Permission-based access control
- **Secure signing**: HS256 algorithm

### Rate Limiting
- **Default**: 100 requests per hour per user
- **Anonymous**: Same limits apply
- **Response**: HTTP 429 when exceeded

### API Key Security
- **Constant-time comparison** prevents timing attacks
- **Configurable header** (default: `X-API-Key`)
- **Easy rotation** through environment variables

## 🔧 Configuration

### Environment Variables

```bash
# JWT Configuration
JWT_SECRET_KEY=your-very-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# API Security
ENABLE_AUTH=true
API_KEY_HEADER=X-API-Key
DEFAULT_API_KEY=your-api-key-for-legacy-systems

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

### Disabling Authentication (Development Only)

```bash
# Disable all authentication
ENABLE_AUTH=false
```

## 📚 Usage Examples

### Python Example

```python
import httpx
import asyncio

async def classify_email_with_jwt():
    async with httpx.AsyncClient() as client:
        # Login
        login_response = await client.post(
            "http://localhost:8000/auth/token",
            data={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]
        
        # Classify email
        classify_response = await client.post(
            "http://localhost:8000/api/classify/text",
            json={"text": "Urgente: Sistema fora do ar!"},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        return classify_response.json()

# Run
result = asyncio.run(classify_email_with_jwt())
print(f"Classification: {result['category']}")
```

### JavaScript Example

```javascript
// Login and get token
async function getAuthToken() {
    const response = await fetch('/auth/token', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'username=admin&password=admin123'
    });
    
    const data = await response.json();
    return data.access_token;
}

// Classify email
async function classifyEmail(text) {
    const token = await getAuthToken();
    
    const response = await fetch('/api/classify/text', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
    });
    
    return await response.json();
}

// Usage
classifyEmail("Obrigado pela ajuda!")
    .then(result => console.log('Category:', result.category));
```

### cURL Examples

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" | jq -r '.access_token')

# Classify text
curl -X POST "http://localhost:8000/api/classify/text" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sistema apresentando problemas críticos!"}'

# Upload file
curl -X POST "http://localhost:8000/api/classify/file" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@email.pdf"

# Using API key (legacy)
curl -X POST "http://localhost:8000/api/v1/classify" \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test email content"}'
```

## 🔍 Swagger UI Integration

The API documentation at `/docs` includes JWT authentication:

1. Click "Authorize" button in Swagger UI
2. Enter `Bearer YOUR_TOKEN` in the Value field
3. Test endpoints directly in the browser

## ⚡ Performance Impact

### JWT Benefits
- **Stateless**: No server-side session storage
- **Scalable**: Works across multiple server instances
- **Fast**: Local token verification

### Minimal Overhead
- **Token creation**: < 1ms
- **Token verification**: < 0.5ms
- **Rate limiting**: < 0.1ms per request

## 🚨 Security Best Practices

### For Production

1. **Change Default Credentials**
   ```bash
   # Create strong passwords
   ADMIN_PASSWORD=your-super-strong-password
   ```

2. **Use Strong JWT Secret**
   ```bash
   # Generate secure secret
   JWT_SECRET_KEY=$(openssl rand -hex 32)
   ```

3. **Configure HTTPS**
   ```bash
   # Use reverse proxy (nginx/caddy) for TLS
   ```

4. **Monitor Rate Limits**
   ```bash
   # Adjust based on usage patterns
   RATE_LIMIT_REQUESTS=1000
   ```

5. **Regular Token Rotation**
   ```bash
   # Implement refresh token logic
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60  # 1 hour
   ```

### Development vs Production

| Feature | Development | Production |
|---------|------------|------------|
| Auth Required | Optional | **Always** |
| Default Passwords | OK | **Never** |
| Token Expiration | 24h | 1-8h |
| Rate Limits | Relaxed | Strict |
| HTTPS | Optional | **Required** |

## 📈 Monitoring & Logging

### Authentication Events
- Failed login attempts
- Token expiration events  
- Rate limit violations
- Unauthorized access attempts

### Log Format
```json
{
  "timestamp": "2025-08-26T12:00:00Z",
  "event": "authentication_failure",
  "username": "admin",
  "ip": "192.168.1.1",
  "reason": "invalid_password"
}
```

## 🔧 Troubleshooting

### Common Issues

**401 Unauthorized**
- Check token format: `Bearer TOKEN`
- Verify token hasn't expired
- Ensure user exists and is active

**403 Forbidden**
- User lacks required scopes
- Check endpoint scope requirements

**429 Too Many Requests**
- Rate limit exceeded
- Wait for rate limit window to reset
- Consider caching results

### Debug Mode

```bash
# Enable detailed auth logging
LOG_LEVEL=DEBUG
```

## 📖 Migration Guide

### From Unprotected API

1. **Update client code** to obtain tokens
2. **Add Authorization headers** to requests  
3. **Handle 401/403 responses** gracefully
4. **Implement token refresh** logic

### Backward Compatibility

- Web interface remains unchanged
- Legacy API key support available
- Health check always accessible
- Documentation available without auth

---

**Security is enabled by default** - Your API is now protected! 🛡️
