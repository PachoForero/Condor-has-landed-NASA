# 🛰️ Condor-has-landed-NASA

**Condor-has-landed-NASA** is a tool designed to **simulate different habitat configurations** for settlement and colonization missions within regions **between the Sun and the Asteroid Belt** of the Solar System.

By configuring and calculating various **habitat module models** and **mission parameters**, it allows the simulation of space habitat development based on mission objectives and system constraints.

---

##  Available Volume Calculations for Each Launch Vehicle

###  Starship (SpaceX)

**Reference Data:**

- Total fuselage diameter: **9 m**  
- Usable payload envelope diameter: **8 m (internal usable space)**  
- Usable height: **~17.24 m**, extendable up to **~22 m**  
- Estimated usable internal volume: **~1,000 m³**

**Cylindrical model (8 m diameter):**

![image](https://github.com/user-attachments/assets/71cb4987-793e-4894-9745-3ccb8f9a5ff2)

**Payload mass:**
- Reusable configuration: **100–150 metric tons**
- Expendable configuration (estimated): **up to 200 tons**

**Conclusion:**
> Effective payload density (mass/volume):  
> **115.5 – 173.3 kg/m³**

Assuming a **maximum payload of 150 tons** and **usable volume of 886.4 m³**,  
with **8 m diameter** and **18–22 m height**.

---

###  New Glenn (Blue Origin)

**Reference Data:**

![image](https://github.com/user-attachments/assets/9d7e0aa1-3905-4e31-905d-332f0d0c29ac)

- Payload capacity: **up to 45 tons (45,000 kg) to LEO**  
- Fairing diameter: **7 m**  
- Usable payload fairing height: **21.9 m**

**Cylindrical model (7 m diameter, 21.9 m height):**

![image](https://github.com/user-attachments/assets/81aac9d4-3d46-446c-9438-dd857030b05a)

**Conclusion:**
> Effective density: **~53.5 kg/m³**  
> Max payload: **45 tons**  
> Max usable volume: **~458 m³**

---

###  Visualization References

**Starship (payload zone highlighted with opacity):**

![image](https://github.com/user-attachments/assets/232197a7-eebd-40b2-b1a3-374762f2e07e)

**New Glenn:**

![image](https://github.com/user-attachments/assets/ba64df03-8bca-4221-a6c5-4e2f8eaaff50)

**Rocket type selection button reference:**

<img width="426" height="233" alt="ejemplo boton tipo de cohete 2" src="https://github.com/user-attachments/assets/d6820280-48cf-474b-a182-42289b13edd8" />

---

##  Mission Cost

Mission cost depends on **final payload mass**:

| Rocket | Cost per kg (USD) |
|---------|------------------:|
| **Starship** | **$2,000 / kg** |
| **New Glenn** | **$1,511 / kg** |

---

##  Module A

**General specifications:**

- **Crew capacity:** 2 humans  
- **Maximum internal volume (no dome):** 60.2 m³  
- **Maximum internal volume (with dome):** 116.75 m³  
- **Airlock:** 1 EVA-compatible hatch  
- **Walls:** Canadarm2 compatible  
- **Dome structure:** multilayer composite shell  

![image](https://github.com/user-attachments/assets/a7a22c5d-e83c-48da-a5f2-922809825f1b)

---

###  BioRLSS (Bioregenerative Life Support System)

#### Oxygen (O₂)
- Consumption: **0.89 kg O₂ / person / day**
- Total for 2 crew × 60 days = **106.8 kg**
- Stored as **LOX** (density ≈ 1141 kg/m³)
  - Volume = 106.8 / 1141 ≈ **0.094 m³ (94 L)**  
  - References:  
    [PMC8398003](https://pmc.ncbi.nlm.nih.gov/articles/PMC8398003/)  
    [Harper16_NS_LifeSupportLunarSettelment.pdf](https://www3.nd.edu/~cneal/CRN_Papers/Harper16_NS_LifeSupportLunarSettelment.pdf)

#### Food
- BVAD rate: **2.39 kg/person·day**
- Total: **286.8 kg** (for 2 crew, 60 days)
- Volume estimate (density 800 kg/m³): **0.36 m³ (360 L)**  
- Reference:  
  [NASA Logistics BVAD 2019](https://ntrs.nasa.gov/api/citations/20190027563/downloads/20190027563.pdf)

#### Energy — Batteries
- Power demand per person:
  - **Low (keep-alive):** 300 W/person
  - **High (transit/full ECLSS):** 2.37 kW/person
- Duration: 60 days  
- Calculations:
  - **Low case (216 kWh):** 864 kg, 0.43 m³
  - **High case (1,704 kWh):** 6,816 kg, 3.41 m³  

References:  
[Harper16_NS_LifeSupportLunarSettelment.pdf](https://www3.nd.edu/~cneal/CRN_Papers/Harper16_NS_LifeSupportLunarSettelment.pdf)  
[Power Requirements and Strategy.pdf](https://cmapspublic3.ihmc.us/rid%3D1P89G93VL-Z1VT05-17QZ/Power%20Requirements%20and%20Strategy.pdf)

---

##  Module A (Juan Configuration)

- **Crew capacity:** 2 humans  
- **Internal volume (no dome):** 60.2 m³  
- **Internal volume (with dome):** 116.75 m³  
- **Airlock:** 1 EVA-compatible hatch  
- **Canadarm2-compatible walls**

### BioRLSS Summary
| Resource | Mass | Volume | Notes |
|-----------|------|--------|-------|
| **O₂** | 106.8 kg | 0.105 m³ | LOX storage |
| **Food** | 286.8 kg | 0.37 m³ | BVAD packed supplies |
| **Batteries** | 864–6,816 kg | 0.42–3.43 m³ | Low ↔ High power cases |

---

##  Canadarm2

- Reported mass: **~1,497 kg (CSA)**  
  - Other sources round up to **~1,800 kg**
- Reserved storage volume: **8 m³**
  - Cylindrical envelope: **0.77 m diameter × 17 m length**

---

## Module Structure (Base Mass)

- **Outer wall:** 6 cm (Al 40% / Ti 10% / Nextel 50%)  
  - Volume = 2.448 m³ → **Mass ≈ 5,581 kg**
- **Internal partitions:** 4 cm (Al 20% / Ti 5% / Nextel 75%)  
  - Volume = 3.298 m³ → **Mass ≈ 6,233 kg**
- **Inflatable dome:** **0.179 t**

**Optimized total structural mass:**
> **≈ 12.0 t (12,000 kg)**

---

##  Internal Distribution (Volume & Mass per Area)

**Total internal volume:** 60.2 m³

| Area | % | Volume (m³) | Mass (kg) |
|------|--:|-------------:|-----------:|
| Exercise | 16% | 9.632 | 500 |
| Social / Dining | 10% | 6.020 | 230 |
| Hygiene / Waste | 7% | 4.214 | 280 |
| Logistics / EVA | 25% | 15.050 | 1,190 |
| Galley / Kitchen | 12% | 7.224 | 370 |
| Medical / Command | 10% | 6.020 | 340 |
| Private (Central) | 20% | 12.040 | 310 |

---

###  Equipment per Area

**Exercise (peripheral sector)** — *9.632 m³ / 500 kg*  
- ARED (frame + actuators) — 220 kg  
- Treadmill — 110 kg  
- Cycle ergometer — 60 kg  
- Harness / sensors — 40 kg  
- Racks / protection mounts — 70 kg  

**Social / Dining / Mission Area** — *6.020 m³ / 230 kg*  
- Folding table, projector, AV system, utensils and panels.

**Hygiene / Toilet / Waste Collection** — *4.214 m³ / 280 kg*  
- Space toilet, solid compactor, hygiene filters, consumable lockers.

**Logistics / Maintenance / EVA support** — *15.050 m³ / 1,190 kg (no batteries)*  
- Storage racks, **Food (286.8 kg)**, **O₂ (106.8 kg)**, tools, EVA fixtures, comms racks.

**Galley / Meal Prep** — *7.224 m³ / 370 kg*  
- Water heater, compact cooling unit, utensils, small sink.

**Medical / Command** — *6.020 m³ / 340 kg*  
- Portable med kits, drugs, consoles, displays, foldable stretcher.

**Private / Sleep / Waste (central mini-hex)** — *12.040 m³ / 310 kg*  
- 2 bunks, personal lockers, work station, small waste packer.

---

##  Energy Scenarios

| Case | Total Energy | Mass | Volume | Notes |
|------|---------------|------|--------|-------|
| **Low (keep-alive)** | 216 kWh | 864 kg | 0.43 m³ | Minimal life support power |
| **High (full transit)** | 1,704 kWh | 6,816 kg | 3.41 m³ | Full ECLSS + processing |

---

##  Overall Mass Totals

| Configuration | Total Mass (excl. structure) |
|----------------|------------------------------:|
| Base (no batteries) | ≈ **3,220 kg** |
| With batteries — low | ≈ **4,084 kg** |
| With batteries — high | ≈ **10,036 kg** |

**Total module mass (structure + systems):**  
> **≈ 12,000 kg + payload (3–10 t)** → **~15–22 tons**

---

###  Structural Integration (Layout Suggestion)

- **6 peripheral sectors:** Exercise, Social, Hygiene, Logistics, Galley, Medical/Command.  
- **1 central mini-hex:** Private / Sleeping area.  
- Allows a radial layout with a central access hub and service connection through outer walls.

<img width="504" height="412" alt="image" src="https://github.com/user-attachments/assets/c751d891-1408-4836-9e5a-d9639ad5efcf" />


