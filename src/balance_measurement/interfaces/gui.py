"""Optional Tkinter GUI with RS232 operations isolated in a background thread."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from balance_measurement.acquisition import AcquisitionSession, AcquisitionSettings
from balance_measurement.scale.client import ScaleClient
from balance_measurement.scale.protocols import default_registry
from balance_measurement.storage import default_recorder_registry
from balance_measurement.scale.transport import SerialSettings, SerialTransport


class AcquisitionWindow:
    """All Tkinter interactions run on the main thread, never from the worker."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        root.title("Balance Measurement")
        self.port = tk.StringVar(value="COM3")
        self.baudrate = tk.StringVar(value="9600")
        self.protocol = tk.StringVar(value="mettler-toledo")
        self.interval = tk.StringVar(value="1.0")
        self.output = tk.StringVar(value="measurements.csv")
        self.status = tk.StringVar(value="Idle")
        self.messages: queue.Queue[tuple[str, str]] = queue.Queue()
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None
        self._closing = False
        grid = ttk.Frame(root, padding=12)
        grid.pack(fill="both", expand=True)
        fields = (
            ("Serial port", self.port), ("Baud rate", self.baudrate),
            ("Protocol", self.protocol), ("Interval (s)", self.interval),
            ("Output file", self.output),
        )
        for row, (name, variable) in enumerate(fields):
            ttk.Label(grid, text=name).grid(row=row, column=0, sticky="w", pady=3)
            if name == "Protocol":
                ttk.Combobox(grid, textvariable=variable, values=default_registry().names(),
                             state="readonly").grid(row=row, column=1, sticky="ew")
            else:
                ttk.Entry(grid, textvariable=variable, width=35).grid(
                    row=row, column=1, sticky="ew"
                )
        ttk.Button(grid, text="Browse…", command=self.browse).grid(row=4, column=2)
        self.start_button = ttk.Button(grid, text="Start", command=self.start)
        self.start_button.grid(row=5, column=0, pady=8)
        ttk.Button(grid, text="Stop", command=self.stop).grid(row=5, column=1, sticky="w")
        ttk.Label(grid, textvariable=self.status).grid(row=6, column=0, columnspan=3, sticky="w")
        self.log = tk.Text(grid, height=12, width=65, state="disabled")
        self.log.grid(row=7, column=0, columnspan=3, sticky="nsew")
        grid.columnconfigure(1, weight=1)
        grid.rowconfigure(7, weight=1)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.after(100, self._poll)

    def browse(self) -> None:
        selected = filedialog.asksaveasfilename(defaultextension=".csv")
        if selected:
            self.output.set(selected)

    def start(self) -> None:
        if self.worker is not None and self.worker.is_alive():
            return
        try:
            settings = SerialSettings(port=self.port.get(), baudrate=int(self.baudrate.get()))
            acquisition = AcquisitionSettings(
                count=None, interval_seconds=float(self.interval.get())
            )
            protocol = default_registry().create(self.protocol.get())
            output = Path(self.output.get())
            if not str(output).strip():
                raise ValueError("Please select an output file")
            recorder = default_recorder_registry().create(output)
        except Exception as exc:
            messagebox.showerror("Invalid settings", str(exc))
            return
        self.stop_event.clear()
        self.start_button.configure(state="disabled")
        self.status.set("Acquiring…")

        def acquire() -> None:
            client = ScaleClient(SerialTransport(settings), protocol)
            session = AcquisitionSession(client, [recorder], acquisition)
            try:
                with session:
                    for measurement in session.collect(stop_event=self.stop_event):
                        if measurement is not None:
                            self.messages.put(("reading", f"{measurement.value} {measurement.unit} "
                                                           f"stable={measurement.stable}"))
            except Exception as exc:
                self.messages.put(("error", str(exc)))
            finally:
                self.messages.put(("stopped", "Acquisition stopped"))

        self.worker = threading.Thread(target=acquire, daemon=True)
        self.worker.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.status.set("Stopping…")

    def _poll(self) -> None:
        while True:
            try:
                kind, message = self.messages.get_nowait()
            except queue.Empty:
                break
            if kind == "stopped":
                self.start_button.configure(state="normal")
                self.status.set(message)
            elif kind == "error":
                self.status.set(f"Error: {message}")
            self.log.configure(state="normal")
            self.log.insert("end", message + "\n")
            self.log.see("end")
            self.log.configure(state="disabled")
        if self._closing and (self.worker is None or not self.worker.is_alive()):
            self.root.destroy()
            return
        self.root.after(100, self._poll)

    def close(self) -> None:
        self._closing = True
        self.stop()


def run_gui() -> None:
    root = tk.Tk()
    AcquisitionWindow(root)
    root.mainloop()
