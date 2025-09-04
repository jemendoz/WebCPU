import reflex as rx


class State(rx.State):
    upload_text: str = ""
    progmem: list[str] = []
    pc: int = 0
    ir: str = ""
    reg: dict[str, str] = {"A": 0, "B": 0, "C": 0, "TEST": "="}
    mem: dict[str, str] = {}
    state: str = "halt"

    @rx.event
    def file_drop(self, data):
        print(data)

    @rx.event
    async def upload_progmem(self, files: list[rx.UploadFile]):
        self.cpu_reset()
        file = files[0]
        if file.headers.get("content-type") != "text/plain":
            return
        data = await file.read()
        lines = data.decode().split("\n")
        while "" in lines:
            lines.remove("")
        self.progmem = []
        for line in lines:
            self.progmem.append(line)
        self.state = "running"

    @rx.event
    def submit_progmem(self, data: dict):
        self.cpu_reset()
        lines = data["text_area"].split("\n")
        while "" in lines:
            lines.remove("")
        self.progmem = []
        for line in lines:
            self.progmem.append(line)
        self.state = "running"

    @rx.event
    def cpu_reset(self):
        self.progmem = []
        self.pc = 0
        self.ir = ""
        self.reg = {"A": "0", "B": "0", "C": "0", "TEST": "="}
        self.mem = {}
        self.state = "halt"

    @rx.event
    def cpu_wipe_progmem(self):
        self.progmem = []

    @rx.event
    def cpu_load(self):
        self.ir = self.progmem[self.pc]

    @rx.event
    def cpu_increment(self):
        self.pc += 1

    @rx.event
    def cpu_execute(self):
        parts = self.ir.split(" ")

        match parts[0]:
            case "LOADA":
                try:
                    self.reg["A"] = self.mem[parts[1]]
                except KeyError:
                    raise (IndexError("La direccion de memoria no existe / no esta inicializada"))

            case "LOADB":
                try:
                    self.reg["B"] = self.mem[parts[1]]
                except KeyError:
                    raise (IndexError("La direccion de memoria no existe / no esta inicializada"))

            case "LOADC":
                try:
                    self.reg["C"] = self.mem[parts[1]]
                except KeyError:
                    raise (IndexError("La direccion de memoria no existe / no esta inicializada"))

            case "CONA":
                self.reg["A"] = parts[1]

            case "CONB":
                self.reg["B"] = parts[1]

            case "CONC":
                self.reg["C"] = parts[1]

            case "SAVEA":
                self.mem[parts[1]] = self.reg["A"]

            case "SAVEB":
                self.mem[parts[1]] = self.reg["B"]

            case "SAVEC":
                self.mem[parts[1]] = self.reg["C"]

            case "ADD":
                self.reg["C"] = str(int(self.reg["A"]) + int(self.reg["B"]))

            case "SUB":
                self.reg["C"] = str(int(self.reg["A"]) - int(self.reg["B"]))

            case "MUL":
                self.reg["C"] = str(int(self.reg["A"]) * int(self.reg["B"]))

            case "DIV":
                self.reg["C"] = str(int(self.reg["A"]) // int(self.reg["B"]))

            case "MOD":
                self.reg["C"] = str(int(self.reg["A"]) % int(self.reg["B"]))

            case "COM":
                if int(self.reg["A"]) < int(self.reg["B"]):
                    self.reg["TEST"] = "<"
                elif int(self.reg["A"]) > int(self.reg["B"]):
                    self.reg["TEST"] = ">"
                else:
                    self.reg["TEST"] = "="

            case "JUMP":
                self.pc = int(parts[1])

            case "JEQ":
                if self.reg["TEST"] == "=":
                    self.pc = int(parts[1])

            case "JNEQ":
                if self.reg["TEST"] != "=":
                    self.pc = int(parts[1])

            case "JG":
                if self.reg["TEST"] == ">":
                    self.pc = int(parts[1])

            case "JGE":
                if self.reg["TEST"] == ">" or self.reg["TEST"] == "=":
                    self.pc = int(parts[1])

            case "JL":
                if self.reg["TEST"] == "<":
                    self.pc = int(parts[1])

            case "JLE":
                if self.reg["TEST"] == "<" or self.reg["TEST"] == "=":
                    self.pc = int(parts[1])

            case "STOP":
                self.state = "halt"

            case _:
                raise (ValueError(f"Instruccion ({parts[0]}) no admitida."))

    @rx.event
    def cpu_step(self):
        if self.state == "running":
            self.cpu_load()
            self.cpu_increment()
            self.cpu_execute()

    @rx.event
    def cpu_run(self):
        while self.state == "running":
            self.cpu_step()


def print_progmem() -> rx.Component:
    return rx.vstack(
        rx.foreach(
            State.progmem,
            lambda line, i: rx.text(
                f"{i}: ",
                rx.cond(State.pc == i, rx.code(line, variant="solid"), rx.code(line, variant="outline"))
            )
        ),
    )


def print_registers() -> rx.Component:
    return rx.scroll_area(
        rx.vstack(
            rx.heading("Registros"),
            rx.separator(),
            rx.text(f"Estado: {State.state}"),
            rx.text(f"IR: {State.ir}"),
            rx.text(f"PC: {State.pc}"),
            rx.text(f"Reg A: {State.reg['A']}"),
            rx.text(f"Reg B: {State.reg['B']}"),
            rx.text(f"Reg C: {State.reg['C']}"),
            rx.text(f"Reg TEST: {State.reg['TEST']}"),

        ),
        scrollbars="both",
        type="auto"
    )


def print_memory() -> rx.Component:
    return rx.scroll_area(
        rx.vstack(
            rx.heading("Memoria"),
            rx.separator(),
            rx.foreach(
                State.mem,
                lambda elem: rx.text(f"Address {elem.to("list")[0]}: {elem.to("list")[1]}")
            )
        ),
        scrollbars="vertical",
        type="auto"
    )


def index():
    return rx.container(
        rx.flex(
            rx.card(
                rx.scroll_area(
                    rx.vstack(
                        rx.heading("Programa"),
                        rx.separator(),
                        print_progmem(),
                        spacing="2"
                    ),
                    scrollbars="both",
                    type="auto"
                ),
                height="80vh",
                width="20vw"
            ),
            rx.flex(
                rx.card(
                    print_registers(),
                    height="38vh",
                    width="100%"
                ),
                rx.card(
                    print_memory(),
                    height="41vh",
                    width="100%"
                ),
                height="80%",
                width="20vw",
                spacing="2",
                direction="column"
            ),
            rx.flex(
                rx.card(
                    rx.form(
                        rx.vstack(
                            rx.heading("Escribir programa"),
                            rx.separator(),
                            rx.text_area(name="text_area", resize="vertical", max_height="40vh"),
                            rx.button("Submit", type="submit"),
                            spacing="2"
                        ),
                        on_submit=State.submit_progmem
                    ),
                    height="59vh",
                    width="100%"
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Subir programa"),
                        rx.separator(),
                        rx.upload(rx.text("Buscar archivo"), id="upload", padding="0.5em", multiple=False),
                        rx.button("Subir", on_click=State.upload_progmem(rx.upload_files("upload")))
                    ),
                    width="100%"
                ),
                direction="column",
                spacing="2",
                width="20vw"
            ),
            rx.flex(
                rx.card(
                    rx.vstack(
                        rx.button("Cargar", on_click=State.cpu_load, width="100%"),
                        rx.button("Incrementar", on_click=State.cpu_increment, width="100%"),
                        rx.button("Ejecutar", on_click=State.cpu_execute, width="100%"),
                        rx.button("Paso", on_click=State.cpu_step, width="100%"),
                        rx.button("Correr", on_click=State.cpu_run, width="100%"),
                        rx.button("Reiniciar", on_click=State.cpu_reset, width="100%"),
                        spacing="3"
                    ),
                ),
                direction="column"
            ),
            direction="row",
            spacing="3",
            justify="center",
            align="start"
        ),
        height="100vh",
        width="100wh"
    )


app = rx.App()
app.add_page(index, title="Inicio")
