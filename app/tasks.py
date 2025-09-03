from celery import shared_task
from email.mime.text import MIMEText
from email.utils import formataddr
from smtplib import SMTP
from pathlib import Path
import environ
from app import randomX

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")

# Document for send email: https://mailtrap.io/blog/python-send-email/

@shared_task
def send_otp(receiver):
    otp_code = randomX.randomOTP()
    subject = 'Mã OTP của bạn từ TestMarkDB'
    body = f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Xác thực OTP</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f7;
                margin: 0;
                padding: 0;
                color: #333333;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background-color: #4682A9;
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 30px 20px;
                line-height: 1.6;
            }}
            .otp-code {{
                display: block;
                width: fit-content;
                margin: 20px auto;
                font-size: 28px;
                font-weight: bold;
                color: #4682A9;
                background-color: #f1f1f1;
                padding: 10px 20px;
                border-radius: 6px;
                text-align: center;
                letter-spacing: 4px;
            }}
            .footer {{
                padding: 20px;
                text-align: center;
                font-size: 14px;
                color: #777777;
                background-color: #f4f4f7;
            }}
        </style>
        </head>
        <body>
            <div class="container">
                <div class="header">Xác thực OTP</div>
                <div class="content">
                    <p>Xin chào,</p>
                    <p>Mã OTP của bạn để xác thực là:</p>
                    <span class="otp-code">{otp_code}</span>
                    <p>Mã này có hiệu lực trong <strong>5 phút</strong>. Vui lòng không chia sẻ mã này với bất kỳ ai để bảo vệ tài khoản của bạn.</p>
                    <p>Nếu bạn không thực hiện yêu cầu này, vui lòng bỏ qua email này hoặc liên hệ với chúng tôi ngay lập tức.</p>
                    <p>Trân trọng,
                </div>
                <div class="footer">
                    &copy; 2025 TestMarkDB
                </div>
            </div>
        </body>
        </html>
        """
    message = MIMEText(body, "html")
    message["From"] = formataddr((env("SENDER_NAME"), env("SENDER_EMAIL")))
    message["To"] = receiver
    message["Subject"] = subject

    with SMTP(host=env("SMTP_SERVER"), port=env("SMTP_PORT")) as smtp:
        smtp.starttls()
        smtp.login(env("SMTP_USERNAME"), env("SMTP_PASSWORD"))
        smtp.send_message(message)

    print("Email đã gửi thành công!")