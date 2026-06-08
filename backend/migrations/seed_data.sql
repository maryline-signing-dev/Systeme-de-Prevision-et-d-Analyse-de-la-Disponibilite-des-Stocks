USE stock_prevision;

-- ============================================================
-- ADMIN
-- ============================================================

-- Mot de passe : admin123
INSERT INTO admin (nom, email, mot_de_passe_hash) VALUES
('Admin', 'adminstock@gmail.com',
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj9vFZ8E4Cqm');

-- ============================================================
-- PRODUITS (5 produits avec scénarios différents)
-- ============================================================

INSERT INTO produit
    (id_produit, nom_produit, categorie, marque,
     stock_initial, date_initialisation, unite, seuil_alerte)
VALUES
-- Produit 1 : Rupture prévue dans ~35 jours
(1, 'Ciment CEM II 42.5',   'Materiaux',   'CIMENCAM',   500,  '2026-01-01', 'sac',     50),
-- Produit 2 : Stock largement suffisant, pas de rupture
(2, 'Carrelage 60x60',      'Revetement',  'SOMAGEC',    1200, '2026-01-01', 'carton',  80),
-- Produit 3 : Rupture passée (test reconstitution historique)
(3, 'Fer a beton 10mm',     'Metallurgie', 'CABRAL',     200,  '2026-01-01', 'barre',   20),
-- Produit 4 : Stock sous le seuil d'alerte (pas encore en rupture)
(4, 'Peinture Blanche 10L', 'Peinture',    'SEIGNEURIE', 80,   '2026-01-01', 'bidon',   30),
-- Produit 5 : Flux simultanés (test RG-03)
(5, 'Cable electrique 2.5', 'Electricite', 'NEXANS',     300,  '2026-01-01', 'rouleau', 25);


-- ============================================================
-- PRODUIT 1 — Ciment CEM II 42.5
-- Scénario : rupture prévue dans ~35 jours
-- Stock initial : 500
-- Calcul attendu aujourd'hui : 500 - 100 + 200 - 150 = 450
-- Avec planifiés : 450 - 180 + 300 - 600 = -30 (RUPTURE)
-- ============================================================

INSERT INTO flux
    (id_produit, type_flux, nature_flux, statut_flux,
     quantite, date_flux, ordre_execution, reference_externe)
VALUES
-- Flux passés REALISES
(1,'SORTANT','LIVRAISON','REALISE', 100,'2026-01-15',1,'BL-001'),
(1,'ENTRANT','RECEPTION','REALISE', 200,'2026-02-01',1,'BC-001'),
(1,'SORTANT','LIVRAISON','REALISE',  80,'2026-02-20',1,'BL-002'),
(1,'SORTANT','LIVRAISON','REALISE',  70,'2026-03-10',1,'BL-003'),
-- Flux en cours
(1,'ENTRANT','RECEPTION','EN_COURS', 150,DATE_ADD(CURDATE(), INTERVAL -5 DAY),1,'BC-002'),
-- Flux futurs PLANIFIES
(1,'SORTANT','LIVRAISON','PLANIFIE', 180,DATE_ADD(CURDATE(), INTERVAL 10 DAY),1,'BL-004'),
(1,'ENTRANT','RECEPTION','PLANIFIE', 600,DATE_ADD(CURDATE(), INTERVAL 20 DAY),1,'BC-003'),
(1,'SORTANT','LIVRAISON','PLANIFIE', 300,DATE_ADD(CURDATE(), INTERVAL 35 DAY),1,'BL-005'),
-- Flux simultanés le même jour (test RG-03)
(1,'ENTRANT','RECEPTION','PLANIFIE', 100,DATE_ADD(CURDATE(), INTERVAL 45 DAY),1,'BC-004'),
(1,'SORTANT','LIVRAISON','PLANIFIE',  80,DATE_ADD(CURDATE(), INTERVAL 45 DAY),2,'BL-006');


-- ============================================================
-- PRODUIT 2 — Carrelage 60x60
-- Scénario : stock confortable, aucune rupture sur 90j
-- Stock initial : 1200
-- Calcul attendu : largement positif
-- ============================================================

INSERT INTO flux
    (id_produit, type_flux, nature_flux, statut_flux,
     quantite, date_flux, ordre_execution, reference_externe)
VALUES
(2,'SORTANT','LIVRAISON','REALISE', 150,'2026-01-20',1,'BL-010'),
(2,'SORTANT','LIVRAISON','REALISE', 200,'2026-02-15',1,'BL-011'),
(2,'ENTRANT','RECEPTION','REALISE', 500,'2026-03-01',1,'BC-010'),
(2,'SORTANT','LIVRAISON','REALISE', 100,'2026-03-20',1,'BL-012'),
(2,'SORTANT','LIVRAISON','PLANIFIE', 80,DATE_ADD(CURDATE(), INTERVAL 15 DAY),1,'BL-013'),
(2,'SORTANT','LIVRAISON','PLANIFIE',120,DATE_ADD(CURDATE(), INTERVAL 40 DAY),1,'BL-014'),
(2,'ENTRANT','RECEPTION','PLANIFIE',200,DATE_ADD(CURDATE(), INTERVAL 60 DAY),1,'BC-011');


-- ============================================================
-- PRODUIT 3 — Fer a beton 10mm
-- Scénario : rupture passée le 2026-04-01
-- Stock initial : 200
-- 200 - 100 - 80 - 30 = -10 au 2026-04-01 (RUPTURE)
-- Puis +150 le 2026-04-10 → stock revient à 140
-- ============================================================

INSERT INTO flux
    (id_produit, type_flux, nature_flux, statut_flux,
     quantite, date_flux, ordre_execution, reference_externe)
VALUES
(3,'SORTANT','LIVRAISON','REALISE',100,'2026-02-01',1,'BL-020'),
(3,'SORTANT','LIVRAISON','REALISE', 80,'2026-03-15',1,'BL-021'),
-- Flux sortant qui crée la rupture : 200-100-80=20 stock, on demande 30
(3,'SORTANT','LIVRAISON','REALISE', 30,'2026-04-01',1,'BL-022'),
-- Réception qui renfloue le stock
(3,'ENTRANT','RECEPTION','REALISE',150,'2026-04-10',1,'BC-020'),
(3,'SORTANT','LIVRAISON','REALISE', 50,'2026-05-01',1,'BL-023'),
(3,'SORTANT','LIVRAISON','PLANIFIE', 60,DATE_ADD(CURDATE(), INTERVAL 25 DAY),1,'BL-024'),
(3,'ENTRANT','RECEPTION','PLANIFIE',200,DATE_ADD(CURDATE(), INTERVAL 50 DAY),1,'BC-021');


-- ============================================================
-- PRODUIT 4 — Peinture Blanche 10L
-- Scénario : stock sous le seuil d'alerte (alerte sans rupture)
-- Stock initial : 80, seuil : 30
-- Après flux réalisés : ~25 (sous le seuil)
-- ============================================================

INSERT INTO flux
    (id_produit, type_flux, nature_flux, statut_flux,
     quantite, date_flux, ordre_execution, reference_externe)
VALUES
(4,'SORTANT','LIVRAISON','REALISE', 20,'2026-02-10',1,'BL-030'),
(4,'SORTANT','LIVRAISON','REALISE', 15,'2026-03-05',1,'BL-031'),
(4,'SORTANT','LIVRAISON','REALISE', 20,'2026-04-15',1,'BL-032'),
-- Stock = 80-20-15-20 = 25 (sous le seuil de 30 → ALERTE)
(4,'ENTRANT','REAPPRO',  'PLANIFIE', 50,DATE_ADD(CURDATE(), INTERVAL 7 DAY),1,'BC-030'),
(4,'SORTANT','LIVRAISON','PLANIFIE', 10,DATE_ADD(CURDATE(), INTERVAL 20 DAY),1,'BL-033');


-- ============================================================
-- PRODUIT 5 — Cable electrique 2.5
-- Scénario : test flux simultanés (même date, RG-03)
-- Stock initial : 300
-- ============================================================

INSERT INTO flux
    (id_produit, type_flux, nature_flux, statut_flux,
     quantite, date_flux, ordre_execution, reference_externe)
VALUES
(5,'SORTANT','LIVRAISON','REALISE',  50,'2026-02-01',1,'BL-040'),
(5,'SORTANT','LIVRAISON','REALISE',  80,'2026-03-01',1,'BL-041'),
(5,'ENTRANT','RECEPTION','REALISE', 100,'2026-03-15',1,'BC-040'),
-- Même date : entrée + sortie (test RG-03 : entrée avant sortie)
(5,'ENTRANT','RECEPTION','PLANIFIE',150,DATE_ADD(CURDATE(), INTERVAL 20 DAY),1,'BC-041'),
(5,'SORTANT','LIVRAISON','PLANIFIE',200,DATE_ADD(CURDATE(), INTERVAL 20 DAY),2,'BL-042'),
-- Sans l'entrée du même jour le stock serait : 270-200 = 70 (OK)
-- Avec RG-03 entrée d'abord : 270+150=420, puis 420-200=220 (OK, pas de rupture)
(5,'SORTANT','LIVRAISON','PLANIFIE', 90,DATE_ADD(CURDATE(), INTERVAL 40 DAY),1,'BL-043'),
(5,'SORTANT','LIVRAISON','PLANIFIE', 80,DATE_ADD(CURDATE(), INTERVAL 70 DAY),1,'BL-044');