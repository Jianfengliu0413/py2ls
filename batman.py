import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import schedule
import time
from datetime import datetime
import os
from pprint import pp
import json


def extract_kv(
    dir_data="/Users/macjianfeng/Dropbox/github/python/py2ls/confidential_data/gmail_login.json",
    idx=0,
):  # select the index
    with open(dir_data, "r") as file:
        email_login = json.load(file)
    for i, (user, pd) in enumerate(email_login.items()):
        if i == idx:
            return user, pd


def email_to(**kwargs):
    """
    usage:
    email_to(who="example@gmail.com",
            subject="test",
            what="this is the body",
            attachments="/Users/test.pdf")
    Send an email with optional attachments.

    :param who: Recipient email address
    :param subject: Email subject
    :param what: Email what
    :param attachments: List of file paths to attach
    """
    who, what, subject = None, None, None
    attachments = False
    pause_sec = False  # default 10 seconds pause

    signature_styles = extract_kv(idx=1)[1]  # signature list
    signature = signature_styles[0]  # default signature,None
    verbose = True

    # params config
    for k, v in kwargs.items():
        if any(
            [
                "who" in k.lower(),
                "whe" in k.lower(),
                all(["@" in k.lower(), "." in k.lower()]),
            ]
        ):  # 'who' or "where"
            who = v
        if any(["sub" in k.lower(), "hea" in k.lower()]):  # 'subject', 'header'
            subject = v
        if any(
            ["wha" in k.lower(), "con" in k.lower(), "bod" in k.lower()]
        ):  # 'what','content','body'
            what = v
        if any(["att" in k.lower(), "fil" in k.lower()]):  # 'attachments', 'file'
            attachments = v  # optional
        if any(
            ["paus" in k.lower(), "tim" in k.lower(), "delay" in k.lower()]
        ):  # 'attachments', 'file'
            pause_sec = v  # optional
        if any(["sig" in k.lower()]):  # 'attachments', 'file'
            signature = v  # optional
            if not isinstance(v, str):
                print(signature_styles)
                signature = signature_styles[v]
        if any(["verb" in k.lower(), "show" in k.lower()]):  # 'verbose', 'show'
            verbose = v  # verbose

    # Create email message
    message = MIMEMultipart()
    message["From"] = extract_kv()[0]
    message["To"] = who
    message["Subject"] = subject

    # add signature
    if signature:
        what += f"\n\n{signature}\n"

    # the eamil's body
    message.attach(MIMEText(what, "plain"))

    # attach files
    if attachments:
        if isinstance(attachments, str):
            attachments = [attachments]
        for file in attachments:
            part = MIMEBase("application", "octet-stream")
            try:
                with open(file, "rb") as attachment:
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)

                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename= "{os.path.basename(file)}"',
                )
                message.attach(part)
            except FileNotFoundError:
                print(f"File not found: {file}")
            except Exception as e:
                print(f"Error attaching file {file}: {e}")
    if pause_sec:
        time.sleep(pause_sec)

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(extract_kv()[0], extract_kv()[1])
            server.sendmail(extract_kv()[0], who, message.as_string())
        if verbose:
            if attachments:
                print(
                    f'\nEmail successfully sent to:\nto:"{who}"\nsubject:{subject}\nattached:'
                )
                pp(attachments)
            else:
                print(f'\nEmail successfully sent to:\nto:"{who}"\nsubject:{subject}')
    except Exception as e:
        print(f"Failed to send email: {e}")


def email_to_every(who, subject, what, when, attachments=None):
    """
    Check the time and send an email when the time matches the when.

    :param who: Recipient email address
    :param subject: Email subject
    :param what: Email what
    :param when: Time to send the email in HH:MM format
    :param attachments: List of file paths to attach
    """
    current_time = datetime.now().strftime("%H:%M")
    if current_time == when:
        email_to(
            who=who,
            subject=subject,
            what=what,
            attachments=attachments,
        )


# Example usage
def example_job():
    # Example email details
    reminder_subject = "Reminder: Important Meeting Tomorrow"
    reminder_what = (
        "Don't forget about the meeting tomorrow at 10 AM in the conference room."
    )
    who = "Jianfeng.Liu0413@gmail.com"
    when = "14:30"  # Send time in 24-hour format

    # Optional attachments
    attachments = ["path/to/attachment1.pdf", "path/to/attachment2.jpg"]

    # Schedule the email
    email_to_every(who, reminder_subject, reminder_what, when, attachments)


if __name__ == "__main__":
    pass
    # # Schedule the job to run every minute
    # schedule.every(1).minutes.do(example_job)

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # # example2:
    # email_to(
    #     who="Jianfeng.Liu@medizin.uni-tuebingen.de",
    #     subj="test",
    #     wha="this is the body",
    #     signat="\n\n Best, Jianfeng\n",
    #     att="/Users/macjianfeng/Dropbox/Downloads/_*_doc-xlsx/20240822-preprints_full_20190101_20201031-2.xlsx",
    # )

    # # example3:
    # email_to(
    #     who="Jianfeng.Liu@medizin.uni-tuebingen.de",
    #     subj="test",
    #     wha="this is the test",
    #     signat=2,
    #     # att="/Users/macjianfeng/Dropbox/Downloads/_*_doc-xlsx/20240822-preprints_full_20190101_20201031-2.xlsx",
    # )

    # # example_4
    # print(extract_kv(idx=0))
    # print(extract_kv(idx=0)[0])
    # print(extract_kv(idx=1))
