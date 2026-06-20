-- schema.sql — Estructura de la base de datos TalentBoard
-- Ejecútalo en MySQL Workbench si necesitas (re)crear las tablas.

CREATE DATABASE IF NOT EXISTS talentboard;
USE talentboard;

CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    correo VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    rol ENUM('administrador', 'empresa', 'candidato') NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Candidatos (
    id_candidato INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    especialidad VARCHAR(100),
    url_cv VARCHAR(255),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Empresas (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre_empresa VARCHAR(150) NOT NULL,
    descripcion TEXT,
    aprobada BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE Vacantes (
    id_vacante INT AUTO_INCREMENT PRIMARY KEY,
    id_empresa INT NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    salario DECIMAL(10,2),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    activa BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_empresa) REFERENCES Empresas(id_empresa) ON DELETE CASCADE
);

CREATE TABLE Postulaciones (
    id_postulacion INT AUTO_INCREMENT PRIMARY KEY,
    id_candidato INT NOT NULL,
    id_vacante INT NOT NULL,
    estado ENUM('pendiente', 'revisado', 'aceptado', 'rechazado') DEFAULT 'pendiente',
    fecha_postulacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_candidato) REFERENCES Candidatos(id_candidato) ON DELETE CASCADE,
    FOREIGN KEY (id_vacante) REFERENCES Vacantes(id_vacante) ON DELETE CASCADE
);

-- Usuario administrador de ejemplo.
-- OJO: la contraseña debe ir HASHEADA con bcrypt para poder iniciar sesión.
-- Genera el hash con:
--   python -c "import bcrypt; print(bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode())"
-- y pégalo abajo en lugar de '123456'.
INSERT INTO Usuarios (correo, password, rol)
VALUES ('usuariosadmin1@test.com', '123456', 'administrador');
