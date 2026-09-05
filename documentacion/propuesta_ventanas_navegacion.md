# Dashboard de Entrenamiento - Ventanas


## Navegación Principal

La aplicación estará compuesta inicialmente por cuatro pantallas:

1. Inicio
2. Calendario
3. Detalle del Día
4. Histórico del Ejercicio

Flujo de navegación:

```text
Inicio

Calendario
   ↓
Detalle del Día
   ↓
Histórico del Ejercicio
```

---

# 1. Pantalla de Inicio

Será la pantalla principal y la más utilizada.

## Próximo Entrenamiento

Mostrar:

- Hoy / Mañana / Dentro de X días.
- Nombre o tipo de sesión.
- Lista resumida de ejercicios.

Ejemplo:

```text
Mañana

Fuerza - Tren Superior

- Press banca
- Remo barra
- Press militar
- Fondos
```

## Último Entrenamiento

Mostrar:

- Fecha.
- Tipo de entrenamiento.
- Duración.
- Volumen total.
- Número de ejercicios.

Ejemplo:

```text
Miércoles 14 Mayo

Fuerza - Piernas

Duración: 1h 20m
Volumen: 12.450 kg
Ejercicios: 6
```

## Resumen General

Selector de periodo:

- Semana
- Mes
- Año
- Histórico

Métricas mostradas:

- Número de entrenamientos.
- Volumen total.
- Horas entrenadas.
- Distancia recorrida (si aplica).

## Calendario Compacto

Pequeña vista del mes actual para acceder rápidamente al calendario completo.

---

# 2. Pantalla de Calendario

Vista mensual completa.

Cada día puede tener uno de los siguientes estados:

- Entrenamiento realizado.
- Entrenamiento planificado.
- Descanso.

Al pulsar sobre una fecha se abrirá la pantalla de detalle correspondiente.

---

# 3. Pantalla de Detalle del Día

Información completa de una sesión concreta.

## Cabecera

Mostrar:

- Fecha.
- Duración.
- Volumen total.

## Ejercicios Realizados

Listado de ejercicios ejecutados.

Ejemplo:

```text
Sentadilla
4x8 100 kg

Peso muerto
3x5 140 kg

Gemelos
3x15 80 kg
```

Al pulsar un ejercicio se abrirá su histórico.

## Mapa Muscular

Representación frontal y trasera del cuerpo.

Colores:

- Rojo: músculo principal.
- Amarillo: músculo secundario.
- Gris: músculo no trabajado.

El objetivo es ofrecer una visualización rápida de las zonas entrenadas durante la sesión.

---

# 4. Pantalla de Histórico del Ejercicio

Pantalla centrada en la evolución de un ejercicio concreto.

Ejemplo:

### Press banca

```text
15/05/2026   100 kg
08/05/2026    97.5 kg
01/05/2026    95 kg
24/04/2026    92.5 kg
```

## Métricas

Mostrar:

- Máximo peso registrado.
- 1RM estimado.

## Gráfico de Evolución

Representación visual de la progresión del ejercicio a lo largo del tiempo.

El gráfico debe permitir detectar rápidamente:

- Mejoras.
- Estancamientos.
- Retrocesos.

