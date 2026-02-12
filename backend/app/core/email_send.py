import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from typing import Any
from app.utils.config import ENV_PROJECT
import traceback


async def send_approval_email(user, thread_id: str, reference_no: str):
    try:
        html_content = f"""
<div style="background-color:#f3f4f6; padding:40px 0; text-align:center; font-family:Arial, sans-serif;">
  <!-- Outer wrapper -->
  <center>
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="max-width:600px; margin:0 auto;">
      <!-- Logo Row -->
      <tr>
        <td align="center" style="padding-bottom:20px;">
          <img src="https://via.placeholder.com/120x60.png?text=Logo" alt="Logo" style="display:block; max-width:120px; height:auto;">
        </td>
      </tr>

      <!-- Card Row -->
      <tr>
        <td align="center" style="padding:0 20px;">
          <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" 
            style="background-color:#ffffff; border-radius:16px; box-shadow:0 4px 8px rgba(0,0,0,0.1); 
                   padding:30px; box-sizing:border-box; max-width:500px; margin:0 auto;">
            <tr>
              <td style="text-align:left; color:#1e3a8a; font-size:18px; font-weight:bold; padding-bottom:20px;">
                Loan Application Details
              </td>
            </tr>
            <tr>
              <td style="text-align:left; font-size:14px; color:#000000;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size:14px;">
                  <tr><td style="font-weight:bold;width:40%;padding:5px 0;">Name:</td><td>{user.name}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Mobile:</td><td>{user.phone_number}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Email:</td>
                      <td><a href=`mailto:{user.email_id}` style="color:#1d4ed8;text-decoration:none;">{user.email_id}</a></td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Employment Type:</td><td>{user.employment_type}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Address:</td><td>{user.user_address}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Clinic:</td><td>{user.treatment_location}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Pincode:</td><td>{user.pincode}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">State:</td><td>{user.state}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">PAN:</td><td>{user.pan_number}</td></tr>
                  <tr><td style="font-weight:bold;padding:5px 0;">Aadhar:</td><td>{user.aadhar_number}</td></tr>
                </table>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </center>
</div>



        """

        message = MIMEMultipart("alternative")
        message["From"] = ENV_PROJECT.ADMIN_EMAIL_ID
        message["To"] = ENV_PROJECT.ADMIN_EMAIL_TO
        message["Subject"] = (
            f"Loan Request Raised by [{thread_id}] with [{reference_no}]"
        )
        message.attach(MIMEText(html_content, "html"))

        await aiosmtplib.send(
            message,
            hostname="smtp.office365.com",
            port=587,
            start_tls=True,
            username=ENV_PROJECT.ADMIN_EMAIL_ID,
            password=ENV_PROJECT.MAIL_PASSWORD,
        )
    except Exception as e:
        traceback.print_exc()
