class User:
    def __init__(self, fullname, time, vol_id, user_photo, chat_id, language, sheet_id, all_data, sheet_name):
        self._fullname = fullname
        self._time = time
        self._vol_id = vol_id
        self._user_photo = user_photo
        self._chat_id = chat_id
        self._language = language
        self._sheet_id = sheet_id
        self._all_data = all_data
        self._sheet_name = sheet_name

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

    def get_language(self):
        return self._language

    def get_sheet_id(self):
        return self._sheet_id

    def get_datas(self):
        return self._all_data

    def get_sheet_name(self):
        return self._sheet_name
