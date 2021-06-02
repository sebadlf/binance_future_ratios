from threading import Thread

class MachineState:

    def check_status(self):
        pass

    def call_api(self):
        pass

    def save(self):
        pass

    def work(self):
        self.check_status()
        self.call_api()
        self.save()