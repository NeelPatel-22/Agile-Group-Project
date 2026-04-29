from html import escape


def build_confirmation_email(username, confirmation_url):
    safe_username = escape(username)
    safe_confirmation_url = escape(confirmation_url, quote=True)

    text_body = (
        f"Hi {username},\n\n"
        "Welcome to RecipeHub. Please confirm your account by opening this link:\n"
        f"{confirmation_url}\n\n"
        "This link expires in 24 hours.\n\n"
        "If you did not create this account, you can ignore this email."
    )

    html_body = f"""
    <!doctype html>
    <html lang="en">
    <body style="margin:0; padding:0; background:#f4f7f2; font-family:Arial, sans-serif; color:#203126;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f4f7f2; padding:32px 12px;">
            <tr>
                <td align="center">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:560px; background:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #dfe8db;">
                        <tr>
                            <td style="background:#2f7d46; padding:28px 32px; color:#ffffff;">
                                <div style="font-size:14px; letter-spacing:1px; text-transform:uppercase;">RecipeHub</div>
                                <h1 style="margin:10px 0 0; font-size:28px; line-height:1.25;">Confirm your email</h1>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding:32px;">
                                <p style="margin:0 0 16px; font-size:16px; line-height:1.6;">Hi {safe_username},</p>
                                <p style="margin:0 0 24px; font-size:16px; line-height:1.6;">
                                    Welcome to RecipeHub. Confirm your email address to finish setting up your account and start exploring recipes.
                                </p>
                                <p style="margin:0 0 28px;">
                                    <a href="{safe_confirmation_url}" style="display:inline-block; background:#2f7d46; color:#ffffff; text-decoration:none; padding:14px 22px; border-radius:8px; font-weight:bold;">
                                        Confirm email
                                    </a>
                                </p>
                                <p style="margin:0 0 12px; font-size:14px; line-height:1.6; color:#5d6b61;">
                                    This link expires in 24 hours. If the button does not work, copy and paste this link into your browser:
                                </p>
                                <p style="margin:0; font-size:13px; line-height:1.6; word-break:break-all;">
                                    <a href="{safe_confirmation_url}" style="color:#2f7d46;">{safe_confirmation_url}</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    return text_body, html_body
