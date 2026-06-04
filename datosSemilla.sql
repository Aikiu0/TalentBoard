-- ============================================================
-- TalentBoard – Seed Data v1.0
-- Sintaxis: PostgreSQL (Supabase compatible)
-- NOTA: Los password_hash corresponden a bcrypt de "Password123!"
-- ============================================================

-- Limpiar datos previos (orden inverso a FK)
TRUNCATE TABLE notifications, applications, jobs,
               company_profiles, graduate_profiles, users
  RESTART IDENTITY CASCADE;

-- ------------------------------------------------------------
-- USUARIOS BASE
-- ------------------------------------------------------------
INSERT INTO users (email, password_hash, role, is_active) VALUES
  -- Admin institucional
  ('admin@talentboard.edu.mx',
   '$2b$10$Xv8kL2mN3pQ4rS5tU6vW7OeF1gH2iJ3kL4mN5pQ6rS7tU8vW9xYz0',
   'admin', TRUE),

  -- Empresa 1
  ('rrhh@softwaremx.com',
   '$2b$10$Xv8kL2mN3pQ4rS5tU6vW7OeF1gH2iJ3kL4mN5pQ6rS7tU8vW9xYz0',
   'company', TRUE),

  -- Empresa 2
  ('contacto@techqueretaro.mx',
   '$2b$10$Xv8kL2mN3pQ4rS5tU6vW7OeF1gH2iJ3kL4mN5pQ6rS7tU8vW9xYz0',
   'company', TRUE),

  -- Egresado 1
  ('valeria.torres@egresado.edu.mx',
   '$2b$10$Xv8kL2mN3pQ4rS5tU6vW7OeF1gH2iJ3kL4mN5pQ6rS7tU8vW9xYz0',
   'graduate', TRUE),

  -- Egresado 2
  ('carlos.reyes@egresado.edu.mx',
   '$2b$10$Xv8kL2mN3pQ4rS5tU6vW7OeF1gH2iJ3kL4mN5pQ6rS7tU8vW9xYz0',
   'graduate', TRUE);

-- ------------------------------------------------------------
-- PERFILES DE EMPRESAS  (user_id 2 y 3)
-- ------------------------------------------------------------
INSERT INTO company_profiles
  (user_id, company_name, rfc, sector, description, logo_url, website,
   lat, lng, is_verified)
VALUES
  (2, 'SoftwareMX S.A. de C.V.', 'SMX201501AB3',
   'Tecnología de la Información',
   'Empresa de desarrollo de software a medida con 10 años de experiencia en el mercado nacional.',
   'https://placehold.co/200x200?text=SMX',
   'https://softwaremx.com',
   20.5888, -100.3899, TRUE),

  (3, 'TechQuerétaro S.C.', 'TQR180803CD5',
   'Consultoría TI',
   'Consultora especializada en transformación digital para PyMEs del Bajío.',
   'https://placehold.co/200x200?text=TQR',
   'https://techqueretaro.mx',
   20.6010, -100.4070, FALSE);

-- ------------------------------------------------------------
-- PERFILES DE EGRESADOS  (user_id 4 y 5)
-- ------------------------------------------------------------
INSERT INTO graduate_profiles
  (user_id, full_name, matricula, career, graduation_year,
   skills, bio, cv_url, linkedin_url, lat, lng)
VALUES
  (4, 'Valeria Torres Mendoza', 'TEC-2021-0042',
   'Ingeniería en Desarrollo de Software', 2024,
   '["React","Node.js","MySQL","Git","REST APIs","TypeScript"]',
   'Egresada apasionada por el desarrollo web. Experiencia en proyectos académicos con React y Express.',
   'https://example.com/cv/valeria-torres.pdf',
   'https://linkedin.com/in/valeria-torres-mx',
   20.5931, -
