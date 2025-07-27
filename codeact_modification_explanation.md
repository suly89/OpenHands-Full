# Mejora del CodeAct Agent: Implementación de Planificación Previa

## Contexto y Motivación

El **CodeAct Agent** de OpenHands es una implementación robusta que combina capacidades conversacionales con ejecución de código mediante un sistema unificado de acciones. Sin embargo, en su estado actual, el agente tiende a comenzar la implementación inmediatamente después de recibir una solicitud, lo que puede llevar a:

- **Malentendidos en los requisitos**: El agente puede interpretar incorrectamente lo que el usuario realmente necesita
- **Falta de transparencia**: El usuario no sabe exactamente qué va a hacer el agente hasta que ya está ejecutando
- **Retrabajos innecesarios**: Cambios de dirección a mitad del desarrollo por falta de alineación inicial
- **Experiencia de usuario subóptima**: Sensación de falta de control sobre el proceso de desarrollo

## Objetivo de la Mejora

**No se trata de crear un agente completamente nuevo**, sino de **mejorar el comportamiento del CodeAct Agent existente** para que adopte un enfoque más estructurado y colaborativo. Específicamente, queremos que el agente:

1. **Pause antes de programar**: No ejecute código inmediatamente tras recibir una solicitud
2. **Analice y planifique**: Dedique tiempo a entender completamente los requisitos
3. **Presente un plan claro**: Muestre al usuario exactamente qué va a hacer y cómo
4. **Solicite aprobación explícita**: Espere confirmación antes de proceder con la implementación
5. **Mantenga su funcionalidad actual**: Conserve todas sus capacidades de ejecución y herramientas

## Enfoque de Implementación

### Modificación del Flujo de Trabajo Existente

En lugar de alterar la arquitectura fundamental del CodeAct Agent, la mejora se implementa como una **capa de procesamiento adicional** que se activa antes del comportamiento normal del agente:

```
Solicitud del Usuario
         ↓
   [NUEVA CAPA]
   Análisis y Planificación
         ↓
   Presentación del Plan
         ↓
   Espera de Aprobación
         ↓
   [FLUJO EXISTENTE]
   Ejecución del CodeAct Agent
```

### Componentes de la Mejora

#### 1. **Estado de Planificación**
- Añadir un nuevo estado al agente: `PLANNING_MODE`
- Cuando está en este modo, el agente se enfoca en análisis en lugar de ejecución
- Una vez aprobado el plan, cambia a `EXECUTION_MODE` (comportamiento actual)

#### 2. **Prompts de Planificación**
- Integrar prompts especializados que guíen al agente a:
  - Analizar requisitos antes de actuar
  - Estructurar una respuesta de planificación
  - Presentar información de manera clara y organizada

#### 3. **Lógica de Aprobación**
- Implementar detección de respuestas de aprobación del usuario
- Gestionar modificaciones al plan según feedback
- Mantener el contexto del plan durante la ejecución

#### 4. **Reporting de Progreso**
- Modificar las acciones de ejecución para reportar progreso según el plan
- Mantener al usuario informado de qué parte del plan se está ejecutando

## Cambios Específicos Propuestos

### En el Archivo Principal del Agente

**Modificación mínima del método `step()`:**
```python
async def step(self, state: State) -> Action:
    # Detectar si es una nueva solicitud de desarrollo
    if self._is_new_development_request(state) and not self._has_approved_plan(state):
        return await self._handle_planning_phase(state)

    # Si ya hay un plan aprobado, proceder con lógica original
    return await self._original_step_logic(state)
```

### Nuevos Métodos de Planificación

**Funciones añadidas sin alterar las existentes:**
- `_handle_planning_phase()`: Genera y presenta el plan
- `_is_development_request()`: Detecta solicitudes que requieren código
- `_has_approved_plan()`: Verifica si ya hay aprobación
- `_format_plan_presentation()`: Estructura la presentación del plan

### Prompts Mejorados

**Extensión de los prompts existentes** para incluir:
- Instrucciones de planificación cuando corresponda
- Formato específico para presentación de planes
- Criterios para detectar aprobación del usuario

## Beneficios de Este Enfoque

### Para el Usuario
1. **Mayor control**: Ve y aprueba lo que va a suceder antes de que ocurra
2. **Transparencia completa**: Entiende el proceso y las decisiones técnicas
3. **Menos frustraciones**: Evita malentendidos y retrabajos
4. **Experiencia más profesional**: Simula el flujo de trabajo de desarrollo real

### Para el Sistema
1. **Compatibilidad total**: No rompe funcionalidad existente
2. **Implementación gradual**: Se puede activar/desactivar según necesidades
3. **Mantenimiento simplificado**: Cambios mínimos al código base
4. **Extensibilidad**: Base para futuras mejoras de planificación

### Para el Desarrollo
1. **Calidad mejorada**: Mejor planificación lleva a mejor código
2. **Eficiencia aumentada**: Menos iteraciones por malentendidos
3. **Documentación automática**: El plan sirve como documentación del proceso
4. **Trazabilidad**: Historial claro de decisiones y aprobaciones

## Implementación Práctica

### Fase 1: Integración Básica (1-2 días)
- Añadir lógica de detección de solicitudes de desarrollo
- Implementar presentación básica de planes
- Integrar sistema de aprobación simple

### Fase 2: Refinamiento (2-3 días)
- Mejorar la calidad de los análisis de requisitos
- Añadir estimaciones de tiempo más precisas
- Implementar manejo de modificaciones al plan

### Fase 3: Optimización (1-2 días)
- Ajustar prompts basado en casos de uso reales
- Optimizar detección de tipos de solicitud
- Añadir métricas de satisfacción del usuario

## Ejemplo de Flujo Mejorado

**Antes (Comportamiento Actual):**
```
Usuario: "Crea una API REST para gestionar usuarios"
Agente: "Voy a crear una API REST. Empezaré configurando FastAPI..."
[Comienza a programar inmediatamente]
```

**Después (Comportamiento Mejorado):**
```
Usuario: "Crea una API REST para gestionar usuarios"
Agente: "Entiendo que quieres una API REST para gestión de usuarios.
         Déjame analizar los requisitos y presentarte un plan detallado.

📋 PLAN DE DESARROLLO
[Plan estructurado con tareas, tecnologías, y estimaciones]

¿Apruebas este plan para proceder?"

Usuario: "Sí, perfecto"
Agente: "Excelente, comenzaré con la implementación siguiendo el plan..."
[Procede con la ejecución normal pero reportando progreso]
```

## Conclusión

Esta mejora transforma el CodeAct Agent de un **ejecutor reactivo** a un **colaborador proactivo**, manteniendo toda su potencia técnica mientras añade una capa de planificación y validación que mejora significativamente la experiencia del usuario y la calidad de los resultados.

La implementación es **no invasiva**, **compatible con el código existente**, y **fácil de mantener**, lo que la convierte en una mejora de bajo riesgo con alto impacto en la usabilidad del sistema.
