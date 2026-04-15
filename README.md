# AutoDoc

AutoDoc es una herramienta diseñada para la verificación automatizada de la consistencia entre la documentación Javadoc y la implementación de métodos en proyectos desarrollados en el lenguaje Java. El sistema se integra dentro de pipelines de integración continua (CI/CD) mediante GitHub Actions, combinando técnicas de análisis estático con modelos de inteligencia artificial para mejorar la calidad documental del software.

El objetivo principal de AutoDoc es garantizar que la documentación asociada a los métodos del código fuente sea coherente, completa y útil tanto para desarrolladores como para mantenedores del sistema.

---

## Arquitectura del sistema

AutoDoc se basa en una arquitectura de tipo pipeline desacoplado, donde cada componente realiza una transformación específica sobre los datos.

El flujo de procesamiento es:
changed_files → java_extractor → normalizer → rules → ai_evaluator → decision_engine → report

---

## Estados de validación

AutoDoc define tres estados:

- PASS: documentación consistente
- FAIL: error crítico (bloquea merge)
- NEEDS REVIEW: requiere intervención humana

Debido a que GitHub Actions solo soporta estados binarios, AutoDoc utiliza múltiples checks para modelar este comportamiento.

---

## Integración en otros repositorios

AutoDoc no se integra como código dentro del proyecto, sino como herramienta externa mediante GitHub Actions.

Para utilizarlo:

1. Crear el archivo:
.github/workflows/doc-check.yml

---

## Configuración de Gemini

### Obtener API Key

Ir a:

https://aistudio.google.com/app/apikey

Generar una nueva clave.

---

### Configuración local

Linux / Mac:
export GEMINI_API_KEY="tu_api_key"

Windows:
setx GEMINI_API_KEY "tu_api_key"

---

### Configuración en GitHub

Ir a:
Repository → Settings → Secrets and variables → Actions

Crear:
Name: GEMINI_API_KEY
Value: <tu_api_key>

---

## Control de integración

- PASS → permite merge
- FAIL → bloquea merge
- NEEDS REVIEW → bloquea hasta override

---

## Override manual

Para desbloquear NEEDS REVIEW:

1. Ir a:
Repository → Actions

2. Seleccionar el workflow

3. Click en:
Run workflow

4. Configurar:
override = true

---

## Control de acceso

Configurado en:
policy/ci-policy.yaml

Ejemplo:

```yaml
override:
  enabled: true
  allowed_users:
    - tech-lead
    - architect

Documentación generada

AutoDoc genera:
reports/output.json
reports/output.pdf
docs/index.html

Publicación en GitHub Pages

Ir a:
Settings → Pages

Configurar:
Source: Deploy from branch
Branch: main
Folder: /docs

La documentación queda disponible en:
https://usuario.github.io/repositorio

Tags soportados

Obligatorios:

@param
@return
@throws
descripción o @purpose

Extendidos:

@example
@uses
@precondition
@postcondition
@sideEffects
@businessRule
@ticket
@requirements
@notes
@since

Testing

Ejecutar:
pytest