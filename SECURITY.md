# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a security vulnerability, please follow these steps:

### How to Report

1. **Do NOT** open a public GitHub issue for security vulnerabilities
2. Email security details to the project maintainers (if available) or create a private security advisory
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- We will acknowledge receipt of your report within 48 hours
- We will provide an initial assessment within 7 days
- We will keep you informed of our progress and any actions taken
- We will notify you when the vulnerability has been resolved

### Disclosure Policy

- We will work with you to understand and resolve the issue quickly
- Security vulnerabilities will be disclosed publicly after a fix is available
- Credit will be given to reporters (unless they prefer to remain anonymous)

## Security Best Practices

When using this bot:

1. **Protect your credentials**: Never commit `.env` files or expose your `BOT_TOKEN` and `CHAT_ID`
2. **Use environment variables**: Store sensitive information in environment variables, not in code
3. **Keep dependencies updated**: Regularly update dependencies to receive security patches
4. **Review permissions**: Ensure the bot only has necessary permissions
5. **Monitor activity**: Regularly check bot logs and Telegram messages for suspicious activity

## Known Security Considerations

- This bot requires system-level permissions to execute shutdown commands
- The `/halt` command can remotely shut down devices - ensure proper access control
- Environment variables containing sensitive tokens should be kept secure
- The bot communicates with external Telegram API servers

## Security Updates

Security updates will be released as patch versions (e.g., 1.0.1, 1.0.2) and should be applied promptly.

For questions or concerns about security, please open a discussion or contact the maintainers.
