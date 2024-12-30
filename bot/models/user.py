class User:
    def __init__(self, fullname, time, vol_id, user_photo, chat_id):
        self._fullname = fullname
        self._time = time
        self._vol_id = vol_id
        self._user_photo = user_photo
        self._chat_id = chat_id

    def get_fullname(self):
        return self._fullname

    def get_time(self):
        return self._time

    def get_vol_id(self):
        return self._vol_id

    def get_user_photo(self):
        return self._user_photo

    def get_chat_id(self):
        return self._chat_id
