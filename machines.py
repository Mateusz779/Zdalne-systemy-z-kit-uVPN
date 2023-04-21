class Machine:
    def __init__(self, name, image_name, start_time, ipvpn, iplocal, username, password):
        self.name = name
        self.image_name = image_name
        self.start_time = start_time
        self.ipvpn = ipvpn
        self.iplocal = iplocal
        self.username = username
        self.password = password


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
