# 🛰️ Condor-has-landed-NASA

**Condor-has-landed-NASA** es una herramienta que permite **simular diferentes configuraciones de hábitats** para misiones de asentamiento y colonización espacial, considerando ubicaciones comprendidas entre el **Sol y el cinturón de asteroides** del Sistema Solar.

A través de la configuración y el cálculo de distintos **modelos de módulos** y **misiones de asentamiento/colonización**, se puede estimar el desarrollo de un hábitat espacial según parámetros técnicos y objetivos de misión.

---

## 🚀 Cálculos de volumen disponible en cada cohete

### 🛩️ Starship (SpaceX)

**Datos de referencia:**

- Diámetro total del fuselaje externo: **9 m**  
- Envoltura dinámica útil para carga: **8 m de diámetro interno**  
- Altura útil típica: **~17.24 m**, extensible hasta **~22 m**  
- Volumen interno utilizable estimado: **~1 000 m³**

**Modelo cilíndrico (8 m de diámetro):**

![image](https://github.com/user-attachments/assets/71cb4987-793e-4894-9745-3ccb8f9a5ff2)

**Masa útil:**
- Configuración reutilizable: **100–150 toneladas**
- Configuración desechable (estimada): **hasta 200 toneladas**

**Conclusión:**
> Densidad efectiva de carga (masa/volumen):  
> **115.5 – 173.3 kg/m³**

Usando un peso máximo de **150 toneladas** y un volumen máximo de **886.4 m³**,  
con **8 m de diámetro** y **18–22 m de altura útil**.

---

### 🛰️ New Glenn (Blue Origin)

**Datos de referencia:**

![image](https://github.com/user-attachments/assets/9d7e0aa1-3905-4e31-905d-332f0d0c29ac)

- Capacidad: **hasta 45 toneladas (45 000 kg) a LEO**
- Diámetro del fairing: **7 m**
- Altura útil de la bahía de carga: **21.9 m**

**Modelo cilíndrico (7 m de diámetro, 21.9 m de altura):**

![image](https://github.com/user-attachments/assets/81aac9d4-3d46-446c-9438-dd857030b05a)

**Conclusión:**
> Densidad efectiva: **~53.5 kg/m³**  
> Peso máximo: **45 toneladas**  
> Volumen máximo aproximado: **458 m³**

---

### 📦 Visualizaciones

**Starship (área de ubicación de los módulos, con opacidad):**

![image](https://github.com/user-attachments/assets/232197a7-eebd-40b2-b1a3-374762f2e07e)

**New Glenn:**

![image](https://github.com/user-attachments/assets/ba64df03-8bca-4221-a6c5-4e2f8eaaff50)

**Ejemplo de botón de selección de tipo de cohete:**

![image](https://github.com/user-attachments/assets/f37e1f02-182e-44db-96e9-31b4906f37b6)

---

## 💰 Costos de misión

El costo total depende del **peso final de la carga**:

| Cohete      | Costo estimado por kg |
|--------------|-----------------------|
| **Starship** | **US$ 2,000 / kg**   |
| **New Glenn**| **US$ 1,511 / kg**   |

---

## 🧩 Módulo A

**Especificaciones generales:**

- **Capacidad:** 2 personas  
- **Volumen máximo (sin Dome deployment):** 60.2 m³  
- **Volumen máximo (con Dome deployment):** 116.75 m³  
- **Compuertas:** 1 compatible con EVA  
- **Paredes:** compatibles con **Canadarm2**  
- **Material del domo:** estructura compuesta multicapa  

![image](https://github.com/user-attachments/assets/a7a22c5d-e83c-48da-a5f2-922809825f1b)

---

### ⚙️ BioRLSS (Life Support System)

#### Oxígeno (O₂)
- Consumo: **0.89 kg O₂ / persona / día**
- Total para 2 personas × 60 días = **106.8 kg**
- Almacenado como **LOX** (densidad ≈ 1141 kg/m³)
  - Volumen = 106.8 / 1141 ≈ **0.094 m³ (94 L)**  
  - Referencias:  
    [PMC8398003](https://pmc.ncbi.nlm.nih.gov/articles/PMC8398003/)  
    [Harper16_NS_LifeSupportLunarSettelment.pdf](https://www3.nd.edu/~cneal/CRN_Papers/Harper16_NS_LifeSupportLunarSettelment.pdf)

#### Alimentos
- Tasa BVAD: **2.39 kg/persona·día**
- Total: **286.8 kg** (para 2 personas, 60 días)
- Volumen estimado (densidad 800 kg/m³): **0.36 m³ (360 L)**
- Referencia:  
  [NASA Logistics BVAD 2019](https://ntrs.nasa.gov/api/citations/20190027563/downloads/20190027563.pdf)

#### Energía — Baterías
- Potencia por persona:  
  - **Bajo (keep-alive):** 300 W/persona  
  - **Alto (transit completo):** 2.37 kW/persona  
- Duración: 60 días  
- Cálculos:
  - Bajo (216 kWh): **864 kg**, **0.43 m³**
  - Alto (1,704 kWh): **6,816 kg**, **3.41 m³**

Referencias técnicas:  
[Harper16_NS_LifeSupportLunarSettelment.pdf](https://www3.nd.edu/~cneal/CRN_Papers/Harper16_NS_LifeSupportLunarSettelment.pdf)  
[Power Requirements and Strategy.pdf](https://cmapspublic3.ihmc.us/rid%3D1P89G93VL-Z1VT05-17QZ/Power%20Requirements%20and%20Strategy.pdf)

---

## 🤖 Módulo A para JUAN

- **Crew capacity:** 2 humans  
- **Internal volume (no dome):** 60.2 m³  
- **Internal volume (with dome):** 116.75 m³  
- **1 EVA-compatible hatch**  
- **Canadarm2 compatible walls**

### BioRLSS Summary
| Recurso | Masa | Volumen | Notas |
|----------|-------|----------|-------|
| **O₂** | 106.8 kg | 0.105 m³ | LOX storage |
| **Comida** | 286.8 kg | 0.37 m³ | BVAD packaging |
| **Baterías** | 864–6,816 kg | 0.42–3.43 m³ | Bajo ↔ Alto consumo |

---

## 🦾 Canadarm2

- Masa reportada: **~1,497 kg (CSA)**  
  - En fuentes extendidas: hasta **1,800 kg**
- Volumen reservado: **8 m³**
  - Envolvente cilíndrica de **0.77 m diámetro × 17 m largo**

---

## 🧱 Estructura del módulo (masa base)

- **Pared exterior:** 6 cm (Al 40% / Ti 10% / Nextel 50%)  
  - Volumen: 2.448 m³ → Masa ≈ **5,581 kg**
- **Paredes internas:** 4 cm (Al 20% / Ti 5% / Nextel 75%)  
  - Volumen: 3.298 m³ → Masa ≈ **6,233 kg**
- **Domo inflable:** **0.179 t**

**Masa total optimizada:**  
> ≈ **12.0 t (12,000 kg)**

---

## 📊 Distribución interna (volúmenes y masas por área)

**Volumen total del módulo:** 60.2 m³  
**Distribución porcentual:**

| Área | % | Volumen (m³) | Masa estimada (kg) |
|------|---|---------------|--------------------|
| Ejercicio | 16% | 9.632 | 500 |
| Social / Comedor | 10% | 6.020 | 230 |
| Higiene / Waste | 7% | 4.214 | 280 |
| Logística / EVA | 25% | 15.050 | 1,190 |
| Galley / Cocina | 12% | 7.224 | 370 |
| Médico / Comando | 10% | 6.020 | 340 |
| Privado (Central) | 20% | 12.040 | 310 |

---

### 🔧 Equipos por área

**Ejercicio (sector periférico)** — *9.632 m³ / 500 kg*  
- ARED (frame + actuators) — 220 kg  
- Treadmill — 110 kg  
- Cycle ergometer — 60 kg  
- Arnés / sensores — 40 kg  
- Racks / protecciones — 70 kg  

**Social / Comedor / Misión (mesa + AV)** — *6.020 m³ / 230 kg*  
- Mesa plegable, proyector, panel AV, estanterías y utensilios.

**Higiene / Inodoro / Recolección** — *4.214 m³ / 280 kg*  
- Toilet espacial, compactador sólidos, bombas/filtros, lockers.

**Logística / Mantenimiento / EVA support** — *15.050 m³ / 1,190 kg (sin baterías)*  
- Racks de stowage, comida (286.8 kg), O₂ (106.8 kg), herramientas, estación EVA, racks IT/comms.

**Galley / Meal Prep** — *7.224 m³ / 370 kg*  
- Rehidratación, unidad de enfriamiento, utensilios, fregadero compacto.

**Médico / Comando** — *6.020 m³ / 340 kg*  
- Kit médico, fármacos, consola, displays, camilla.

**Privado / Sleep / Waste (mini-hex central)** — *12.040 m³ / 310 kg*  
- 2 camas, lockers personales, estación de trabajo, compactador pequeño.

---

## ⚡ Escenarios de energía

| Escenario | Energía total | Masa | Volumen | Comentario |
|------------|----------------|--------|-----------|-------------|
| **Bajo (keep-alive)** | 216 kWh | 864 kg | 0.43 m³ | Energía mínima de soporte vital |
| **Alto (transit completo)** | 1,704 kWh | 6,816 kg | 3.41 m³ | ECLSS completo + procesamiento |

---

## 📦 Totales globales


| Configuración | Masa total (sin estructuras) |
|----------------|------------------------------|
| Base (sin baterías) | **≈ 3,220 kg** |
| Con baterías (bajo)** | **≈ 4,084 kg** |
| Con baterías (alto)** | **≈ 10,036 kg** |

**Masa total del módulo (estructura + equipos + sistemas):**
> **≈ 12,000 kg + payload (3–10 t)** → **15–22 t** aprox.

---

### 🪐 Integración estructural sugerida

- **6 sectores periféricos:** áreas de Ejercicio, Social, Higiene, Logística, Galley, Médico/Comando.  
- **1 mini-hex central:** zona Privada / Descanso.  
- Permite disposición radial con acceso común central y conexión de servicios hacia los bordes.


<img width="504" height="412" alt="image" src="https://github.com/user-attachments/assets/c751d891-1408-4836-9e5a-d9639ad5efcf" />


