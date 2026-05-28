# Modelo del Panel Solar

Interfaz gráfica en Python para simular las curvas Voltaje-Corriente y Voltaje-Potencia de un panel solar, basada en el PDF/LabVIEW `Modelo del Panel`.

## Fórmula usada

Modelo simplificado visto en el documento:

```text
I = Np·Iph - Np·Io·( exp(q·V / (k·T·A·Ns)) - 1 )
```

También se considera:

```text
I = Iph - Id - Ish
```

con la aproximación indicada en el PDF: `Rsh` alta y `Rs` baja.

## Valores iniciales

Los valores por defecto son los visibles en el panel de LabVIEW:

- Temperatura: `25 °C`
- Irradiancia: `1000 W/m²`
- Ns: `36`
- Np: `1`
- Voc: `22.41 V`
- Isc: `9.67 A`
- KIsc: `0.1 %/°C`
- KVoc: `-0.08 V/°C`
- Factor de idealidad A: `2.0`

## Ejecutar

Requiere `numpy` y `matplotlib`.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Archivos

- `main.py`: interfaz gráfica Tkinter + gráficas Matplotlib.
- `panel_model.py`: cálculo del modelo matemático con NumPy.
- `requirements.txt`: dependencias.
