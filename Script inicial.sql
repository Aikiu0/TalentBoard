-- ============================================================
-- TalentBoard – Script DDL v1.0
-- Base de Datos: talentboard_db
-- Motor: MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS talentboard_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE talentboard_db;

-- ------------------------------------------------------------
-- Tabla: users
-- Entidad base de autenticación para todos los roles
-- ------------------------------------------------------------
CREATE TABLE users (
  id            INT             NOT NULL AUTO_INCREMENT,
  email         VARCHAR(191)    NOT NULL,
  password_hash VARCHAR(255)    NOT NULL,
  role          ENUM('admin','graduate','company') NOT NULL DEFAULT 'graduate',
  is_active     BOOLEAN         NOT NULL DEFAULT TRUE,
  created_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_users_email (email)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: graduate_profiles
-- Perfil extendido del egresado
-- ------------------------------------------------------------
CREATE TABLE graduate_profiles (
  id              INT           NOT NULL AUTO_INCREMENT,
  user_id         INT           NOT NULL,
  full_name       VARCHAR(150)  NOT NULL,
  matricula       VARCHAR(50)   NOT NULL,
  career          VARCHAR(150)  NOT NULL,
  graduation_year YEAR,
  skills          JSON,            -- ej: ["React","Node.js","MySQL"]
  bio             TEXT,
  cv_url          VARCHAR(500),
  linkedin_url    VARCHAR(500),
  lat             DECIMAL(10,7),   -- Geolocalización
  lng             DECIMAL(10,7),
  created_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at      TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_graduate_user (user_id),
  UNIQUE KEY uq_graduate_matricula (matricula),
  CONSTRAINT fk_graduate_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: company_profiles
-- Perfil extendido de la empresa reclutadora
-- ------------------------------------------------------------
CREATE TABLE company_profiles (
  id            INT           NOT NULL AUTO_INCREMENT,
  user_id       INT           NOT NULL,
  company_name  VARCHAR(200)  NOT NULL,
  rfc           VARCHAR(20),
  sector        VARCHAR(100),
  description   TEXT,
  logo_url      VARCHAR(500),
  website       VARCHAR(500),
  lat           DECIMAL(10,7),
  lng           DECIMAL(10,7),
  is_verified   BOOLEAN       NOT NULL DEFAULT FALSE,
  created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_company_user (user_id),
  CONSTRAINT fk_company_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: jobs
-- Vacantes publicadas por las empresas
-- ------------------------------------------------------------
CREATE TABLE jobs (
  id              INT             NOT NULL AUTO_INCREMENT,
  company_id      INT             NOT NULL,
  title           VARCHAR(200)    NOT NULL,
  description     TEXT            NOT NULL,
  required_skills JSON,            -- ej: ["React","Git","REST APIs"]
  contract_type   ENUM('full_time','part_time','freelance','internship','temporary')
                  NOT NULL DEFAULT 'full_time',
  modality        ENUM('on_site','remote','hybrid') NOT NULL DEFAULT 'on_site',
  salary_min      DECIMAL(10,2),
  salary_max      DECIMAL(10,2),
  city            VARCHAR(100),
  status          ENUM('active','closed','draft') NOT NULL DEFAULT 'active',
  created_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  closes_at       TIMESTAMP,
  updated_at      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_jobs_company (company_id),
  KEY idx_jobs_status (status),
  CONSTRAINT fk_jobs_company
    FOREIGN KEY (company_id) REFERENCES company_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: applications
-- Postulaciones de egresados a vacantes
-- ------------------------------------------------------------
CREATE TABLE applications (
  id            INT     NOT NULL AUTO_INCREMENT,
  job_id        INT     NOT NULL,
  graduate_id   INT     NOT NULL,
  status        ENUM('pending','reviewed','accepted','rejected')
                NOT NULL DEFAULT 'pending',
  cover_letter  TEXT,
  applied_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_application (job_id, graduate_id),  -- Un egresado no puede postularse dos veces
  KEY idx_applications_job (job_id),
  KEY idx_applications_graduate (graduate_id),
  CONSTRAINT fk_application_job
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
  CONSTRAINT fk_application_graduate
    FOREIGN KEY (graduate_id) REFERENCES graduate_profiles(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: notifications
-- Notificaciones in-app por cambio de estado
-- ------------------------------------------------------------
CREATE TABLE notifications (
  id          INT           NOT NULL AUTO_INCREMENT,
  user_id     INT           NOT NULL,
  title       VARCHAR(200)  NOT NULL,
  message     TEXT          NOT NULL,
  is_read     BOOLEAN       NOT NULL DEFAULT FALSE,
  created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_notifications_user (user_id),
  KEY idx_notifications_read (user_id, is_read),
  CONSTRAINT fk_notification_user
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
