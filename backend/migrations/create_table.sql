CREATE DATABASE IF NOT EXISTS stock_prevision
    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stock_prevision;

CREATE TABLE IF NOT EXISTS admin (
    id_admin          INT           NOT NULL AUTO_INCREMENT,
    nom               VARCHAR(100)  NOT NULL,
    telephone         VARCHAR(20)   NULL,
    email             VARCHAR(150)  NOT NULL UNIQUE,
    age               INT           NULL,
    sexe              ENUM('M','F') NULL,
    mot_de_passe_hash VARCHAR(255)  NOT NULL,
    derniere_connexion DATETIME     NULL,
    date_creation     DATETIME      NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id_admin)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS produit (
    id_produit          INT           NOT NULL AUTO_INCREMENT,
    nom_produit         VARCHAR(200)  NOT NULL,
    categorie           VARCHAR(100)  NULL,
    marque              VARCHAR(100)  NULL,
    stock_initial       INT NOT NULL DEFAULT 0,
    date_initialisation DATE          NOT NULL,
    unite               VARCHAR(20)   NOT NULL DEFAULT 'unite',
    seuil_alerte        INT NOT NULL DEFAULT 0,
    actif               BOOLEAN       NOT NULL DEFAULT TRUE,
    PRIMARY KEY (id_produit)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS flux (
    id_flux           INT           NOT NULL AUTO_INCREMENT,
    id_produit        INT           NOT NULL,
    type_flux         ENUM('ENTRANT','SORTANT') NOT NULL,
    nature_flux       VARCHAR(100)  NULL,
    statut_flux       ENUM('PLANIFIE','EN_COURS','REALISE') NOT NULL DEFAULT 'PLANIFIE',
    quantite          INT NOT NULL,
    date_flux         DATE          NOT NULL,
    heure_flux        TIME          NULL,
    ordre_execution   INT           NOT NULL DEFAULT 0,
    reference_externe VARCHAR(100)  NULL,
    commentaire       TEXT          NULL,
    date_saisie       DATETIME      NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id_flux),
    CONSTRAINT fk_flux_produit FOREIGN KEY (id_produit)
        REFERENCES produit(id_produit) ON DELETE RESTRICT,
    CONSTRAINT chk_quantite CHECK (quantite > 0)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS historique_flux (
    id_historique   INT    NOT NULL AUTO_INCREMENT,
    id_flux         INT    NOT NULL,
    id_produit      INT    NOT NULL,
    id_admin        INT    NULL,
    ancienne_valeur JSON   NULL,
    nouvelle_valeur JSON   NULL,
    type_operation  ENUM('INSERT','UPDATE','DELETE') NOT NULL,
    date_historique DATETIME NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id_historique),
    CONSTRAINT fk_hist_flux    FOREIGN KEY (id_flux)    REFERENCES flux(id_flux)       ON DELETE CASCADE,
    CONSTRAINT fk_hist_produit FOREIGN KEY (id_produit) REFERENCES produit(id_produit) ON DELETE CASCADE,
    CONSTRAINT fk_hist_admin   FOREIGN KEY (id_admin)   REFERENCES admin(id_admin)     ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_flux_produit_date ON flux (id_produit, date_flux, statut_flux);
CREATE INDEX idx_flux_date_type    ON flux (date_flux, type_flux, ordre_execution);