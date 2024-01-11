from langchain_core.runnables import Runnable


class UserInputRunnable(Runnable):
    def __init__(self):
        self.user_input = None

    def invoke(self, input, config=None):
        return {"user_input": self.user_input}

    def set_user_input(self, user_input):
        self.user_input = user_input