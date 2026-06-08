/**
 * charts.js — Module de visualisation Chart.js
 * Gère la courbe temporelle d'évolution du stock.
 *
 * Éléments affichés :
 *   - Courbe bleue  : évolution du stock jour par jour
 *   - Ligne orange  : seuil d'alerte (pointillés)
 *   - Ligne rouge   : zéro (rupture) (pointillés)
 *   - Zone rouge    : segments où le stock est négatif
 */

let chartInstance = null;

/**
 * Charge les données et affiche le graphique.
 *
 * @param {number} productId  - ID du produit
 * @param {string} dateFrom   - Date début ISO (YYYY-MM-DD)
 * @param {string} dateTo     - Date fin   ISO (YYYY-MM-DD)
 * @param {string} canvasId   - ID de l'élément <canvas>
 */
async function renderStockChart(productId, dateFrom, dateTo,
                                canvasId = 'stockChart') {

    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    // Afficher le loader dans le conteneur du graphique
    const container = canvas.closest('.chart-container')
                   || canvas.parentElement;
    container.classList.add('loading');

    const result = await apiCall(
        `/prevision/${productId}/courbe` +
        `?from=${dateFrom}&to=${dateTo}`
    );

    container.classList.remove('loading');

    if (!result || !result.success) {
        showAlert('Erreur lors du chargement du graphique.', 'danger');
        return;
    }

    const { labels, values, seuil_alerte, ruptures, produit } =
        result.data;

    // Détruire l'instance précédente si elle existe
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }

    const ctx = canvas.getContext('2d');

    // ---- Couleur de segment selon le stock ----
    // Rouge si stock < 0, bleu sinon
    const segmentColors = values.map((v, i) => {
        if (i === 0) return v < 0 ? '#dc3545' : '#0d6efd';
        return values[i - 1] < 0 || v < 0 ? '#dc3545' : '#0d6efd';
    });

    // ---- Données du graphique ----
    chartInstance = new Chart(ctx, {
        type: 'line',

        data: {
            labels,
            datasets: [

                // Dataset 1 — Courbe stock
                {
                    label          : `Stock — ${produit.nom}`,
                    data           : values,
                    borderColor    : '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.08)',
                    borderWidth    : 2,
                    fill           : true,
                    tension        : 0.3,
                    pointRadius    : (ctx) => {
                        // Afficher un point uniquement sur les ruptures
                        const d = labels[ctx.dataIndex];
                        return ruptures.includes(d) ? 6 : 0;
                    },
                    pointBackgroundColor: '#dc3545',
                    pointBorderColor    : '#fff',
                    pointBorderWidth    : 2,
                    segment: {
                        borderColor: (ctx) => {
                            const v1 = ctx.p0.parsed.y;
                            const v2 = ctx.p1.parsed.y;
                            return (v1 < 0 || v2 < 0)
                                ? '#dc3545'
                                : '#0d6efd';
                        },
                        backgroundColor: (ctx) => {
                            const v1 = ctx.p0.parsed.y;
                            const v2 = ctx.p1.parsed.y;
                            return (v1 < 0 || v2 < 0)
                                ? 'rgba(220,53,69,0.08)'
                                : 'rgba(13,110,253,0.08)';
                        }
                    }
                },

                // Dataset 2 — Seuil d'alerte
                {
                    label          : `Seuil d'alerte (${seuil_alerte} ${produit.unite})`,
                    data           : new Array(labels.length)
                                         .fill(seuil_alerte),
                    borderColor    : '#ffc107',
                    borderWidth    : 1.5,
                    borderDash     : [6, 4],
                    fill           : false,
                    tension        : 0,
                    pointRadius    : 0,
                    pointHoverRadius: 0
                },

                // Dataset 3 — Ligne zéro (rupture)
                {
                    label          : 'Rupture (stock = 0)',
                    data           : new Array(labels.length).fill(0),
                    borderColor    : '#dc3545',
                    borderWidth    : 1,
                    borderDash     : [10, 5],
                    fill           : false,
                    tension        : 0,
                    pointRadius    : 0,
                    pointHoverRadius: 0
                }
            ]
        },

        options: {
            responsive        : true,
            maintainAspectRatio: false,

            interaction: {
                mode     : 'index',
                intersect: false
            },

            plugins: {
                legend: {
                    position: 'top',
                    labels  : {
                        usePointStyle: true,
                        pointStyle   : 'line',
                        padding      : 20,
                        font         : { size: 12 }
                    }
                },

                title: {
                    display: true,
                    text   : `Évolution du stock — ${produit.nom}`,
                    font   : { size: 14, weight: 'bold' },
                    padding: { bottom: 16 }
                },

                tooltip: {
                    callbacks: {
                        title : (items) =>
                            `📅 ${formatDate(items[0].label)}`,
                        label : (item) => {
                            if (item.datasetIndex === 0) {
                                const val = item.parsed.y;
                                const icon = val < 0 ? '⚠' :
                                             val === 0 ? '!' : '✓';
                                return ` ${icon} Stock : ${val} ${produit.unite}`;
                            }
                            if (item.datasetIndex === 1)
                                return ` Seuil : ${item.parsed.y} ${produit.unite}`;
                            return null;
                        },
                        afterBody: (items) => {
                            const d = items[0].label;
                            if (ruptures.includes(d)) {
                                return ['', '⚠ RUPTURE DÉTECTÉE CE JOUR'];
                            }
                            return [];
                        }
                    }
                }
            },

            scales: {
                x: {
                    grid : { display: false },
                    ticks: {
                        maxTicksLimit: 12,
                        maxRotation  : 45,
                        font         : { size: 11 },
                        callback     : (val, idx, ticks) => {
                            // Afficher une date sur N
                            const step = Math.max(
                                1,
                                Math.floor(labels.length / 12)
                            );
                            return idx % step === 0
                                ? formatDate(labels[idx])
                                : '';
                        }
                    }
                },

                y: {
                    title: {
                        display: true,
                        text   : produit.unite,
                        font   : { size: 12 }
                    },
                    grid: {
                        color: (ctx) =>
                            ctx.tick.value === 0
                                ? 'rgba(220,53,69,0.3)'
                                : 'rgba(0,0,0,0.06)'
                    },
                    ticks: {
                        font: { size: 11 }
                    }
                }
            }
        }
    });

    // Annoter les ruptures sous le graphique
    afficherAnnotationsRuptures(ruptures, produit.unite);
}

/**
 * Affiche une liste des dates de rupture détectées.
 */
function afficherAnnotationsRuptures(ruptures, unite) {
    const container = document.getElementById('chart-ruptures');
    if (!container) return;

    if (!ruptures || ruptures.length === 0) {
        container.innerHTML = `
            <small class="text-success">
                <i class="bi bi-check-circle me-1"></i>
                Aucune rupture détectée sur la période.
            </small>`;
        return;
    }

    container.innerHTML = `
        <small class="text-danger fw-semibold me-2">
            <i class="bi bi-exclamation-triangle-fill me-1"></i>
            Ruptures détectées :
        </small>` +
        ruptures.map(d =>
            `<span class="badge bg-danger me-1">
                ${formatDate(d)}
             </span>`
        ).join('');
}

/**
 * Détruit le graphique actuel.
 */
function destroyChart() {
    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }
}