-- Base de données : Concession automobile

CREATE TABLE marques (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    pays VARCHAR(50) NOT NULL,
    fondee_en INT
);

CREATE TABLE modeles (
    id SERIAL PRIMARY KEY,
    marque_id INT REFERENCES marques(id),
    nom VARCHAR(100) NOT NULL,
    type VARCHAR(30),
    annee_lancement INT
);

CREATE TABLE voitures (
    id SERIAL PRIMARY KEY,
    modele_id INT REFERENCES modeles(id),
    annee INT NOT NULL,
    couleur VARCHAR(30),
    prix DECIMAL(10,2) NOT NULL,
    kilometrage INT DEFAULT 0,
    carburant VARCHAR(20),
    disponible BOOLEAN DEFAULT TRUE
);

CREATE TABLE ventes (
    id SERIAL PRIMARY KEY,
    voiture_id INT REFERENCES voitures(id),
    vendeur VARCHAR(100),
    acheteur VARCHAR(100),
    prix_vente DECIMAL(10,2) NOT NULL,
    date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Marques
INSERT INTO marques (nom, pays, fondee_en) VALUES
    ('Renault',    'France',     1899),
    ('Peugeot',    'France',     1882),
    ('Volkswagen', 'Allemagne',  1937),
    ('Toyota',     'Japon',      1937),
    ('BMW',        'Allemagne',  1916),
    ('Ford',       'États-Unis', 1903);

-- Modèles
INSERT INTO modeles (marque_id, nom, type, annee_lancement) VALUES
    (1, 'Clio',        'Citadine',   1990),
    (1, 'Megane',      'Berline',    1995),
    (1, 'Captur',      'SUV',        2013),
    (2, '208',         'Citadine',   2012),
    (2, '3008',        'SUV',        2008),
    (3, 'Golf',        'Compacte',   1974),
    (3, 'Tiguan',      'SUV',        2007),
    (4, 'Yaris',       'Citadine',   1999),
    (4, 'RAV4',        'SUV',        1994),
    (5, 'Série 3',     'Berline',    1975),
    (5, 'X5',          'SUV',        1999),
    (6, 'Mustang',     'Coupé',      1964);

-- Voitures
INSERT INTO voitures (modele_id, annee, couleur, prix, kilometrage, carburant, disponible) VALUES
    (1,  2021, 'Rouge',      14500.00,  12000, 'Essence',   TRUE),
    (1,  2020, 'Blanc',      12900.00,  28000, 'Diesel',    TRUE),
    (2,  2022, 'Gris',       22000.00,   5000, 'Hybride',   TRUE),
    (3,  2023, 'Bleu',       26500.00,   1500, 'Essence',   TRUE),
    (4,  2021, 'Noir',       16800.00,  18000, 'Électrique',TRUE),
    (5,  2022, 'Blanc',      34000.00,   9000, 'Hybride',   TRUE),
    (6,  2020, 'Argent',     23500.00,  35000, 'Essence',   FALSE),
    (7,  2021, 'Vert',       38000.00,  22000, 'Diesel',    TRUE),
    (8,  2023, 'Rouge',      19000.00,   3000, 'Hybride',   TRUE),
    (9,  2022, 'Noir',       42000.00,  11000, 'Hybride',   TRUE),
    (10, 2021, 'Bleu',       45000.00,  14000, 'Essence',   TRUE),
    (11, 2020, 'Blanc',      72000.00,  20000, 'Diesel',    FALSE),
    (12, 2023, 'Rouge',      58000.00,   2000, 'Essence',   TRUE);

-- Ventes
INSERT INTO ventes (voiture_id, vendeur, acheteur, prix_vente, date_vente) VALUES
    (7,  'Marie Dupont',   'Lucas Bernard',  23000.00, '2024-01-15 10:30:00'),
    (12, 'Pierre Martin',  'Sophie Leroy',   55000.00, '2024-02-03 14:00:00');
