from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from panel_model import PanelParams, simulate_panel


class PanelApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title('Modelo del Panel Solar')
        self.geometry('1180x720')
        self.minsize(1050, 650)

        self.vars: dict[str, tk.StringVar] = {}
        self.result_vars: dict[str, tk.StringVar] = {}

        self._build_ui()
        self.simulate()

    def _add_input(self, parent: ttk.Frame, row: int, label: str, key: str, value: str, unit: str = '') -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', padx=6, pady=4)
        var = tk.StringVar(value=value)
        self.vars[key] = var
        entry = ttk.Entry(parent, textvariable=var, width=12)
        entry.grid(row=row, column=1, sticky='ew', padx=6, pady=4)
        ttk.Label(parent, text=unit).grid(row=row, column=2, sticky='w', padx=2, pady=4)
        entry.bind('<Return>', lambda _event: self.simulate())
        entry.bind('<FocusOut>', lambda _event: self.simulate())

    def _add_result(self, parent: ttk.Frame, row: int, label: str, key: str, unit: str = '') -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', padx=6, pady=4)
        var = tk.StringVar(value='—')
        self.result_vars[key] = var
        ttk.Label(parent, textvariable=var, font=('Segoe UI', 10, 'bold')).grid(row=row, column=1, sticky='e', padx=6, pady=4)
        ttk.Label(parent, text=unit).grid(row=row, column=2, sticky='w', padx=2, pady=4)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=10)
        root.pack(fill='both', expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        left = ttk.Frame(root)
        left.grid(row=0, column=0, sticky='nsw', padx=(0, 12))

        env = ttk.LabelFrame(left, text='Condiciones ambientales', padding=8)
        env.pack(fill='x', pady=(0, 10))
        env.columnconfigure(1, weight=1)
        self._add_input(env, 0, 'Temperatura', 'temperature_c', '25', '°C')
        self._add_input(env, 1, 'Irradiancia S', 'irradiance', '1000', 'W/m²')

        panel = ttk.LabelFrame(left, text='Datos del panel / arreglo', padding=8)
        panel.pack(fill='x', pady=(0, 10))
        panel.columnconfigure(1, weight=1)
        self._add_input(panel, 0, 'Ns celdas serie', 'ns', '36')
        self._add_input(panel, 1, 'Np paralelo', 'np_parallel', '1')
        self._add_input(panel, 2, 'Voc', 'voc_ref', '22.41', 'V')
        self._add_input(panel, 3, 'Isc', 'isc_ref', '9.67', 'A')
        self._add_input(panel, 4, 'KVoc', 'kvoc', '-0.08', 'V/°C')
        self._add_input(panel, 5, 'KIsc', 'kisc_percent', '0.1', '%/°C')

        buttons = ttk.Frame(left)
        buttons.pack(fill='x', pady=(0, 10))
        ttk.Button(buttons, text='Simular', command=self.simulate).pack(side='left', fill='x', expand=True)
        ttk.Button(buttons, text='Valores LabVIEW', command=self.reset_defaults).pack(side='left', fill='x', expand=True, padx=(8, 0))

        results = ttk.LabelFrame(left, text='Resultados', padding=8)
        results.pack(fill='x')
        results.columnconfigure(1, weight=1)
        self._add_result(results, 0, 'Voc corregido', 'voc', 'V')
        self._add_result(results, 1, 'Isc corregida', 'isc', 'A')
        self._add_result(results, 2, 'Pmax', 'pmax', 'W')
        self._add_result(results, 3, 'Vmax / Vmp', 'vmp', 'V')
        self._add_result(results, 4, 'Imax / Imp', 'imp', 'A')
        self._add_result(results, 5, 'Ropt', 'ropt', 'Ω')
        self._add_result(results, 6, 'Iph', 'iph', 'A')
        self._add_result(results, 7, 'Io', 'io', 'A')

        right = ttk.Frame(root)
        right.grid(row=0, column=1, sticky='nsew')
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax_iv = self.fig.add_subplot(211)
        self.ax_pv = self.fig.add_subplot(212)
        self.fig.tight_layout(pad=3.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        note = ttk.Label(
            right,
            text='Modelo: I = Np·Iph - Np·Io·(exp(qV / (k·T·A·Ns)) - 1).  Rsh alta y Rs baja.',
            foreground='#555555',
        )
        note.grid(row=1, column=0, sticky='ew', pady=(8, 0))

    def reset_defaults(self) -> None:
        defaults = {
            'temperature_c': '25',
            'irradiance': '1000',
            'ns': '36',
            'np_parallel': '1',
            'voc_ref': '22.41',
            'isc_ref': '9.67',
            'kvoc': '-0.08',
            'kisc_percent': '0.1',
        }
        for key, value in defaults.items():
            self.vars[key].set(value)
        self.simulate()

    def _params_from_ui(self) -> PanelParams:
        def f(key: str) -> float:
            return float(self.vars[key].get().replace(',', '.'))

        def i(key: str) -> int:
            return int(float(self.vars[key].get().replace(',', '.')))

        return PanelParams(
            temperature_c=f('temperature_c'),
            irradiance=f('irradiance'),
            ns=i('ns'),
            np_parallel=i('np_parallel'),
            voc_ref=f('voc_ref'),
            isc_ref=f('isc_ref'),
            kvoc=f('kvoc'),
            kisc_percent=f('kisc_percent'),
            diode_ideality=2.0,
        )

    def simulate(self) -> None:
        try:
            params = self._params_from_ui()
            result = simulate_panel(params)
        except Exception as exc:
            messagebox.showerror('Datos inválidos', f'Revisa los valores de entrada.\n\n{exc}')
            return

        self.result_vars['voc'].set(f'{result.voc:.2f}')
        self.result_vars['isc'].set(f'{result.isc:.2f}')
        self.result_vars['pmax'].set(f'{result.pmax:.2f}')
        self.result_vars['vmp'].set(f'{result.vmp:.2f}')
        self.result_vars['imp'].set(f'{result.imp:.2f}')
        self.result_vars['ropt'].set(f'{result.ropt:.2f}')
        self.result_vars['iph'].set(f'{result.iph:.2f}')
        self.result_vars['io'].set(f'{result.io:.3e}')

        self.ax_iv.clear()
        self.ax_iv.plot(result.voltage, result.current, color='#0066cc', linewidth=2)
        self.ax_iv.scatter([result.vmp], [result.imp], color='red', zorder=3, label='Pmax')
        self.ax_iv.set_title('Curva Voltaje - Corriente')
        self.ax_iv.set_xlabel('Voltaje [V]')
        self.ax_iv.set_ylabel('Corriente [A]')
        self.ax_iv.grid(True, alpha=0.3)
        self.ax_iv.legend(loc='best')

        self.ax_pv.clear()
        self.ax_pv.plot(result.voltage, result.power, color='#f28c28', linewidth=2)
        self.ax_pv.scatter([result.vmp], [result.pmax], color='red', zorder=3, label=f'Pmax {result.pmax:.2f} W')
        self.ax_pv.set_title('Curva Voltaje - Potencia')
        self.ax_pv.set_xlabel('Voltaje [V]')
        self.ax_pv.set_ylabel('Potencia [W]')
        self.ax_pv.grid(True, alpha=0.3)
        self.ax_pv.legend(loc='best')

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw_idle()


if __name__ == '__main__':
    PanelApp().mainloop()
