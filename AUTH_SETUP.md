# Authentication Setup Guide

## Overview

The application now includes user authentication using Supabase Auth. Users must sign in to access the constraint parser.

## Features Implemented

✅ **User Registration** - Email/password signup with email confirmation  
✅ **User Login** - Secure authentication with session management  
✅ **Protected Routes** - Search interface requires authentication  
✅ **Session Persistence** - Users stay logged in across page refreshes  
✅ **Sign Out** - User dropdown menu with sign out option  

## Supabase Auth Configuration

### 1. Enable Email Authentication

Your Supabase project has email authentication enabled by default. No additional setup needed!

### 2. Configure Email Templates (Optional)

To customize confirmation emails:

1. Go to **Authentication** → **Email Templates** in Supabase
2. Customize the following templates:
   - **Confirm signup**: Sent when users register
   - **Magic Link**: For passwordless login (optional)
   - **Change Email**: When users update their email
   - **Reset Password**: For password recovery

### 3. Configure Site URL (Important for Production)

1. Go to **Authentication** → **URL Configuration**
2. Set **Site URL** to your production domain:
   - Development: `http://localhost:3000`
   - Production: `https://your-app.vercel.app`
3. Add redirect URLs:
   - `http://localhost:3000/**` (for development)
   - `https://your-app.vercel.app/**` (for production)

### 4. Email Provider (For Production)

By default, Supabase uses their SMTP server with rate limits. For production:

1. Go to **Project Settings** → **Auth**
2. Scroll to **SMTP Settings**
3. Configure your own SMTP provider (SendGrid, AWS SES, etc.)

**Recommended Providers:**
- SendGrid (generous free tier)
- AWS SES (very cheap)
- Mailgun
- Postmark

## User Experience Flow

### New User (Sign Up)

```
1. User visits app
   ↓
2. Sees login/signup screen
   ↓
3. Clicks "Sign up"
   ↓
4. Enters email & password
   ↓
5. Receives confirmation email
   ↓
6. Clicks confirmation link
   ↓
7. Redirected to app & automatically logged in
   ↓
8. Can now use the constraint parser
```

### Returning User (Sign In)

```
1. User visits app
   ↓
2. Sees login screen
   ↓
3. Enters credentials
   ↓
4. Instantly logged in
   ↓
5. Can use the constraint parser
```

### Session Management

- Sessions last for 1 hour by default
- Auto-refreshed when user is active
- Persisted in localStorage
- Cleared on sign out

## UI Components

### Login Form (`components/auth/login-form.tsx`)
- Email/password inputs
- Loading states
- Error handling
- Toggle to signup

### Signup Form (`components/auth/signup-form.tsx`)
- Email/password inputs
- Password confirmation
- Email confirmation message
- Toggle to login

### Auth Gate (`components/auth/auth-gate.tsx`)
- Wraps protected content
- Shows auth forms when not logged in
- Displays loading spinner during auth check

### Navbar with Auth (`components/navbar.tsx`)
- User avatar with email initial
- Dropdown menu with:
  - User email display
  - Profile option (placeholder)
  - Sign out button

## Code Integration

### Auth Context (`lib/auth-context.tsx`)

Provides auth state and methods throughout the app:

```typescript
const { user, session, loading, signIn, signUp, signOut } = useAuth()
```

### Protect Any Component

```typescript
import { AuthGate } from "@/components/auth/auth-gate"

export default function ProtectedPage() {
  return (
    <AuthGate>
      <YourContent />
    </AuthGate>
  )
}
```

### Check Auth State

```typescript
import { useAuth } from "@/lib/auth-context"

function MyComponent() {
  const { user, loading } = useAuth()
  
  if (loading) return <div>Loading...</div>
  if (!user) return <div>Not logged in</div>
  
  return <div>Welcome, {user.email}!</div>
}
```

## Security Features

✅ **Password Requirements**
- Minimum 6 characters
- Can be customized in Supabase settings

✅ **Email Verification**
- Required by default
- Prevents fake accounts
- Can be disabled in Supabase Auth settings

✅ **Session Security**
- HTTP-only cookies (when using server-side)
- Automatic token refresh
- Secure by default

✅ **Rate Limiting**
- Built into Supabase Auth
- Prevents brute force attacks

## Testing Authentication

### Test User Flow

1. **Start the dev server:**
   ```bash
   npm run dev
   ```

2. **Visit** `http://localhost:3000`

3. **Sign Up:**
   - Click "Sign up"
   - Enter: `test@example.com` / `password123`
   - Check email for confirmation link
   - Click confirmation link

4. **Sign In:**
   - Enter credentials
   - Should see the constraint parser interface

5. **Sign Out:**
   - Click avatar in top right
   - Click "Sign Out"
   - Should return to login screen

### Check Supabase Dashboard

1. Go to **Authentication** → **Users**
2. You should see your test user listed
3. Check **Last Sign In** timestamp
4. View user metadata

## Customization Options

### Disable Email Confirmation

If you want to skip email confirmation (not recommended for production):

1. Go to **Authentication** → **Settings**
2. Uncheck **Enable email confirmations**
3. Users can sign in immediately after signup

### Add Social Auth (Google, GitHub, etc.)

1. Go to **Authentication** → **Providers**
2. Enable providers:
   - Google
   - GitHub
   - Facebook
   - Twitter
   - Apple
3. Configure OAuth credentials
4. Update signup form to include social buttons

### Password Reset Flow

Add password reset functionality:

```typescript
// In your auth context or component
const resetPassword = async (email: string) => {
  const { error } = await supabase.auth.resetPasswordForEmail(email, {
    redirectTo: 'http://localhost:3000/reset-password',
  })
  if (error) throw error
}
```

## Troubleshooting

### "Email not confirmed" error

**Solution**: Check your email and click the confirmation link.

**Alternative**: Disable email confirmation in Supabase settings (dev only).

### "Invalid login credentials"

**Possible causes:**
- Wrong password
- Email not confirmed yet
- User doesn't exist

**Solution**: Double-check credentials or create a new account.

### Not receiving confirmation emails

**Possible causes:**
- Check spam folder
- Using Supabase's rate-limited SMTP (free tier)
- Invalid email address

**Solution**: 
1. Check Supabase logs: **Authentication** → **Logs**
2. Set up custom SMTP provider
3. Verify email address is correct

### Session expires immediately

**Possible causes:**
- Browser blocking cookies
- Incognito/private mode
- Clock sync issues

**Solution**:
1. Check browser console for errors
2. Allow cookies from Supabase domain
3. Try regular browsing mode

### Sign out doesn't work

**Check:**
1. Console for errors
2. Supabase connection
3. Session storage cleared

### Can't access after login

**Check:**
1. Auth context is wrapping the app (in `layout.tsx`)
2. No console errors
3. User object exists in auth context

## Production Checklist

Before deploying with authentication:

- [ ] Set production Site URL in Supabase
- [ ] Add production redirect URLs
- [ ] Configure custom SMTP provider
- [ ] Enable email confirmation
- [ ] Test signup flow end-to-end
- [ ] Test login flow
- [ ] Test sign out
- [ ] Test session persistence
- [ ] Customize email templates
- [ ] Set up password requirements
- [ ] Configure rate limits (if needed)
- [ ] Test on mobile devices

## Environment Variables

Make sure these are set (already in `.env.local`):

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

The anon key is safe for client-side use. It's used for authentication and respects RLS policies.

## Database Policies (Optional)

If you want to store user-specific data (like query history), create tables with RLS:

```sql
-- Example: User query history table
CREATE TABLE user_queries (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  query TEXT NOT NULL,
  result JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_queries ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own queries
CREATE POLICY "Users can view own queries"
  ON user_queries
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own queries
CREATE POLICY "Users can insert own queries"
  ON user_queries
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);
```

## Next Steps

### Future Enhancements

1. **Social Login**
   - Add Google OAuth
   - Add GitHub OAuth

2. **User Profiles**
   - Display name
   - Avatar upload
   - Preferences

3. **Query History**
   - Save user queries
   - View past results
   - Export functionality

4. **Team Collaboration**
   - Share constraints
   - Invite team members
   - Role-based access

5. **API Keys**
   - Generate API keys for users
   - Programmatic access
   - Usage tracking

## Resources

- [Supabase Auth Docs](https://supabase.com/docs/guides/auth)
- [Next.js Auth Patterns](https://nextjs.org/docs/authentication)
- [Auth Best Practices](https://supabase.com/docs/guides/auth/auth-helpers/nextjs)

## Support

For auth issues:
1. Check Supabase Auth logs
2. Review browser console
3. Test with a fresh incognito window
4. Verify environment variables

---

**Authentication is now fully integrated! 🔐**

Users must sign in to access the constraint parser, providing security and enabling future user-specific features.

