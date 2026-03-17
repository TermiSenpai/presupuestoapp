# Calculadora de Presupuestos DTF

Aplicación de escritorio para calcular costes de impresión DTF (Direct to Film) de forma rápida y precisa. Pensada para profesionales que trabajan directamente con proveedores de DTF y necesitan presupuestar al cliente final sin complicaciones.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/TermiSenpai/presupuestoapp)
![Release](https://img.shields.io/github/v/release/TermiSenpai/presupuestoapp)
![Build](https://img.shields.io/github/actions/workflow/status/TermiSenpai/presupuestoapp/build.yml?label=build)

---

## Características

- **Cálculo instantáneo de coste** según ancho de rollo, precio por metro, dimensiones del diseño, márgenes y número de copias.
- **Comparación automática de orientaciones** (0° y 90°) para encontrar el aprovechamiento óptimo del rollo.
- **Tamaños predefinidos** para los formatos DTF más habituales: etiquetas, logos, mangas, frontales, espaldas, gorras, bolsas, parches, infantil y textiles grandes.
- **Configuración persistente** — el ancho del rollo, precio/metro y márgenes se guardan entre sesiones.
- **Actualizaciones automáticas** — la app comprueba nuevas versiones en GitHub Releases al arrancar e instala la actualización con un solo clic.
- **Ejecutable portable para Windows** — no requiere instalar Python ni dependencias.

## Descarga rápida

Descarga la última versión del ejecutable desde la sección de [Releases](https://github.com/TermiSenpai/presupuestoapp/releases/latest). Descomprime el ZIP y ejecuta `DTF_Pricing_Calculator.exe`.

## Ejecución desde código fuente

### Requisitos previos

- Python 3.11 o superior
- pip

### Instalación

```bash
git clone https://github.com/TermiSenpai/presupuestoapp.git
cd presupuestoapp
pip install -r requirements.txt
```

### Uso

```bash
python main.py
```

La aplicación abrirá una ventana con dos pestañas:

- **Cálculo** — selecciona un tamaño predefinido o introduce dimensiones personalizadas, el número de copias y pulsa *Calcular*. Los resultados muestran diseños por fila, filas necesarias, aprovechamiento del rollo, longitud total consumida y coste estimado para ambas orientaciones.
- **Configuración** — ajusta el ancho del rollo (cm), precio por metro (€), margen superior y margen derecho. Los valores se guardan automáticamente al cerrar la app.

## Estructura del proyecto

```
presupuestoapp/
├── .github/workflows/
│   └── build.yml            # CI/CD — build con PyInstaller + release automático
├── presupuestos_dtf/
│   ├── __init__.py          # Versión del paquete (__version__)
│   ├── app.py               # Punto de entrada, inicialización de la ventana y auto-updater
│   ├── calc.py              # Lógica de cálculo de layout y coste
│   ├── config.py            # Carga/guardado de configuración en JSON
│   ├── constants.py         # Constantes globales (valores por defecto, título, tamaño de ventana)
│   ├── models.py            # Dataclasses de entrada (CalcInput) y resultado (CalcResult)
│   ├── ui.py                # Interfaz gráfica con tkinter (pestañas, presets, validación)
│   └── updater.py           # Comprobación y descarga de actualizaciones desde GitHub Releases
├── main.py                  # Entry point
├── requirements.txt         # Dependencias de runtime y build
├── PresupuestosDTF.ico      # Icono de la aplicación
├── LICENSE.md               # Licencia MIT
└── README.md
```

## Build del ejecutable

El proyecto usa GitHub Actions para generar el ejecutable automáticamente en cada push a `main`. Si prefieres hacer el build en local:

```bash
pip install pyinstaller
pyinstaller --noconfirm --clean --noconsole --onedir \
  --name DTF_Pricing_Calculator \
  --icon PresupuestosDTF.ico \
  main.py
```

El ejecutable estará en `dist/DTF_Pricing_Calculator/`.

## Configuración

Los ajustes se almacenan en un archivo JSON cuya ubicación depende del sistema operativo:

- **Windows:** `%APPDATA%\PresupuestosDTF\config.json`
- **Linux/macOS:** `~/.PresupuestosDTF/config.json`

Valores por defecto:

| Parámetro | Valor |
|---|---|
| Ancho del rollo | 57 cm |
| Precio por metro | 11 €/m |
| Margen superior | 0.5 cm |
| Margen derecho | 0.5 cm |

## Contribuir

Las contribuciones son bienvenidas. Para cambios relevantes, abre primero un *issue* para discutir la propuesta.

1. Haz fork del repositorio.
2. Crea una rama para tu cambio (`git checkout -b feature/mi-mejora`).
3. Haz commit de tus cambios (`git commit -m "feat: descripción del cambio"`).
4. Sube la rama (`git push origin feature/mi-mejora`).
5. Abre un Pull Request.

## Licencia

Este proyecto está licenciado bajo la [Licencia MIT](LICENSE.md).
