class Machine:
    def __init__(self, name, image_name, start_time, ip, username, password):
        self.name = name
        self.image_name = image_name
        self.start_time = start_time
        self.ip = ip
        self.username = username
        self.password = password

    def __str__(self):
        return f"Name: {self.name}\nImage name: {self.image_name}\nStart time: {self.start_time}\nIP: {self.ip}\nUsername: {self.username}\nPassword: {self.password}"

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

    def to_html_table(self):
        html = "<table>"
        html += """<th>Nazwa maszyny</th>
				<th>Obraz</th>
				<th>Czas uruchomienia</th>
                <th>IP uVPN</th>
				<th></th>"""
        for machine in self.machines:
            html += f"""<tr>
					<td>{ machine.name }</td>
					<td>{ machine.image_name }</td>
					<td>{ machine.start_time }</td>
                    <td>{ machine.ip }</td>
					<td><button onclick="ssh('{ machine.ip, machine.username, machine.password }')">SSH</button></td>
				</tr>"""
        html += "</table>"
        return html
