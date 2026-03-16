-- Base de données bibliothèque
CREATE DATABASE IF NOT EXISTS bibliotheque;
USE bibliotheque;

CREATE TABLE auteurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    nationalite VARCHAR(50),
    date_naissance DATE,
    biographie TEXT
);

CREATE TABLE livres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    auteur_id INT NOT NULL,
    genre VARCHAR(50),
    annee_publication INT,
    isbn VARCHAR(20) UNIQUE,
    nb_pages INT,
    langue VARCHAR(30) DEFAULT 'Français',
    disponible BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (auteur_id) REFERENCES auteurs(id)
);

CREATE TABLE emprunts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    livre_id INT NOT NULL,
    emprunteur VARCHAR(150) NOT NULL,
    date_emprunt DATE NOT NULL,
    date_retour_prevue DATE NOT NULL,
    date_retour_effective DATE,
    rendu BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (livre_id) REFERENCES livres(id)
);

-- Auteurs
INSERT INTO auteurs (nom, prenom, nationalite, date_naissance, biographie) VALUES
('Hugo', 'Victor', 'Française', '1802-02-26', 'Poète, romancier et dramaturge romantique français.'),
('Camus', 'Albert', 'Française', '1913-11-07', 'Écrivain, philosophe et journaliste français, prix Nobel 1957.'),
('Zola', 'Émile', 'Française', '1840-04-02', 'Romancier et journaliste français, chef de file du naturalisme.'),
('de Maupassant', 'Guy', 'Française', '1850-08-05', 'Écrivain français, maître de la nouvelle.'),
('Proust', 'Marcel', 'Française', '1871-07-10', 'Romancier français, auteur d''À la recherche du temps perdu.'),
('Flaubert', 'Gustave', 'Française', '1821-12-12', 'Romancier français, chef de file du réalisme littéraire.'),
('Stendhal', 'Henri', 'Française', '1783-01-23', 'Écrivain français du XIXe siècle.'),
('Balzac', 'Honoré de', 'Française', '1799-05-20', 'Romancier et dramaturge français, auteur de La Comédie humaine.');

-- Livres
INSERT INTO livres (titre, auteur_id, genre, annee_publication, isbn, nb_pages, langue, disponible) VALUES
('Les Misérables', 1, 'Roman', 1862, '978-2-07-040850-4', 1900, 'Français', TRUE),
('Notre-Dame de Paris', 1, 'Roman historique', 1831, '978-2-07-036024-5', 570, 'Français', FALSE),
('L''Étranger', 2, 'Roman', 1942, '978-2-07-036024-1', 186, 'Français', TRUE),
('La Peste', 2, 'Roman', 1947, '978-2-07-036024-2', 352, 'Français', TRUE),
('Germinal', 3, 'Roman', 1885, '978-2-07-036820-3', 591, 'Français', FALSE),
('Nana', 3, 'Roman', 1880, '978-2-07-036820-4', 484, 'Français', TRUE),
('Bel-Ami', 4, 'Roman', 1885, '978-2-07-036024-6', 376, 'Français', TRUE),
('Une vie', 4, 'Roman', 1883, '978-2-07-036024-7', 312, 'Français', TRUE),
('Du côté de chez Swann', 5, 'Roman', 1913, '978-2-07-036024-8', 556, 'Français', FALSE),
('Madame Bovary', 6, 'Roman', 1857, '978-2-07-036820-5', 468, 'Français', TRUE),
('L''Éducation sentimentale', 6, 'Roman', 1869, '978-2-07-036820-6', 600, 'Français', TRUE),
('Le Rouge et le Noir', 7, 'Roman', 1830, '978-2-07-036820-7', 700, 'Français', TRUE),
('La Chartreuse de Parme', 7, 'Roman', 1839, '978-2-07-036820-8', 510, 'Français', FALSE),
('Père Goriot', 8, 'Roman', 1835, '978-2-07-036820-9', 376, 'Français', TRUE),
('Eugénie Grandet', 8, 'Roman', 1833, '978-2-07-036821-0', 302, 'Français', TRUE);

-- Emprunts
INSERT INTO emprunts (livre_id, emprunteur, date_emprunt, date_retour_prevue, date_retour_effective, rendu) VALUES
(2, 'Marie Dupont', '2024-11-01', '2024-11-15', '2024-11-14', TRUE),
(5, 'Jean Martin', '2024-12-01', '2024-12-15', NULL, FALSE),
(9, 'Sophie Leroy', '2024-12-10', '2024-12-24', NULL, FALSE),
(13, 'Paul Bernard', '2024-10-05', '2024-10-19', '2024-10-18', TRUE),
(2, 'Claire Petit', '2025-01-03', '2025-01-17', NULL, FALSE),
(5, 'Thomas Richard', '2024-09-01', '2024-09-15', '2024-09-12', TRUE),
(9, 'Julie Moreau', '2025-01-15', '2025-01-29', NULL, FALSE);
