class RequestsData:
    data: dict | None = None

    def __init__(self, UserID: int, args: dict = {}):
        self.data = {
            'UserID': UserID
        }
        self.data.update(args)
