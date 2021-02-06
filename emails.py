import os
import smtplib


def sendEmails(to_email: str,
               otp: int):
    conn = smtplib.SMTP('imap.gmail.com', 587)
    conn.ehlo()
    conn.starttls()
    conn.login(os.getenv('login_id'), os.getenv('password'))
    conn.sendmail(os.getenv('login_id'),
                  to_email,
                  'Subject: OTP for login'
                  f"\n\n\n\nmsg: OTP if {otp} valid for xyz mins")
    conn.quit()

