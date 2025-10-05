# Condor-has-landed-NASA
Con esta herramienta se podran simular las diferentes configuraciones de habitats para misiones de asentamientos y colonización, partiendo de espacios comprendidos entre el sol y el cinturon de asteroides del sistema solar
A traves de la configuracion y el calculo de diferentes modelos de modulos y misiones de asentamiento y colonizacion, se puede simular el desarrollo de el habitat espacial dependiendo de los parametros y objetivos

## Calculos volumen disponible en cada cohete 
### starship 
Datos de referencia:
- El diámetro total del fairing / fuselaje externo es de 9 m (diámetro exterior) según el Starship Users Guide de SpaceX. Referencia: Starship users guide de spacex (esta en el grupo)
- la “envoltura dinámica de carga útil” (payload dynamic envelope) que SpaceX menciona es de 8 m de diámetro para la carga interna utilizable. Referencia: https://www.eoportal.org/other-space-activities/starship-of-spacex
- Altura útil típica de carga: ~ 17.24 m para la sección recta interior, con opción de extensión hasta ~ 22 m.
- Algunas fuentes estiman un volumen interno cercano a ~ 1 000 m³ para la bahía utilizable.

Asumiendo que usas un cilindro ideal con diámetro 8m

<img width="557" height="323" alt="image" src="https://github.com/user-attachments/assets/71cb4987-793e-4894-9745-3ccb8f9a5ff2" />

para masa util estimada:
- En configuración reutilizable: ~ 100 a 150 toneladas (100 000 a 150 000 kg) según SpaceX
- En configuración desechable: algunas fuentes especulan hasta ~ 200 toneladas

Conclusion: Entonces la densidad efectiva de carga (masa / volumen) para las configuraciones sería:
(115.5 – 173.3 km/m^3) para el starship colocar peso max de 150 toneladas y un volumen max de 886.4m^3 con un diametro de 8m y unaaltura de entre 18 y 22m

### New Glenn

Datos de referencia:

<img width="686" height="472" alt="image" src="https://github.com/user-attachments/assets/9d7e0aa1-3905-4e31-905d-332f0d0c29ac" />

- Azul Origin indica que New Glenn puede llevar hasta 45 000 kg (45 toneladas) a órbita terrestre baja (LEO)
- Diámetro del cohete / fairing: 7 m de diámetro exterior
- En el New Glenn Payload User’s Guide se menciona que la altura útil de la bahía de carga (fairing) es 21.9 m con diámetro 7 m

Asumiendo que la carga cabe en un cilindro de diámetro 7 m y altura total de la etpa 21.9 m:

<img width="599" height="183" alt="image" src="https://github.com/user-attachments/assets/81aac9d4-3d46-446c-9438-dd857030b05a" />

Conclusion: la densidad efectiva seria: 53.5kg/m3 colocar peso max de 45 tonaeladas y volumen max aprox de 458m^3 con 7 m de diametro y largo util de 11.9m

Colocar la siguiente foto para el STARSHIP con opacidad en el area de ubicacion de los modulos

<img width="291" height="781" alt="image" src="https://github.com/user-attachments/assets/232197a7-eebd-40b2-b1a3-374762f2e07e" />

Colocar la diguiente foto para el NEW GLENN

<img width="1920" height="1080" alt="Diseño sin título" src="https://github.com/user-attachments/assets/ba64df03-8bca-4221-a6c5-4e2f8eaaff50" />

usar la sig referencia para el boton de tipo de cohete

<img width="426" height="233" alt="ejemplo boton tipo de cohete" src="https://github.com/user-attachments/assets/f37e1f02-182e-44db-96e9-31b4906f37b6" />

en costo total de la mision se pone un valor depnede del peso final
 en costo para el starship es de US$2000/kg
 en el costo del new glenn es de US$1,511U/kg

## menu debe contener:

 Modulo A 

si selecciona mas info debe decir las siguientes especificaciones:
Capacidad 2 personas
Volumen max (sin Dome deployment): 60.2m^3
Volumen max (with Dome deployment): 116.75m^3
1 compuerta para EVA
Paredes compatibles con Canadarm2
- BioRLSS:
  - 0.89 kg O₂ / persona / día (valor conservador en literatura para misiones que incluye ejercicio) entonces carga con 106.8 kg O₂ y Si se almacena como LOX
    - (densidad LOX ≈ 1141 kg/m³): volumen = 106.8 / 1141 ≈ 0.094 m³ (≈ 94 L) (densidad LOX: 1141 kg/m³).https://pmc.ncbi.nlm.nih.gov/articles/PMC8398003/ https://www3.nd.edu/~cneal/CRN_Papers/Harper16_NS_LifeSupportLunarSettelment.pdf
  - Supuesto usado (BVAD / NASA logistics): 2.39 kg por persona por día (como enviado / embalado) (esta cifra incluye empaques / preparación típico ISS/BVAD). https://ntrs.nasa.gov/api/citations/20190027563/downloads/20190027563.pdf la densidad de “alimentos listos para misión” varía: comidas liofilizadas ocupan menos masa pero requieren agua para rehidratación; comidas refrigeradas/frozen ocupan más volumen. NASA/BVAD presenta tablas de volumen por masa según tipo. en otraiteracion del programa se podria especificar mas y cambiar variables del bioRLSS segun el tipo de comida
    - Cálculo: 2.39 kg × 2 × 60 = 286.8 kg total (comida + embalaje).
    - Volumen (estimado): asumí una densidad global de paquete ≈ 800 kg/m³ (0.8 kg/L) — resultado: 286.8 / 800 = 0.3585 m³ ≈ 0.36 m³ (≈ 360 L).
  - Energía — baterías: Supuestos de potencia por persona https://www3.nd.edu/~cneal/CRN_Papers/Harper16_NS_LifeSupportLunarSettelment.pdf https://cmapspublic3.ihmc.us/rid%3D1P89G93VL-Z1VT05-17QZ/Power%20Requirements%20and%20Strategy.pdf en la práctica se combinaría: paneles solares u otra generación + baterías sólo como buffer (no almacenar toda la energía de la misión en baterías). Para misiones de tránsito con energía nuclear/fisión o celdas de combustible, la estrategia será distinta.
    - Alto (transit/surface ECLSS más completo): ~2.37 kW / persona (escenario con mayor capacidad ECLSS / climatización / procesamiento). Usé este valor para representar un caso exigente. (nota: conceptos de misión y estudios de potencia muestran requerimientos por tripulante desde cientos de W hasta kW según alcance)
    - Bajo (ISS keep-alive/PLS): ~300 W / persona continuo
      - Potencia total continuo (bajo): 300 W × 2 = 600 W. (60dias)
      - Potencia total continuo (alto): 2,370 W × 2 ≈ 4,733 W. (60 dias)
        - Bajo (216 kWh): masa ≈ 216,000 Wh / 250 Wh/kg ≈ 864 kg ; volumen ≈ 216,000 Wh / 500 Wh/L = 432 L = 0.432 m³.
        - Alto (1,704 kWh): masa ≈ 6,816 kg ; volumen ≈ 3.41 m³
        
MODULO A PARA JUAN
- Crew capacity: 2 HUMANS
- Maximum internal volume (without Dome deployment): 60.2 m³
- Maximum internal volume (with Dome deployment): 116.75 m³
- Airlock / hatch: 1 EVA-compatible hatch
- Wall interfaces: Compatible with Canadarm2 for handling and docking operation
- BioRLSS
    - Oxygen (O₂)
      - Mass (by BVAD rate 0.89 kg/person·day): 106.8 kg
      - Volume (by CTBE method from paper, 0.0527 m³/CTBE ≈ 2 CTBE): 0.105 m³
    - Food (nutritional supplies)
      - Mass (by BVAD 2.39 kg/person·day): 286.8 kg
      - Volume (by CTBE method from paper, ≈ 7 CTBE): 0.37 m³
    - Energy / Batteries
      - Volume (low-power case = 216 kWh): 0.43 m³ | (high-power case = 1704 kWh): 3.41 m³
      - Mass (low-power): 864 kg | (high-power): 6 816 kg
      - Volume (CTBE equivalent, low ≈ 8 CTBE | high ≈ 65 CTBE): 0.42 – 3.43 m³ usar ESTE volumen
- Eva suits
- Human factors

MODULO B PARA JUAN


     




