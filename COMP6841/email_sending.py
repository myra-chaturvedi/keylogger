import smtplib

sender = "Private Person <hello@demomailtrap.com>"
receiver = "A Test User <geniusmyra@gmail.com>"

message = f"""\
Subject: Hi Mailtrap
To: {receiver}
From: {sender}

This is a test e-mail message."""

with smtplib.SMTP("live.smtp.mailtrap.io", 587) as server:
    server.starttls()
    server.login("api", "135c408123864db529258d292639635a")
    server.sendmail(sender, receiver, message)