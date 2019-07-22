from youtube_upload.auth import GoogleAuth, NoCredentialFile
from youtube_upload.youtube import Youtube

gauth = GoogleAuth()

try:
    gauth.LoadCredentialsFile('test.txt')
except NoCredentialFile:
    url = gauth.GetAuthUrl()

    print(url)

    code = str(input("enter code"))

    gauth.Auth(code)

auth = gauth.authorize()

gauth.SaveCredentialsFile('test.txt')

youtube = Youtube(auth)

options = {
            'category': '27',
            'description': 'Sample Leran ABC Video',
            'tags': '',
            'title': 'Sample Test video upload',
            'privacyStatus': 'private',
        }

r = youtube.upload_video('test.mp4', options)
