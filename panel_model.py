from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

Q_ELECTRON = 1.602176634e-19
K_BOLTZMANN = 1.380649e-23
T_REF_C = 25.0
S_REF = 1000.0


@dataclass
class PanelParams:
    temperature_c: float = 25.0
    irradiance: float = 1000.0
    ns: int = 36
    np_parallel: int = 1
    voc_ref: float = 22.41
    isc_ref: float = 9.67
    kvoc: float = -0.08  # V/°C, coeficiente del panel completo
    kisc_percent: float = 0.1  # %/°C
    diode_ideality: float = 2.0
    points: int = 300


@dataclass
class PanelResult:
    voltage: np.ndarray
    current: np.ndarray
    power: np.ndarray
    voc: float
    isc: float
    pmax: float
    vmp: float
    imp: float
    ropt: float
    iph: float
    io: float


def corrected_isc(params: PanelParams) -> float:
    irradiance_factor = max(params.irradiance, 0.0) / S_REF
    temp_factor = 1.0 + (params.kisc_percent / 100.0) * (params.temperature_c - T_REF_C)
    return max(0.0, params.isc_ref * irradiance_factor * temp_factor * max(params.np_parallel, 1))


def corrected_voc(params: PanelParams) -> float:
    # El PDF/LabVIEW usa KVoc como coeficiente negativo de voltaje por °C.
    voc_temp = params.voc_ref + params.kvoc * (params.temperature_c - T_REF_C)

    # Aproximación física para irradiancia: Voc cambia logarítmicamente con S.
    # A S=1000 W/m² no altera el valor de referencia.
    irradiance = max(params.irradiance, 1e-9)
    ns = max(params.ns, 1)
    ideality = max(params.diode_ideality, 0.1)
    thermal_voltage = K_BOLTZMANN * (params.temperature_c + 273.15) / Q_ELECTRON
    voc_irradiance_delta = ideality * ns * thermal_voltage * math.log(irradiance / S_REF)
    return max(0.0, voc_temp + voc_irradiance_delta)


def simulate_panel(params: PanelParams) -> PanelResult:
    ns = max(int(params.ns), 1)
    points = max(int(params.points), 20)
    ideality = max(float(params.diode_ideality), 0.1)
    temp_k = max(params.temperature_c + 273.15, 1.0)

    isc = corrected_isc(params)
    voc = corrected_voc(params)
    iph = isc

    exponent_voc = Q_ELECTRON * voc / (K_BOLTZMANN * temp_k * ideality * ns)
    exponent_voc = min(exponent_voc, 700.0)
    denominator = math.exp(exponent_voc) - 1.0
    io = iph / denominator if denominator > 0 else 0.0

    voltage = np.linspace(0.0, voc, points)
    exponent = Q_ELECTRON * voltage / (K_BOLTZMANN * temp_k * ideality * ns)
    exponent = np.clip(exponent, None, 700.0)
    current = iph - io * (np.exp(exponent) - 1.0)
    current = np.maximum(current, 0.0)
    power = voltage * current

    idx = int(np.argmax(power)) if power.size else 0
    pmax = float(power[idx]) if power.size else 0.0
    vmp = float(voltage[idx]) if voltage.size else 0.0
    imp = float(current[idx]) if current.size else 0.0
    ropt = vmp / imp if imp > 0 else 0.0

    return PanelResult(
        voltage=voltage,
        current=current,
        power=power,
        voc=float(voc),
        isc=float(isc),
        pmax=pmax,
        vmp=vmp,
        imp=imp,
        ropt=ropt,
        iph=float(iph),
        io=float(io),
    )
