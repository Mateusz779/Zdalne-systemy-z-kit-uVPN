class Machine:
    def __init__(self, name, image_name, start_time, ipvpn, iplocal, username, password):
        self.name = name
        self.image_name = image_name
        self.start_time = start_time
        self.ipvpn = ipvpn
        self.iplocal = iplocal
        self.username = username
        self.password = password


    def __str__(self):
        return f"Name: {self.name}\nImage name: {self.image_name}\nStart time: {self.start_time}\nIP VPN: {self.ipvpn}\nIP local: {self.iplocal}\nUsername: {self.username}\nPassword: {self.password}"

class MachineManager:
    def __init__(self):
        self.machines = []

    def add_machine(self, machine):
        self.machines.append(machine)

    def remove_machine(self, machine):
        self.machines.remove(machine)

    def get_machine_by_name(self, name):
        for machine in self.machines:
            if machine.name == name:
                return machine
        return None

    def __str__(self):
        result = ""
        for machine in self.machines:
            result += str(machine) + "\n\n"
        return result
