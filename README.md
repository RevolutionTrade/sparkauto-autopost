# Agent static ads Spark Auto

Chaque jour vers 6 h 30 (heure de Paris), l'agent :

1. choisit 6 combinaisons **format de pub × véhicule du catalogue** (24 formats, 39 véhicules ; un même duo ne revient pas avant 90 jours) ;
2. génère les visuels **Instagram 1080×1350** et **TikTok 1080×1920**, avec la vraie photo CarPlay du véhicule, son nom et le badge « +250 modèles / 40 marques » ;
3. écrit les légendes et les hashtags (uniquement des infos présentes sur sparkauto.fr, aucun prix) ;
4. les programme dans **Buffer**, qui les publie sur Instagram et TikTok à **08:30, 11:30, 13:30, 17:00, 19:30 et 21:30**.

Tout tourne gratuitement sur GitHub Actions, même quand le PC est éteint.

## Lancer à la main
Onglet *Actions* → *Static ads Spark Auto* → *Run workflow* :
- **test** : 1 brouillon par réseau dans Buffer (rien n'est publié) ;
- **normal** : programme les posts restants de la journée ;
- **dry-run** : génère seulement les images (téléchargeables dans l'exécution, artefact « visuels »).

## Réglages (`config.json`)
| Clé | Rôle |
| --- | --- |
| `times` | Heures de publication (heure de Paris). 5 heures = 5 posts par jour. |
| `promos` | Offres datées (code, titre, dates `from` / `until`). Une pub promo par jour tant que l'offre est active. |
| `evergreen_offer` / `evergreen_caption` | Offre permanente (CARPLAY10). |
| `platforms` | `false` pour couper Instagram ou TikTok. |
| `exclude_templates` / `exclude_vehicles` | Retirer un format (ex. `"voici_julien"`) ou un véhicule (son `id`). |

**Ajouter un véhicule** : dans `vehicles.json`, copier un bloc et changer `id` (handle Shopify), `name`, `short`, `brand`, `years`, `start` et `photos` (photos où l'écran CarPlay est en français).

## Suivi
- Journal de chaque exécution dans l'onglet *Actions* ; e-mail de GitHub en cas d'erreur.
- `history.json` garde la trace de tout ce qui a été programmé.
- La clé Buffer est stockée dans *Settings → Secrets and variables → Actions* (`BUFFER_API_KEY`).
- Les images sont hébergées sur la branche `media` (seulement celles du jour).
