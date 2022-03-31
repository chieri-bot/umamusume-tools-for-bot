
class UmaNotFound(Exception):
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return str(self.info)

    def __repr__(self):
        return self.__str__()


class SkillNotFound(Exception):
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return str(self.info)

    def __repr__(self):
        return self.__str__()


class EventNotFound(Exception):
    def __init__(self, info: str):
        self.info = info

    def __str__(self):
        return str(self.info)

    def __repr__(self):
        return self.__str__()
