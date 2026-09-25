# Plataforma Olga de Chica

Plataforma para la **sistematización, consulta, navegación y visualización de relaciones** de la colección documental asociada a Olga de Chica.

El sistema busca organizar información sobre filminas, bocetos y recursos relacionados, preservando su procedencia, información descriptiva y relaciones dentro de la colección.

## Estado del proyecto

El proyecto se encuentra en etapa inicial de desarrollo. Actualmente se está construyendo la primera versión funcional mediante un enfoque incremental y basado en **TDD (Test-Driven Development)**.

## Objetivos principales

* Registrar y consultar filminas, bocetos y recursos.
* Mantener la procedencia de los materiales.
* Asociar archivos digitales cuando estén disponibles.
* Clasificar elementos mediante tags reutilizables.
* Establecer y consultar relaciones entre los elementos de la colección.
* Facilitar la exploración de la colección mediante búsquedas, filtros y visualización de relaciones.
* Permitir posteriormente la selección y organización de materiales para actividades de investigación y socialización.

## Arquitectura

Se decidió implementar el sistema como un **monolito modular basado en capas (Layered Modular Monolith)**.

La arquitectura se organiza en cuatro capas:

```text
Presentación
      ↓
Aplicación
      ↓
Dominio
      ↓
Persistencia
```

### Capas

* **Presentación:** interfaz de usuario, vistas y controladores.
* **Aplicación:** implementación de los casos de uso y gestión de las funcionalidades.
* **Dominio:** entidades y reglas propias del problema.
* **Persistencia:** almacenamiento de metadatos, relaciones y archivos digitales en el sistema de archivos local.

La arquitectura busca mantener separadas las responsabilidades y permitir que las decisiones de infraestructura no condicionen el modelo del dominio.

Más información: [Arquitectura](../../wiki/Arquitectura)

## Modelo de dominio

Las principales entidades del dominio son:

* `Filmina`
* `Boceto`
* `Recurso`
* `Tag`
* `Archivo`

Una **Selección** no se modela como una entidad del dominio. Se considera una funcionalidad de la capa de aplicación que permite agrupar y consultar materiales existentes de la colección.

### Reglas de `Filmina`

Una `Filmina` contiene:

* un identificador de negocio;
* una descripción obligatoria;
* una fecha;
* una procedencia obligatoria;
* un archivo digital opcional;
* hasta tres tags, sin repetirlos;
* bocetos relacionados.

El archivo digital puede asociarse posteriormente cuando esté disponible. La entidad `Archivo` representa sus metadatos y su ruta relativa; el contenido binario se administra en la capa de persistencia.

### Caso de uso `RegistrarFilmina`

`RegistrarFilmina` pertenece a la capa de aplicación. Su método `ejecutar` recibe los datos del registro, solicita al generador el identificador de negocio, crea la entidad `Filmina` y la entrega al repositorio para guardarla.

El caso de uso no depende de una implementación concreta de almacenamiento. En las pruebas unitarias se utiliza un repositorio en memoria; en producción se utilizará un repositorio conectado a la persistencia de la aplicación.

### Separación entre dominio y persistencia

Se decidió separar el **modelo de dominio** del **modelo de persistencia**.

Las entidades de dominio representan los conceptos y reglas del problema independientemente de la tecnología utilizada para almacenarlos.

Los modelos de persistencia representan la forma en que esas entidades son almacenadas en la base de datos mediante SQLAlchemy.

El flujo esperado es:

```text
Entidad de dominio
       ↓
   Repositorio
       ↓
Modelo de persistencia
       ↓
   SQLAlchemy
       ↓
     SQLite
```

y, en sentido inverso, al consultar información:

```text
SQLite
   ↓
SQLAlchemy
   ↓
Modelo de persistencia
   ↓
Repositorio
   ↓
Entidad de dominio
```

Esta separación permite que las reglas del dominio no dependan directamente de SQLite o SQLAlchemy.

Más información: [Modelo de dominio](../../wiki/Modelo-de-dominio)

## Tecnologías

| Tecnología                    | Uso                            |
| ----------------------------- | ------------------------------ |
| Python                        | Lenguaje principal             |
| Flask                         | Aplicación web                 |
| SQLAlchemy / Flask-SQLAlchemy | Persistencia y ORM             |
| SQLite                        | Base de datos local            |
| HTML / Jinja                  | Vistas                         |
| CSS                           | Estilos                        |
| JavaScript                    | Interactividad y visualización |
| `unittest`                    | Pruebas                        |
| Faker                         | Generación de datos de prueba  |

## Desarrollo basado en TDD

El desarrollo sigue el ciclo:

```text
RED → GREEN → REFACTOR
```

Antes de implementar una funcionalidad se define el comportamiento esperado y se escribe una prueba que inicialmente debe fallar.

Por ejemplo, para `Filmina`:

```text
Definir comportamiento
        ↓
Escribir test_crear_filmina
        ↓
RED ❌
        ↓
Implementar Filmina
        ↓
GREEN ✅
        ↓
REFACTOR
```

Las pruebas utilizan `unittest`. Faker se utiliza para generar datos de prueba cuando resulta útil, pero no reemplaza la definición explícita de los comportamientos que deben verificarse.

Más información: [Pruebas](../../wiki/Pruebas)

## Primer comportamiento implementado

El desarrollo de la entidad `Filmina` comenzó definiendo su comportamiento mínimo.

Una Filmina puede ser creada como una instancia de la entidad de dominio con su identificador de negocio, descripción, fecha y procedencia. El archivo es opcional y los tags y bocetos se asocian mediante comportamientos del dominio.

El identificador de negocio es diferente del identificador técnico que posteriormente pueda asignar la base de datos. El usuario no diligencia ninguno de los dos.

## Almacenamiento de archivos

Los archivos digitales se guardan en el sistema de archivos local del computador donde se ejecuta Flask. La capa de persistencia administra el contenido binario y devuelve una entidad `Archivo` con sus metadatos.

La ruta física esperada es:

```text
instance/
└── storage/
        └── filminas/
                └── F001/
                        └── archivo.jpg
```

`Archivo.ruta` conserva una ruta relativa, por ejemplo:

```text
filminas/F001/archivo.jpg
```

La ruta absoluta se construye a partir de la carpeta de almacenamiento configurada por la aplicación. No se guardan rutas absolutas del computador del usuario en el dominio ni en la base de datos.

El almacenamiento de archivos y el almacenamiento de metadatos son responsabilidades de persistencia diferentes:

```text
Contenido binario  → sistema de archivos local
Metadatos y relaciones → SQLite mediante SQLAlchemy
```

## Datos de prueba

Los datos ficticios para las pruebas pueden generarse mediante Faker.

Se definió un fixture para generar múltiples conjuntos de datos de Filminas, manteniendo una semilla fija para permitir la reproducibilidad de las pruebas.

Ejemplo conceptual:

```text
tests/
└── fixtures/
    └── filminas.py
```

Los fixtures generan datos de prueba; no representan directamente las entidades de dominio.

## Estructura actual del proyecto

```text
plataforma-olga/
├── app/
│   ├── __init__.py
│   ├── application/
│   │   ├── generador_identificadores.py
│   │   └── registrar_filmina.py
│   ├── domain/
│   │   ├── archivo.py
│   │   ├── boceto.py
│   │   ├── enums.py
│   │   ├── filmina.py
│   │   ├── recurso.py
│   │   └── tag.py
│   ├── persistence/
│   │   ├── almacenamiento_archivos_local.py
│   │   ├── repositorio_filminas.py
│   │   └── modelos/
│   │       ├── modelo_archivo.py
│   │       └── modelo_filmina.py
│   └── presentation/
│       ├── controladores/
│       │   └── controlador_filminas.py
│       └── templates/
│           └── filminas/
│               └── formulario.html
├── instance/
│   ├── olga.db
│   └── storage/
├── tests/
│   ├── unit/
│   │   ├── application/
│   │   ├── domain/
│   │   ├── persistence/
│   │   └── presentation/
│   ├── integration/
│   │   └── persistence/
│   └── functional/
├── run.py
├── requirements.txt
└── README.md
```

La estructura se mantendrá sencilla y podrá evolucionar a medida que aparezcan nuevas necesidades.

## Ejecución en desarrollo

Crear y activar un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Inicializar o actualizar el esquema de la base de datos:

```bash
alembic upgrade head
```

Ejecutar la aplicación:

```bash
python run.py
```

## Ubicación de los datos

La aplicación, Alembic y la herramienta de migración comparten
`app/configuracion.py`. La carpeta contiene `olga.db`, `storage/` y los respaldos:

- `OLGA_DATA_DIR` permite definir una carpeta para todos los puntos de entrada.
- En Windows se usa por defecto `%LOCALAPPDATA%\OlgaDeChica`.
- En desarrollo en otros sistemas se usa `instance/` en la raíz del proyecto,
  independientemente del directorio desde el que se ejecute el comando.
- `OlgaMigracion.exe --data-dir RUTA` tiene prioridad para esa migración.
  Si se usa una ruta personalizada, configura también `OLGA_DATA_DIR` al iniciar
  la aplicación.

Los recursos empaquetados de Alembic se buscan dentro del paquete; los datos
persistentes nunca se guardan allí. Las rutas personalizadas se expanden y se
convierten en absolutas; las relativas se interpretan desde el directorio actual.
`ALEMBIC_DATABASE_URL` deja de utilizarse: configura `OLGA_DATA_DIR` para evitar
que Alembic y la aplicación apunten a bases distintas.

## Ejecutar las pruebas

Desde la raíz del proyecto:

```bash
python -m unittest discover tests -v
```

Las pruebas unitarias se ejecutan sin depender de una base de datos real. Para probar el almacenamiento local se utiliza un directorio temporal, que se elimina al terminar cada prueba. Las pruebas de integración utilizarán una base de datos de prueba para verificar la interacción con SQLAlchemy.

La herramienta de migración solo acepta bases que ya tienen la tabla `alembic_version`.

Las futuras modificaciones del esquema deben hacerse mediante nuevas revisiones de Alembic. `Base.metadata.create_all()` no se ejecuta al iniciar la aplicación.

## Integración continua

El workflow de GitHub Actions ejecuta Black y la suite de pruebas cuando se hace `push` a `main` o a una rama `feature/**`.

Los tags con formato `vX.Y.Z` generan además un paquete versionado y una GitHub Release. El paquete no incluye `instance/`, porque allí viven la base de datos y los archivos de los usuarios. El procedimiento de migración, respaldo, actualización y rollback está documentado en [Migración y entrega continua](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Migracion-y-entrega-continua).

## Documentación

La documentación detallada del proyecto se encuentra en el **GitHub Wiki**.

* [Visión y alcance](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Vision-y-alcance)
* [Requisitos](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Requisitos)
* [Historias de usuario](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Historias-de-usuario)
* [Arquitectura](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Arquitectura)
* [Modelo de dominio](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Modelo-de-dominio)
* [Diseño técnico](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Diseno-tecnico)
* [Pruebas](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Pruebas)
* [Estructura del proyecto](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Estructura-del-proyecto)
* [Flujo de trabajo Git](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Flujo-de-trabajo-Git)
* [Instalación y distribución](https://github.com/ibeltran1999/OlgadeChicaApp/wiki/Instalacion-y-distribucion)

## Principios de desarrollo

El proyecto seguirá los siguientes principios:

* Desarrollo incremental.
* TDD para las funcionalidades principales.
* Separación de responsabilidades.
* Independencia del dominio frente a la persistencia.
* Código y datos separados.
* Pruebas automatizadas y reproducibles.
* Cambios pequeños y verificables.
* Trazabilidad entre historias de usuario, pruebas e implementación.
* Evitar complejidad prematura.

## Inicio de la aplicación instalada

Al abrir OlgaDeChica se inicia Waitress en `127.0.0.1:5000` y se abre el
navegador predeterminado cuando la página responde. El ejecutable principal
no muestra consola. Los errores se registran en `aplicacion.log` dentro de
la carpeta de datos (por defecto, `%LOCALAPPDATA%\OlgaDeChica` en Windows).

Cerrar la pestaña no detiene el servidor. Para cerrarlo por completo en Windows,
finaliza `OlgaDeChica.exe` desde el Administrador de tareas antes de volver a
iniciarlo o actualizarlo. Si el puerto 5000 ya está ocupado, el nuevo proceso
termina y registra el error. En desarrollo, `python run.py` utiliza el mismo
arranque; se puede detener con Ctrl+C.

### Numeración de filminas

El siguiente identificador se calcula a partir del mayor número guardado en
`filminas`. El cálculo y el registro comparten una transacción de escritura,
para evitar duplicados entre solicitudes simultáneas. Reiniciar la aplicación
no reinicia la numeración. No se requiere una migración ni tablas adicionales.

Los identificadores anteriores no numéricos se conservan y no participan en el
cálculo. Un registro revertido no consume el número. Si se elimina manualmente
la filmina con el mayor número, ese número puede volver a utilizarse.
