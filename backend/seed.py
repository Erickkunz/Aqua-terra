"""Seed data for Aqua-Terra platform.

Run automatically on startup if SEED_ON_STARTUP=true.
Run manually with reset: `python seed.py --reset`.
"""
from __future__ import annotations

import logging
import sys
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import Category, Product, Project, Testimonial, BlogPost
from utils import slugify

logger = logging.getLogger("aquaterra.seed")


CATEGORIES = [
    {"slug": "riego-automatico", "name": "Sistemas de Riego Automatico", "icon": "droplet",
     "description": "Goteo, aspersion, pivot y controladores inteligentes."},
    {"slug": "equipos-maquinaria", "name": "Equipos y Maquinaria", "icon": "gears",
     "description": "Bombas, filtros, tuberias y accesorios."},
    {"slug": "soluciones-inteligentes", "name": "Soluciones Inteligentes", "icon": "microchip",
     "description": "IoT, software de gestion y sensorica especializada."},
    {"slug": "soluciones-sostenibles", "name": "Soluciones Sostenibles", "icon": "leaf",
     "description": "Recoleccion de lluvia, tratamiento de aguas y renovables."},
]


PRODUCTS = [
    # ---- Riego automatico ----
    {"category": "riego-automatico", "name": "Kit Goteo Premium 5ha", "price": 4200, "rating": 4.7, "in_stock": True, "is_featured": True,
     "short_description": "Sistema completo de riego por goteo para 5 hectareas, autoregulable.",
     "specifications": {"cobertura": "5 ha", "presion": "2.0 bar", "emisores": "Compensados 2 L/h", "filtracion": "120 mesh"},
     "features": ["Autoregulable", "Garantia 5 años", "Instalacion modular"],
     "bulk_discount": {"5": 0.05, "10": 0.10},
     "tech_tags": ["drip"]},
    {"category": "riego-automatico", "name": "Kit Goteo Premium 10ha", "price": 7800, "rating": 4.8, "in_stock": True, "is_featured": True,
     "short_description": "Solucion goteo para 10 hectareas con controlador integrado.",
     "specifications": {"cobertura": "10 ha", "presion": "2.5 bar", "emisores": "Compensados 4 L/h", "filtracion": "120 mesh"},
     "features": ["IoT Ready", "Controlador incluido", "Garantia 5 años"],
     "bulk_discount": {"3": 0.06, "10": 0.12}},
    {"category": "riego-automatico", "name": "Aspersor Sectorial Pro", "price": 320, "rating": 4.5, "in_stock": True,
     "short_description": "Aspersor sectorial de bajo consumo, ideal para frutales.",
     "specifications": {"caudal": "1.5 m3/h", "alcance": "12 m", "presion": "3.5 bar"},
     "features": ["Bajo consumo", "Cobertura uniforme"],
     "bulk_discount": {"20": 0.08, "100": 0.15}},
    {"category": "riego-automatico", "name": "Sistema Pivot Central 40ha", "price": 38500, "rating": 4.9, "in_stock": True, "is_featured": True,
     "short_description": "Pivot central robusto, automatizado, ideal para cereales.",
     "specifications": {"cobertura": "40 ha", "longitud_brazo": "215 m", "torres": "8"},
     "features": ["Control remoto GPS", "Diagnostico predictivo", "Brazos galvanizados"]},
    {"category": "riego-automatico", "name": "Controlador Inteligente Smart-Drip", "price": 890, "rating": 4.6, "in_stock": True,
     "short_description": "Controlador WiFi/LoRa para hasta 16 valvulas.",
     "specifications": {"canales": "16", "conectividad": "WiFi + LoRa", "alimentacion": "Solar"},
     "features": ["App movil", "Modos programables", "Bateria 5 años"]},
    {"category": "riego-automatico", "name": "Valvula Solenoide 1\"", "price": 65, "rating": 4.3, "in_stock": True,
     "short_description": "Valvula solenoide 24V para sistemas automatizados.",
     "specifications": {"diametro": "1 pulgada", "voltaje": "24 V AC", "presion_max": "10 bar"},
     "features": ["Apertura manual", "Cuerpo PVC reforzado"],
     "bulk_discount": {"10": 0.07, "50": 0.18}},
    {"category": "riego-automatico", "name": "Sensor Humedad Suelo Pro", "price": 145, "rating": 4.7, "in_stock": True,
     "short_description": "Sensor capacitivo de humedad de suelo con conectividad LoRa.",
     "specifications": {"profundidad": "30 cm", "conectividad": "LoRa 868 MHz", "bateria": "3 años"},
     "features": ["IP67", "Calibracion automatica"]},
    {"category": "riego-automatico", "name": "Kit Aspersion Movil 2ha", "price": 1450, "rating": 4.4, "in_stock": False,
     "short_description": "Kit de aspersion movil para parcelas pequeñas.",
     "specifications": {"cobertura": "2 ha", "aspersores": "12", "tuberia": "100 m"},
     "features": ["Portatil", "Conexion rapida"]},

    # ---- Equipos y maquinaria ----
    {"category": "equipos-maquinaria", "name": "Bomba Centrifuga 5HP", "price": 1850, "rating": 4.6, "in_stock": True,
     "short_description": "Bomba centrifuga de alta eficiencia para riego de mediana escala.",
     "specifications": {"potencia": "5 HP", "caudal_max": "45 m3/h", "altura_max": "55 m"},
     "features": ["Acero inoxidable", "Sello mecanico premium"]},
    {"category": "equipos-maquinaria", "name": "Bomba Sumergible 10HP", "price": 3200, "rating": 4.5, "in_stock": True, "is_featured": True,
     "short_description": "Bomba sumergible para pozos profundos hasta 120 m.",
     "specifications": {"potencia": "10 HP", "profundidad_max": "120 m", "caudal_max": "90 m3/h"},
     "features": ["Acero inoxidable AISI 304", "Proteccion termica"]},
    {"category": "equipos-maquinaria", "name": "Filtro Arena 50 m3/h", "price": 1280, "rating": 4.5, "in_stock": True,
     "short_description": "Filtro de arena automatico para sistemas de riego.",
     "specifications": {"caudal": "50 m3/h", "presion_max": "8 bar"},
     "features": ["Retrolavado automatico", "Fibra de vidrio"]},
    {"category": "equipos-maquinaria", "name": "Filtro de Anillas 4\"", "price": 480, "rating": 4.4, "in_stock": True,
     "short_description": "Filtro de anillas de 4 pulgadas para goteo intensivo.",
     "specifications": {"diametro": "4 pulgadas", "filtracion": "120 mesh"},
     "features": ["Cuerpo PVC", "Limpieza manual"]},
    {"category": "equipos-maquinaria", "name": "Tuberia PE 32mm x 100m", "price": 110, "rating": 4.3, "in_stock": True,
     "short_description": "Rollo de tuberia polietileno alta densidad.",
     "specifications": {"diametro": "32 mm", "longitud": "100 m", "presion": "6 bar"},
     "features": ["Resistencia UV", "Flexible"],
     "bulk_discount": {"10": 0.08, "50": 0.18}},
    {"category": "equipos-maquinaria", "name": "Conjunto de Accesorios Premium", "price": 380, "rating": 4.2, "in_stock": True,
     "short_description": "Kit de accesorios: tees, codos, reducciones.",
     "specifications": {"piezas": "60", "material": "PP + PVC"},
     "features": ["Compatible con todas las marcas"]},
    {"category": "equipos-maquinaria", "name": "Purificador UV 20 m3/h", "price": 2100, "rating": 4.6, "in_stock": True,
     "short_description": "Esterilizacion por luz ultravioleta para agua de riego.",
     "specifications": {"caudal": "20 m3/h", "potencia_uv": "120 W"},
     "features": ["Bajo consumo electrico", "Sin productos quimicos"]},

    # ---- Soluciones inteligentes ----
    {"category": "soluciones-inteligentes", "name": "Plataforma AquaOS Cloud", "price": 4800, "rating": 4.9, "in_stock": True, "is_featured": True,
     "short_description": "Plataforma cloud de gestion hidrica con dashboards y alertas.",
     "specifications": {"usuarios": "Ilimitados", "sensores": "Hasta 500", "almacenamiento": "5 años"},
     "features": ["API REST", "Alertas SMS y email", "Integracion ERP"]},
    {"category": "soluciones-inteligentes", "name": "Sensor Caudal Magnetico DN50", "price": 720, "rating": 4.7, "in_stock": True,
     "short_description": "Caudalimetro magnetico DN50 con salida 4-20 mA.",
     "specifications": {"diametro": "DN50", "rango": "0.5-10 m/s", "precision": "0.5 %"},
     "features": ["IP68", "Sin partes moviles"]},
    {"category": "soluciones-inteligentes", "name": "Estacion Meteorologica IoT", "price": 1850, "rating": 4.8, "in_stock": True, "is_featured": True,
     "short_description": "Estacion con 7 sensores y conectividad LoRa/4G.",
     "specifications": {"sensores": "T, HR, viento, lluvia, ET0, presion, UV", "alimentacion": "Solar"},
     "features": ["Plug & play", "Datos cada 5 min"]},
    {"category": "soluciones-inteligentes", "name": "Gateway LoRa Multi-canal", "price": 980, "rating": 4.5, "in_stock": True,
     "short_description": "Gateway LoRa 8 canales con backhaul 4G.",
     "specifications": {"canales": "8", "alcance": "8 km", "backhaul": "4G"},
     "features": ["Outdoor IP65", "Mountaje universal"]},
    {"category": "soluciones-inteligentes", "name": "Sensor Calidad de Agua Multi-parametro", "price": 1650, "rating": 4.6, "in_stock": False,
     "short_description": "Mide pH, CE, DO y temperatura. Para fertirriego.",
     "specifications": {"parametros": "pH, CE, DO, T", "salida": "Modbus RTU"},
     "features": ["Auto-calibracion", "Robustez industrial"]},
    {"category": "soluciones-inteligentes", "name": "Software AquaBI - Analytics", "price": 3200, "rating": 4.7, "in_stock": True,
     "short_description": "BI especializado en consumo, eficiencia y forecasting hidrico.",
     "specifications": {"forecast": "30/60/90 dias", "exports": "CSV, PDF, API"},
     "features": ["Modelos ML pre-entrenados", "SSO empresarial"]},

    # ---- Soluciones sostenibles ----
    {"category": "soluciones-sostenibles", "name": "Sistema Recoleccion Lluvia 20 m3", "price": 5400, "rating": 4.6, "in_stock": True, "is_featured": True,
     "short_description": "Sistema completo de captacion y almacenamiento pluvial.",
     "specifications": {"capacidad": "20 m3", "filtros": "3 etapas"},
     "features": ["Tanque polietileno", "Bomba incluida"]},
    {"category": "soluciones-sostenibles", "name": "Planta Tratamiento Aguas Grises 5 m3/dia", "price": 12500, "rating": 4.7, "in_stock": True,
     "short_description": "Planta compacta para tratamiento de aguas grises.",
     "specifications": {"capacidad": "5 m3/dia", "consumo_electrico": "1.2 kWh/m3"},
     "features": ["Modular", "Control automatizado"]},
    {"category": "soluciones-sostenibles", "name": "Panel Solar Bomba Sumergible 2HP", "price": 4200, "rating": 4.5, "in_stock": True,
     "short_description": "Kit fotovoltaico para bomba sumergible 2HP.",
     "specifications": {"potencia_pv": "2.5 kWp", "bomba": "2 HP", "autonomia": "Diurna"},
     "features": ["MPPT integrado", "Sin baterias"]},
    {"category": "soluciones-sostenibles", "name": "Biofiltro Humedales Artificiales", "price": 8800, "rating": 4.8, "in_stock": True,
     "short_description": "Sistema natural de tratamiento por humedales artificiales.",
     "specifications": {"caudal": "3 m3/dia", "area": "30 m2"},
     "features": ["Bajo OPEX", "Cero quimicos"]},
    {"category": "soluciones-sostenibles", "name": "Estacion Reuso Agua Industrial", "price": 22000, "rating": 4.6, "in_stock": False,
     "short_description": "Estacion compacta para reuso de agua de procesos industriales.",
     "specifications": {"caudal": "10 m3/h", "tecnologia": "MBR + UV"},
     "features": ["Integracion SCADA", "Diseño modular"]},
]


PROJECTS = [
    {"name": "Riego sostenible Valle de Santa Cruz", "country": "Peru", "region": "Ica", "client_type": "agro",
     "technology": "drip", "lat": -14.07, "lng": -75.73, "water_saved_m3": 580000, "hectares": 120, "co2_reduced_t": 450,
     "duration_months": 12, "completion_date": date(2024, 6, 15), "is_featured": 1,
     "summary": "Implementacion de goteo + IoT en 120 ha de uva de exportacion.",
     "description": "Modernizamos el sistema de riego de un viñedo familiar, integrando goteo con sensores de humedad y una plataforma de gestion centralizada. El proyecto redujo el consumo de agua en 58% y aumento la produccion en 22%.",
     "testimonial_text": "El equipo se involucro como si fuera su propio campo. Resultados desde el primer ciclo.",
     "testimonial_author": "Carlos Mendoza - Gerente Agricola, Vinia Santa Cruz"},
    {"name": "Sistema municipal de aguas grises Tlalnepantla", "country": "Mexico", "region": "Estado de Mexico", "client_type": "municipal",
     "technology": "tratamiento", "lat": 19.54, "lng": -99.19, "water_saved_m3": 1200000, "hectares": 0, "co2_reduced_t": 780,
     "duration_months": 18, "completion_date": date(2024, 11, 2), "is_featured": 1,
     "summary": "Planta de tratamiento de aguas grises para reuso en 9 parques publicos.",
     "description": "Diseno y construccion de una planta modular para tratamiento de aguas grises municipales. El agua tratada se reutiliza para riego de areas verdes y limpieza vial, evitando 1.2M m3/anio de extraccion de pozo."},
    {"name": "Pivot solar Hacienda La Esmeralda", "country": "Colombia", "region": "Valle del Cauca", "client_type": "agro",
     "technology": "pivot", "lat": 3.43, "lng": -76.52, "water_saved_m3": 380000, "hectares": 240, "co2_reduced_t": 620,
     "duration_months": 8, "completion_date": date(2024, 9, 20), "is_featured": 1,
     "summary": "Pivot central de 240 ha alimentado por planta solar de 600 kWp.",
     "description": "Instalacion de dos pivots centrales con sistema fotovoltaico aislado, eliminando consumo electrico de la red para riego.",
     "testimonial_text": "Pasamos a operar con tarifa cero de energia para riego. ROI proyectado en 3.8 años.",
     "testimonial_author": "Maria Ines Lopera - Directora, Hacienda La Esmeralda"},
    {"name": "Cooperativa de cafetaleros Quindio", "country": "Colombia", "region": "Quindio", "client_type": "agro",
     "technology": "drip", "lat": 4.53, "lng": -75.68, "water_saved_m3": 95000, "hectares": 38, "co2_reduced_t": 75,
     "duration_months": 6, "completion_date": date(2023, 12, 5),
     "summary": "Goteo subterraneo en cafetales de altura con calidad de exportacion.",
     "description": "Programa de adopcion tecnologica para 14 fincas asociadas. Resultado: +18% en rendimiento y -32% en consumo hidrico."},
    {"name": "Olivos del Sur - Sistema integral", "country": "Chile", "region": "Region del Maule", "client_type": "agro",
     "technology": "drip", "lat": -35.43, "lng": -71.65, "water_saved_m3": 720000, "hectares": 310, "co2_reduced_t": 540,
     "duration_months": 14, "completion_date": date(2024, 3, 12),
     "summary": "Modernizacion de 310 ha de olivar con fertirriego y monitoreo IoT.",
     "description": "Migracion de aspersion a goteo subterraneo con sensorica avanzada y plataforma de fertirriego automatizado."},
    {"name": "Programa nacional Aguas Rurales Mendoza", "country": "Argentina", "region": "Mendoza", "client_type": "municipal",
     "technology": "tratamiento", "lat": -32.89, "lng": -68.85, "water_saved_m3": 850000, "hectares": 0, "co2_reduced_t": 320,
     "duration_months": 22, "completion_date": date(2024, 8, 1),
     "summary": "Suministro de agua tratada a 12 comunidades rurales de Mendoza.",
     "description": "Diseno y operacion de 12 plantas potabilizadoras compactas para comunidades de hasta 1.500 habitantes."},
    {"name": "Frutales de exportacion Aconcagua", "country": "Chile", "region": "Region de Valparaiso", "client_type": "agro",
     "technology": "drip", "lat": -32.85, "lng": -70.59, "water_saved_m3": 460000, "hectares": 180, "co2_reduced_t": 340,
     "duration_months": 10, "completion_date": date(2024, 5, 18),
     "summary": "Sistema integral de riego y fertirriego para cerezas de exportacion.",
     "description": "Implementacion de plataforma de fertirriego inteligente conectada a sensorica de suelo y estacion meteorologica."},
    {"name": "Recuperacion lago Texcoco", "country": "Mexico", "region": "Estado de Mexico", "client_type": "ambiental",
     "technology": "renovables", "lat": 19.5, "lng": -98.99, "water_saved_m3": 1500000, "hectares": 0, "co2_reduced_t": 1200,
     "duration_months": 30, "completion_date": date(2024, 12, 10),
     "summary": "Consultoria internacional para restauracion hidrica del lago Texcoco.",
     "description": "Lideramos el componente de modelado hidrico y energias renovables del programa de restauracion ambiental."},
    {"name": "Programa Arroz Sostenible Pampas", "country": "Argentina", "region": "Entre Rios", "client_type": "agro",
     "technology": "iot", "lat": -32.49, "lng": -58.23, "water_saved_m3": 920000, "hectares": 540, "co2_reduced_t": 680,
     "duration_months": 16, "completion_date": date(2024, 4, 22),
     "summary": "IoT y modelado para reduccion de huella hidrica en arroz.",
     "description": "Combinamos sensorica, satelite y modelos predictivos para reducir consumo de agua en arroz hasta 35%.",
     "testimonial_text": "Por primera vez podemos cuantificar el agua que ahorramos. Cambia la conversacion con el mercado.",
     "testimonial_author": "Federico Pinto - Productor"},
    {"name": "Distrito de riego Piura", "country": "Peru", "region": "Piura", "client_type": "agro",
     "technology": "pivot", "lat": -5.19, "lng": -80.63, "water_saved_m3": 1100000, "hectares": 420, "co2_reduced_t": 510,
     "duration_months": 20, "completion_date": date(2024, 10, 8),
     "summary": "Modernizacion de distrito de riego con pivot y telemetria.",
     "description": "Reemplazo de canales de tierra por pivots y telemetria centralizada. Eficiencia hidrica subio de 38% a 78%."},
    {"name": "Cultivos hidroponicos Vega Real", "country": "Ecuador", "region": "Pichincha", "client_type": "agro",
     "technology": "iot", "lat": -0.21, "lng": -78.49, "water_saved_m3": 65000, "hectares": 8, "co2_reduced_t": 28,
     "duration_months": 5, "completion_date": date(2023, 11, 14),
     "summary": "Cultivo hidroponico de hortalizas con reuso de nutrientes.",
     "description": "Implementacion de sistema cerrado de fertirriego con reuso de 95% del agua."},
    {"name": "Hub agro-fotovoltaico Caatinga", "country": "Brasil", "region": "Bahia", "client_type": "agro",
     "technology": "renovables", "lat": -12.97, "lng": -38.51, "water_saved_m3": 410000, "hectares": 160, "co2_reduced_t": 480,
     "duration_months": 18, "completion_date": date(2024, 7, 25),
     "summary": "Hub agro-fotovoltaico combinando frutales tropicales y energia solar.",
     "description": "Diseno y operacion de un hub demostrativo de 160 ha con paneles solares elevados sobre cultivos."},
]


TESTIMONIALS = [
    {"client_name": "Carlos Mendoza", "client_role": "Gerente Agricola", "company": "Vinia Santa Cruz",
     "text": "Excelente solucion, reducimos costos de agua un 40% en el primer ciclo y subimos calidad de exportacion.", "rating": 5, "is_featured": True},
    {"client_name": "Maria Ines Lopera", "client_role": "Directora", "company": "Hacienda La Esmeralda",
     "text": "El acompanamiento durante toda la implementacion fue clave. Cumplieron tiempos y presupuesto.", "rating": 5, "is_featured": True},
    {"client_name": "Federico Pinto", "client_role": "Productor de arroz", "company": "Entre Rios",
     "text": "Por primera vez podemos medir y reportar agua ahorrada con datos auditables. Cambia la conversacion con el mercado.", "rating": 5, "is_featured": True},
    {"client_name": "Sandra Velez", "client_role": "Directora de Sostenibilidad", "company": "Grupo AgroInd",
     "text": "Una alianza estrategica de largo plazo. Su capacidad tecnica y de implementacion es de clase mundial.", "rating": 5, "is_featured": True},
    {"client_name": "Ing. Juan Lopez", "client_role": "Director de Obras", "company": "Municipalidad de Tlalnepantla",
     "text": "Pasaron de la consultoria a operar. La planta funciona desde hace 14 meses sin incidentes.", "rating": 5, "is_featured": True},
    {"client_name": "Rosa Diaz", "client_role": "Gerente de Operaciones", "company": "Olivos del Sur",
     "text": "Recuperamos la inversion en menos de 3 años y la calidad del aceite es notablemente mayor.", "rating": 5},
    {"client_name": "Tomas Rivera", "client_role": "Coordinador de Proyectos", "company": "Cooperativa Quindio",
     "text": "Capacitaron a nuestros tecnicos. Hoy operamos el sistema sin dependencia externa.", "rating": 4},
    {"client_name": "Laura Bermudez", "client_role": "Investigadora", "company": "Universidad Nacional",
     "text": "Su division de I+D publica con nosotros. Es de los pocos vendors que invierte en ciencia abierta.", "rating": 5},
]


BLOG_POSTS = [
    {"title": "Crisis global de agua: oportunidades en riego inteligente",
     "category": "Tendencias",
     "excerpt": "Por que la proxima decada sera definitoria para la transicion hidrica y donde se concentran las inversiones.",
     "content": "<p>El agua es ya un activo estrategico. Segun la ONU, la demanda global crecera 30% para 2050...</p><h2>Tres palancas clave</h2><p>Modernizacion de riego, reuso urbano y tratamiento descentralizado son las tres palancas con mejor relacion impacto/inversion.</p><p>En este articulo revisamos cifras recientes y casos en LATAM.</p>",
     "author": "Dra. Lucia Carrasco", "read_time_min": 6, "publish_date": datetime(2025, 11, 14)},
    {"title": "Sensorica LoRa en agricultura: 5 lecciones del campo",
     "category": "Tecnologia",
     "excerpt": "Lecciones operativas tras desplegar mas de 1.200 nodos LoRa en cultivos de 4 paises.",
     "content": "<p>LoRa nos ha permitido densificar la sensorica con un costo de operacion sostenible.</p><h2>1. Colocacion del gateway importa mas que el modelo</h2><p>La altura y la linea de vista determinan el 80% del alcance util.</p><h2>2. Bateria reportada vs. real</h2><p>Las cifras de catalogo asumen un duty cycle minimo; en campo, recalculamos a 60% del catalogo.</p>",
     "author": "Ing. Mateo Diaz", "read_time_min": 8, "publish_date": datetime(2026, 1, 8)},
    {"title": "Como construimos una calculadora ROI confiable",
     "category": "Consultoria",
     "excerpt": "Detras de la herramienta interactiva: variables, sensibilidad y el rol del cliente en la calibracion.",
     "content": "<p>Una calculadora ROI no es una caja magica. Es un modelo que necesita ser explicado, calibrado y revisado.</p><h2>Variables clave</h2><p>Inversion CAPEX, costo del agua, productividad incremental y horizonte temporal.</p>",
     "author": "Ana Rojas, PhD", "read_time_min": 5, "publish_date": datetime(2025, 9, 22)},
    {"title": "El distrito de riego Piura: de 38% a 78% de eficiencia",
     "category": "Casos",
     "excerpt": "Resumen del proyecto que modernizo un distrito de 420 ha con pivots y telemetria.",
     "content": "<p>El distrito de riego de Piura operaba con canales de tierra y eficiencia hidrica del 38%. Hoy esta sobre 78%.</p><h2>Que cambiamos</h2><p>Pivots centrales, telemetria de caudal y plataforma de operacion remota.</p>",
     "author": "Equipo Aqua-Terra", "read_time_min": 7, "publish_date": datetime(2025, 12, 2)},
    {"title": "Reuso urbano: aprendizajes de Tlalnepantla",
     "category": "Casos",
     "excerpt": "Como diseñamos una planta de aguas grises que riega 9 parques publicos.",
     "content": "<p>El proyecto de Tlalnepantla nos ensenio que la institucionalidad pesa tanto como el diseno tecnico.</p>",
     "author": "Sofia Linares", "read_time_min": 6, "publish_date": datetime(2025, 8, 30)},
    {"title": "Energia solar para bombeo: cuando si y cuando no",
     "category": "Tecnologia",
     "excerpt": "Una guia practica para decidir si conviene un sistema solar para bombeo agricola.",
     "content": "<p>Las bombas solares pueden tener payback de 3-5 años. Pero no son universales.</p><h2>Donde si funciona</h2><p>Tarifas electricas altas, baja sombra, riego diurno predecible.</p>",
     "author": "Ing. Mateo Diaz", "read_time_min": 5, "publish_date": datetime(2026, 2, 18)},
]


def seed_if_empty(db: Session) -> None:
    existing = db.query(Category).count()
    if existing:
        logger.info("Seed skipped: %s categorias ya existen.", existing)
        return
    do_seed(db)


def do_seed(db: Session) -> None:
    logger.info("Seeding initial data...")
    cat_map: dict[str, Category] = {}
    for c in CATEGORIES:
        cat = Category(**c)
        db.add(cat)
        cat_map[c["slug"]] = cat
    db.flush()

    for p in PRODUCTS:
        cat = cat_map[p["category"]]
        prod = Product(
            slug=slugify(p["name"]),
            name=p["name"],
            short_description=p["short_description"],
            description=p.get("description") or f'{p["short_description"]} Producto disenado para condiciones reales de campo, con soporte tecnico regional y garantia oficial.',
            price=p["price"],
            currency="USD",
            image_url=p.get("image_url", ""),
            in_stock=p.get("in_stock", True),
            rating=p.get("rating", 4.5),
            reviews_count=p.get("reviews_count", 18),
            is_featured=p.get("is_featured", False),
            specifications=p.get("specifications", {}),
            features=p.get("features", []),
            bulk_discount=p.get("bulk_discount", {}),
            tech_tags=p.get("tech_tags", []),
            category=cat,
        )
        db.add(prod)

    for pr in PROJECTS:
        proj = Project(
            slug=slugify(pr["name"]),
            name=pr["name"],
            summary=pr["summary"],
            description=pr["description"],
            country=pr["country"],
            region=pr["region"],
            latitude=pr["lat"],
            longitude=pr["lng"],
            client_type=pr["client_type"],
            technology=pr["technology"],
            water_saved_m3=pr["water_saved_m3"],
            hectares=pr["hectares"],
            co2_reduced_t=pr["co2_reduced_t"],
            duration_months=pr["duration_months"],
            completion_date=pr["completion_date"],
            testimonial_text=pr.get("testimonial_text", ""),
            testimonial_author=pr.get("testimonial_author", ""),
            is_featured=pr.get("is_featured", 0),
        )
        db.add(proj)

    for t in TESTIMONIALS:
        db.add(Testimonial(**t))

    for b in BLOG_POSTS:
        db.add(BlogPost(
            slug=slugify(b["title"]),
            title=b["title"],
            excerpt=b["excerpt"],
            content=b["content"],
            category=b["category"],
            author=b["author"],
            read_time_min=b["read_time_min"],
            publish_date=b["publish_date"],
        ))

    db.commit()
    logger.info("Seed completed: %s products, %s projects, %s testimonials, %s posts",
                len(PRODUCTS), len(PROJECTS), len(TESTIMONIALS), len(BLOG_POSTS))


def reset_and_seed() -> None:
    logger.info("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        do_seed(db)
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    if "--reset" in sys.argv:
        reset_and_seed()
    else:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_if_empty(db)
        finally:
            db.close()
