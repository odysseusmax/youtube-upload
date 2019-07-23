import httplib2, http, asyncio
from apiclient.http import MediaFileUpload

class MaxRetryExceeded(Exception):
    pass
class UploadFailed(Exception):
    pass

class Youtube:

    MAX_RETRIES = 10

    RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError,
                        http.client.NotConnected,
                        http.client.IncompleteRead,
                        http.client.ImproperConnectionState,
                        http.client.CannotSendRequest,
                        http.client.CannotSendHeader,
                        http.client.ResponseNotReady,
                        http.client.BadStatusLine)

    RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

    def __init__(self, auth, video, properties, chunksize=1024*1024):
        self.youtube = auth
        self.request = None
        self.chunksize = chunksize
        self.response = None
        self.error = None
        self.retry = 0
        self.video = video
        self.properties = properties



    async def upload_video(self, progress=None, *arg):
        self.progress = progress
        self.arg = arg
        body = dict(
            snippet=dict(
                title = self.properties.get('title'),
                description = self.properties.get('description'),
                tags = self.properties.get('tags'),
                categoryId = self.properties.get('category')
            ),
            status=dict(
                privacyStatus=self.properties.get('privacyStatus')
            )
        )
        self.request = self.youtube.videos().insert(body = body,
            media_body = MediaFileUpload(self.video,
                chunksize = self.chunksize,
                resumable = True,
            ),
            part = ','.join(body.keys())
        )
        self.method = "insert"
        await self._resumable_upload()
        return self.response

    async def _resumable_upload(self):

        cur = 0

        while self.response is None:
            try:
                #print("Uploading the file...")
                status, self.response = self.request.next_chunk()
                cur+=1

                if(self.progress):
                    await self.progress(cur*self.chunksize, os.path.getsize(self.video), *self.args)

                if self.response is not None:
                    if self.method == 'insert' and 'id' in self.response:
                        await print_response(self.response)
                    elif self.method != 'insert' or 'id' not in self.response:
                        await print_response(self.response)
                    else:
                        raise UploadFailed("The file upload failed with an unexpected response:{}".format(self.response))
            except HttpError as e:
                if e.resp.status in self.RETRIABLE_STATUS_CODES:
                    self.error = "A retriable HTTP error {} occurred:\n {}".format(e.resp.status, e.content)
                else:
                    raise
            except self.RETRIABLE_EXCEPTIONS as e:
                self.error = "A retriable error occurred: {}".format(e)

            if self.error is not None:
                print(self.error)
                self.retry += 1

                if self.retry > self.MAX_RETRIES:
                    raise MaxRetryExceeded("No longer attempting to retry.")

                max_sleep = 2 ** self.retry
                sleep_seconds = random.random() * max_sleep

                print("Sleeping {} seconds and then retrying...".format(sleep_seconds))
                asyncio.sleep(sleep_seconds)


async def print_response(response):
    for key, value in response.items():
        print(key, " : ", value, '\n\n')
