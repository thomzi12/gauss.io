import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# This function takes in a list of a dict that
# map's students emails to a list of videos
def sendEmail(studentName, studentEmail, urlList):
	teacherEmail = '<teacheremail>'

	student = studentName

	fromaddr = teacherEmail
	toaddr = studentEmail
	msg = MIMEMultipart('alternative')
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = "Khan Academy Videos"

	headerText = """
	<div style="background-color: RGBA(53, 58, 64, 1.00); font-family: -apple-system-headline, -apple-system-body, sans-serif;">
		<div style="width: 640px; margin-left: auto; margin-right: auto; background-color: RGBA(249, 249, 249, 1.00); padding: 10px 20px;">
				<div>
					<img style="width: 100%;" src="https://thumbs.dreamstime.com/t/banner-gold-trophy-cup-vector-16935592.jpg">
				</div>
				<h1 style="text-align: center; font-family: -apple-system-headline, -apple-system-body, sans-serif;">Good job on the exam, """ + student + """!</h1>
				Here are the recommended videos based on your previous test score from Khan Academy:"""
	linksText = "<ul>"
	for url in urlList:
		linksText = linksText + '<li>' + url + '</li>'
	linksText = linksText + """</ul>
		<div>
		<p style="text-align: center;"><strong>Gauss.io</strong></p>
		</div>
		</div>
	</div>"""

	html = headerText + linksText

	# part1 = MIMEText(text, 'plain')
	part2 = MIMEText(html, 'html')

	# msg.attach(part1)
	msg.attach(part2)

	try:
	   smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
	   smtpObj.ehlo()
	   smtpObj.starttls()
	   smtpObj.login(teacherEmail, '<login>')
	   text = msg.as_string()
	   smtpObj.sendmail(fromaddr, toaddr, text)
	   smtpObj.close()
	   print("Successfully sent email")
	except smtplib.SMTPException:
	   print("Error: unable to send email")

# if __name__ == '__main__':
# 	studentName = 'Alexis'
# 	studentEmail = '<email'
# 	urlList = ['url1', 'url2', 'url3']
# 	sendEmail(studentName, studentEmail, urlList)
