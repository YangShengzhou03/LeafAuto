import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 邮箱信息
sender_email = '3555844679@qq.com'
receiver_email = 'yangsz03@foxmail.com'
smtp_server = 'smtp.qq.com'  # QQ邮箱的SMTP服务器地址
smtp_port = 465  # SMTP服务器端口号，默认为465

# 登录信息
username = '3555844679@qq.com'
password = 'xtibpzrdwnppchhi'  # 使用你生成的授权码

# 创建邮件内容
subject = 'Python SMTP 测试邮件'
body = '这是一封通过Python脚本发送的测试邮件。'

# 设置正确的 From 和 To 头部
sender_name = '发件人名字'  # 可以修改为你想要显示的名字
receiver_name = '收件人名字'  # 可以修改为你想要显示的名字

message = MIMEText(body, 'plain', 'utf-8')
message['From'] = 'ABC 3555844679@qq.com'
message['To'] = f"{Header(receiver_name, 'utf-8')} <{receiver_email}>"
message['Subject'] = Header(subject, 'utf-8')

try:
    # 发送邮件
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)  # 使用SSL加密连接
    server.login(username, password)
    server.sendmail(sender_email, [receiver_email], message.as_string())
    print("邮件发送成功")
except Exception as e:
    print(f"邮件发送失败: {e}")
finally:
    server.quit()