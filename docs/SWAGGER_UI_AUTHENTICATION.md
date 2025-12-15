# Swagger UI Authentication Guide

## Problem
After successful login, the `/api/v1/auth/me` and `/api/v1/auth/logout` endpoints return **403 Forbidden**.

## Root Cause
Swagger UI requires you to **explicitly authorize** using the "Authorize" button before making authenticated requests. Simply copying the token into individual request headers in Swagger UI **does not work properly**.

## Solution: How to Use Swagger UI with JWT Authentication

### Step 1: Access Swagger UI
Open your browser and navigate to:
```
http://localhost:8000/docs
```

### Step 2: Login to Get Token
1. Scroll down to the **Authentication** section
2. Find the `POST /api/v1/auth/login` endpoint
3. Click **"Try it out"**
4. Enter credentials:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. Click **"Execute"**
6. **Copy the `access_token`** from the response (it's a long string starting with `eyJ...`)

### Step 3: Authorize in Swagger UI (CRITICAL STEP)
1. **Look for the "Authorize" button** at the top right of the Swagger UI page (it has a 🔓 lock icon)
2. **Click the "Authorize" button**
3. A dialog will appear with a "Bearer" input field
4. **Paste your access token** into the "Value" field
   - You can paste just the token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Or with "Bearer " prefix: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
5. Click **"Authorize"**
6. Click **"Close"**

### Step 4: Test Protected Endpoints
Now you can successfully call protected endpoints:

1. Try `GET /api/v1/auth/me`:
   - Click "Try it out"
   - Click "Execute"
   - You should get **200 OK** with your user info

2. Try `POST /api/v1/auth/logout`:
   - Click "Try it out"
   - Click "Execute"
   - You should get **200 OK**

## Why This Happens

### What Doesn't Work ❌
- Manually adding `Authorization` header in individual requests
- Copying token into the request body
- Using the token without clicking "Authorize" button

### What Works ✅
- Using the **"Authorize" button** at the top of Swagger UI
- This configures Swagger UI to automatically add the `Authorization: Bearer <token>` header to ALL requests

## Testing with curl (Alternative)

If you prefer command line testing:

```bash
# 1. Login and get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. Use token in Authorization header
TOKEN="<your_access_token_here>"

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

## Testing with Python Script

Run the provided test script:

```bash
cd /home/user/webapp
python test_auth.py
```

This script tests the complete authentication flow and confirms the API is working correctly.

## Common Issues

### Issue: Still getting 403 after clicking Authorize
**Solution**: Make sure you copied the complete token. The token is very long (200+ characters).

### Issue: Token expired
**Solution**: Tokens expire after 24 hours. Login again to get a new token.

### Issue: Wrong token type
**Solution**: Make sure you're using the `access_token`, not the `refresh_token`.

## Demo Credentials

- **Admin User**:
  - Username: `admin`
  - Password: `admin123`
  - Has admin privileges

- **Regular User**:
  - Username: `user`  
  - Password: `user123`
  - Standard user privileges

## Screenshots Guide

1. **Before Authorization**: Lock icon is open (🔓)
2. **After Authorization**: Lock icon is closed (🔒)
3. **Successful Request**: Returns 200 OK with data
4. **Failed Request** (no auth): Returns 403 Forbidden

## Technical Details

### How JWT Authentication Works

1. **Login**: Exchange username/password for access_token + refresh_token
2. **Authenticate**: Send `Authorization: Bearer <access_token>` header
3. **Validate**: Server decodes JWT, verifies signature, checks expiration
4. **Authorize**: Server checks user permissions for the requested resource

### Token Structure

The access token is a JWT (JSON Web Token) containing:
- `sub`: Username (subject)
- `is_admin`: Whether user has admin privileges
- `exp`: Expiration timestamp
- `type`: "access" (to distinguish from refresh tokens)

### Security Features

- ✅ Tokens are signed with secret key (HMAC SHA-256)
- ✅ Tokens expire after 24 hours
- ✅ Refresh tokens valid for 7 days
- ✅ Password hashing with bcrypt
- ✅ HTTPBearer security scheme
- ✅ CORS protection
- ✅ Request validation with Pydantic

## API Endpoints Reference

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/v1/auth/login` | POST | ❌ No | Get access token |
| `/api/v1/auth/refresh` | POST | ❌ No | Refresh access token |
| `/api/v1/auth/me` | GET | ✅ Yes | Get current user info |
| `/api/v1/auth/logout` | POST | ✅ Yes | Logout (invalidate token) |
| `/api/v1/translate/text` | POST | ✅ Yes | Translate text |
| `/api/v1/chat/stream` | POST | ✅ Yes | Chat with AI (streaming) |
| `/api/v1/review/contract` | POST | ✅ Yes | Review contract document |
| `/api/v1/review/bidding` | POST | ✅ Yes | Review bidding document |

## Need Help?

If you're still experiencing issues:

1. Check the server logs for detailed error messages
2. Verify your token hasn't expired
3. Make sure you clicked the "Authorize" button in Swagger UI
4. Try the `test_auth.py` script to verify the API works
5. Try using curl to eliminate Swagger UI as a variable

## Summary

**The key point**: In Swagger UI, you **MUST** click the "Authorize" button (🔓) at the top of the page and enter your token there. Simply pasting the token into individual request fields will not work.
