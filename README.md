# Agent pubs Spark Auto

Chaque jour vers 6 h 30 (heure de Paris), l'agent :

1. choisit 6 combinaisons **format de pub × véhicule du catalogue** : 4 statiques (24 formats) et **2 Reels animés** (6 formats, à 11:30 et 19:30) ; un même duo ne revient pas avant 90 jours ;
2. génère les statiques **Instagram 1080×1350 / TikTok 1080×1920** et les Reels **1080×1920, 10 s**, avec la vraie photo CarPlay du véhicule, son nom, le logo Spark Auto en haut au centre et le badge « +300 modèles / 40 marques » ;
3. **auto-évalue chaque pub avant de la programmer** :
   - contrôles automatiques (gratuits) : texte coupé, hors cadre ou qui se chevauche, logo absent en haut au centre, badge absent, prix affiché ;
   - notation par une IA qui regarde l'image (Claude, si le secret `ANTHROPIC_API_KEY` existe) : esthétisme, compréhension, intérêt, conversion, notés sur 5, et critères éliminatoires ;
   - publiée seulement si **≥ 16/20 et aucune note sous 3** ; sinon régénérée avec un autre format ou véhicule (2 essais), puis créneau laissé vide ;
   - si l'IA est indisponible, les pubs qui passent les contrôles automatiques sont publiées et marquées « non évalué » ;
4. écrit les légendes et les hashtags (uniquement des infos présentes sur sparkauto.fr, aucun prix) ;
5. les programme dans **Buffer**, qui les publie sur Instagram (post ou Reel) et TikTok à **08:30, 11:30, 13:30, 17:00, 19:30 et 21:30**.

Chaque lundi, un **récapitulatif de la semaine** (meilleurs et pires formats, formats à retirer, pubs rejetées) est publié dans l'onglet *Issues* du dépôt : GitHub l'envoie par e-mail.

Tout tourne sur GitHub Actions, même quand le PC est éteint.

## Lancer à la main
Onglet *Actions* → *Static ads Spark Auto* → *Run workflow* :
- **test** : 1 statique + 1 Reel en brouillon dans Buffer (rien n'est publié) ;
- **normal** : programme les posts restants de la journée ;
- **dry-run** : génère et évalue seulement (fichiers téléchargeables dans l'exécution, artefact « visuels ») ;
- **recap** : récapitulatif de la semaine.

## Réglages (`config.json`)
| Clé | Rôle |
| --- | --- |
| `times` | Heures de publication (heure de Paris). |
| `video_slots` | Créneaux en Reel (numéros dans `times`, par défaut 2 et 5). |
| `evaluation` | Modèle IA, note minimale (`min_total`, `min_each`), nombre de régénérations, publication si l'IA est indisponible. |
| `promos` | Offres datées (code, titre, dates `from` / `until`). Une pub promo par jour tant que l'offre est active. |
| `evergreen_offer` / `evergreen_caption` | Offre permanente (CARPLAY10). |
| `platforms` | `false` pour couper Instagram ou TikTok. |
| `exclude_templates` / `exclude_vehicles` | Retirer un format (ex. `"voici_julien"`, `"reel_ticket"`) ou un véhicule (son `id`). |

**Ajouter un véhicule** : dans `vehicles.json`, copier un bloc et changer `id` (handle Shopify), `name`, `short`, `brand`, `years`, `start` et `photos` (photos où l'écran CarPlay est en français).

## Suivi
- Journal de chaque exécution dans l'onglet *Actions* ; e-mail de GitHub en cas d'erreur.
- `history.json` garde la trace de tout ce qui a été programmé ou rejeté, avec les notes.
- Secrets dans *Settings → Secrets and variables → Actions* : `BUFFER_API_KEY` (obligatoire), `ANTHROPIC_API_KEY` (évaluation IA).
- Les fichiers sont hébergés sur la branche `media` (aujourd'hui et hier seulement).
