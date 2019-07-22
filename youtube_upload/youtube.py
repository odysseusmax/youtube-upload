import httplib2, http

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

    def __init__(self, auth, chunksize=1024*1024):
        self.youtube = auth
        self.request = None
        self.chunksize = chunksize
        self.response = None
        self.error = None
        self.retry = 0



    def upload_video(self, video, properties):

        body = dict(
            snippet=dict(
                title = properties.get('title'),
                description = properties.get('description'),
                tags = properties.get('tags'),
                categoryId = properties.get('category')
            ),
            status=dict(
                privacyStatus=properties.get('privacyStatus')
            )
        )
        self.request = self.youtube.videos().insert(body = body,
            media_body = MediaFileUpload(video,
                chunksize = chunksize,
                resumable = True,
            ),
            part = ','.join(body.keys())
        )
        self.method = "insert"
        self._resumable_upload()
        return self.response

    def _resumable_upload(self):
        while self.response is None:
            try:
                print("Uploading the file...")
                status, self.response = self.request.next_chunk()

                if self.response is not None:
                    if self.method == 'insert' and 'id' in self.response:
                        print_response(self.response)
                    elif self.method != 'insert' or 'id' not in self.response:
                        print_response(self.response)
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
                time.sleep(sleep_seconds)


def print_response(response):
    for key, value in response.items():
        print(key, " : ", value, '\n\n')
