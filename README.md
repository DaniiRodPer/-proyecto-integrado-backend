# Backend del proyecto integrado

## Requisitos para la Ejecución

Para levantar este servidor en local, asegúrate de cumplir con lo siguiente:

### 1. Base de Datos (MariaDB)
- Tener instalado **MariaDB**.
- Crear una base de datos vacía.
- Configurar en el fichero .env:
  - Host, Nombre, Usuario y contraseña de la Base de Datos
  - Usuario y contraseña del servicio de email
  - IP del equipo servidor y puerto en el que se alojará

### 2. Entorno Python (MariaDB / MySQL)

- Crear el entorno (Linux)
  
  ```python
  python3 -m venv venv

- Crear el entorno (Linux)
  
  ```python
  python -m venv venv

- Activar el entorno (Linux)
  
  ```python
  source venv/bin/activate

- Activar el entorno (Windows)
  
   ```python
  venv\Scripts\activate

### 3. Instalar dependencias

  ```bash
   pip install -r requirements.txt
  ```

### 4. Iniciar el servidor

   ```python
  uvicorn app.main:app --host 0.0.0.0
  ```

- Nota: Usar --host 0.0.0.0 es fundamental para que el emulador de Android pueda comunicarse con el servidor.
