# Incorporar el proyecto al GitHub del equipo

Los archivos se prepararon a partir del repositorio compartido. No se subieron cambios porque el entorno no tiene autenticación de escritura en GitHub.

1. Descarga y extrae el ZIP. No trabajes dentro del archivo comprimido.
2. Si ya tienes el repositorio clonado, abre esa carpeta en VS Code. Si no, ejecuta en una terminal:

```powershell
git clone https://github.com/laurat2025/Caso_Accidentes.git
cd Caso_Accidentes
```

3. Copia el contenido de la carpeta extraída dentro de la carpeta del repositorio local. Conserva su carpeta `.git`. Incluye el archivo `.gitignore`.
4. Ejecuta los comandos del README para revisar la carga, las pruebas y el notebook.
5. Crea una rama y revisa qué archivos vas a subir:

```powershell
git switch -c primera-entrega-etl
git add README.md .gitignore requirements.txt src sql notebooks reports docs tests data/raw data/processed/.gitkeep
git diff --cached --stat
git status
```

6. Si los archivos corresponden al trabajo revisado, registra y sube el cambio:

```powershell
git commit -m "Implementa ETL, modelo estrella y EDA de mortalidad"
git push -u origin primera-entrega-etl
```

7. En GitHub abre la rama y crea un pull request para revisión del equipo. Si tu cuenta no tiene permiso de escritura, la dueña del repositorio debe darte acceso o el equipo debe trabajar mediante un fork.

No subas `.venv`, la base SQLite ni cachés. La base incluida en el ZIP sirve para consultar los resultados de inmediato; el ETL la regenera. El mínimo de registros analíticos y la lista de integrantes siguen siendo asuntos de la entrega que deben resolver antes de presentarla.
