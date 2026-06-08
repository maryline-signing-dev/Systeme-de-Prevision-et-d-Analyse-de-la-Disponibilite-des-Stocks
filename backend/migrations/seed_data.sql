USE stock_prevision;

INSERT INTO admin (nom, email, mot_de_passe_hash) VALUES
('Administrateur', 'stockadmin@gmail.com', '$2b$12$H0dOc7O9C7mQ8SSZK7gbDOnetbgqZWvpe9VbJzUVub6g2oqYOz2ey');

INSERT INTO produit (nom_produit, categorie, marque, stock_initial, date_initialisation, unite, seuil_alerte) VALUES
('Ciment CEM II 42.5',   'Materiaux',   'CIMENCAM',   500, '2026-01-01', 'sac',     50),
('Carrelage 60x60',      'Revetement',  'SOMAGEC',    800, '2026-01-01', 'carton',  80),
('Fer a beton 10mm',     'Metallurgie', 'CABRAL',     200, '2026-01-01', 'barre',   20);

INSERT INTO flux (id_produit, type_flux, nature_flux, statut_flux, quantite, date_flux, ordre_execution) VALUES
(1,'SORTANT','LIVRAISON','REALISE',  100,'2026-01-15',1),
(1,'ENTRANT','RECEPTION','REALISE',  200,'2026-02-01',1),
(1,'SORTANT','LIVRAISON','REALISE',  150,'2026-03-10',1),
(1,'SORTANT','LIVRAISON','PLANIFIE', 180,DATE_ADD(CURDATE(), INTERVAL 10 DAY),1),
(1,'ENTRANT','RECEPTION','PLANIFIE', 300,DATE_ADD(CURDATE(), INTERVAL 20 DAY),1),
(1,'SORTANT','LIVRAISON','PLANIFIE', 600,DATE_ADD(CURDATE(), INTERVAL 35 DAY),1),
(2,'SORTANT','LIVRAISON','REALISE',  100,'2026-01-20',1),
(3,'SORTANT','LIVRAISON','REALISE',  100,'2026-02-01',1),
(3,'SORTANT','LIVRAISON','REALISE',   80,'2026-03-15',1),
(3,'SORTANT','LIVRAISON','REALISE',   30,'2026-04-01',1),
(3,'ENTRANT','RECEPTION','REALISE',  150,'2026-04-10',1);