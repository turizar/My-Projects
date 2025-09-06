# Buscador de Centros Deportivos Santiago

Una aplicación web para buscar y filtrar centros deportivos en Santiago, Chile.

## Tecnologías Utilizadas

- Frontend: React.js
- Backend: Laravel
- Base de datos: MySQL

## Requisitos

- Node.js (v14 o superior)
- PHP 8.1 o superior
- Composer
- MySQL

## Instalación

### Backend (Laravel)

1. Clonar el repositorio
2. Navegar al directorio del proyecto
3. Instalar dependencias de PHP:
```bash
composer install
```
4. Copiar el archivo .env.example a .env y configurar la base de datos
5. Generar la clave de la aplicación:
```bash
php artisan key:generate
```
6. Ejecutar las migraciones:
```bash
php artisan migrate
```
7. Iniciar el servidor:
```bash
php artisan serve
```

### Frontend (React)

1. Navegar al directorio frontend:
```bash
cd frontend
```
2. Instalar dependencias:
```bash
npm install
```
3. Iniciar el servidor de desarrollo:
```bash
npm start
```

## Características

- Búsqueda de centros deportivos
- Filtrado por deportes
- Filtrado por ubicación
- Filtrado por precio
- Vista detallada de cada centro deportivo
- Mapa interactivo con la ubicación de los centros 