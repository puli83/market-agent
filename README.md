# 🔍 Agent d'Analyse de Marché E-commerce

Agent IA qui orchestre plusieurs outils spécialisés pour produire des rapports
stratégiques sur des produits e-commerce. Propulsé par LangGraph et Groq (LLaMA 3.3 70B).

---

## Table des matières

1. [Architecture](#architecture)
2. [Installation rapide](#installation-rapide)
3. [Lancement avec Docker](#lancement-avec-docker)
4. [Utilisation de l'API](#utilisation-de-lapi)
5. [Tests](#tests)
6. [Choix techniques](#choix-techniques)
7. [Réponses aux questions théoriques (étapes 4 à 7)](#réponses-aux-questions-théoriques)

---

## Architecture

### Structure du projet

```
market-agent/
├── main.py                  # Point d'entrée → lance le serveur FastAPI
├── api.py                   # Endpoints REST: /health, /analyze
├── config.py                # Configuration centralisée (env, logging, constantes)
├── agent/
│   ├── state.py             # Structure de données du graphe (AgentState)
│   ├── prompts.py           # 2 prompts spécialisés (orchestrateur + analyste)
│   ├── safe_tools.py        # Exécution sécurisée des outils (gestion d'erreurs)
│   └── graph.py             # Construction du graphe LangGraph (orchestration)
├── tools/
│   └── market_tools.py      # 3 outils: scraper, sentiment, trends
├── data/
│   └── mock_data.py         # Données mockées réalistes (3 produits)
├── models/
│   └── schemas.py           # Schémas Pydantic (validation requêtes/réponses)
├── tests/
│   └── test_agent.py        # 13 tests unitaires
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

### Graphe d'orchestration (pattern ReAct)

```
Architecture du graphe:

                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
    START ──→ agent_node ──→ should_continue()            │
              (LLM pense)       │                         │
                                │                         │
                    ┌───────────┼───────────┐             │
                    │           │           │             │
                    ▼           ▼           ▼             │
              LLM veut    LLM a fini   Garde-fou         │
              un outil    son rapport   déclenché         │
                    │           │           │             │
                    ▼           ▼           ▼             │
              safe_tool_node   END    force_end_node      │
              (exécute l'outil)       (rapport partiel)   │
                    │                       │             │
                    │                       ▼             │
                    │                      END            │
                    │                                     │
                    └─────────────────────────────────────┘
                        résultat retourné à l'agent

```

Prompts utilisés:
  ● agent_node (0-2 outils collectés) → ORCHESTRATOR_PROMPT
  ● agent_node (3 outils collectés)   → ANALYST_PROMPT
  ● force_end_node                    → ANALYST_PROMPT + FORCE_END_PROMPT
  
L'agent suit le pattern ReAct (Reason + Act) implémenté via un graphe LangGraph à 3 nœuds:

1. Le point d'entrée est toujours agent_node. Le LLM reçoit l'historique des messages
   et un prompt adapté à la phase en cours. Si moins de 3 outils ont répondu, il reçoit
   le ORCHESTRATOR_PROMPT (court, directif: "appelle les outils"). Si les 3 outils ont
   répondu, il reçoit le ANALYST_PROMPT (détaillé: "analyse les données, produis le rapport").

2. Après chaque réponse du LLM, la fonction should_continue() détermine le chemin:

   - Si un garde-fou est déclenché (timeout ou max itérations) → force_end_node.
     Le LLM est appelé SANS outils avec le ANALYST_PROMPT et une instruction de
     conclure immédiatement. Il produit un rapport partiel avec les données disponibles.

   - Si le LLM demande un outil → safe_tool_node. L'outil est exécuté dans un
     try/except. Si l'outil plante, un message d'erreur est retourné au LLM au lieu
     de crasher l'agent. Le résultat (succès ou erreur) est renvoyé à agent_node.

   - Si le LLM donne sa réponse finale (pas de tool_call) → END. Le rapport est
     retourné à l'utilisateur.

3. La boucle agent_node → safe_tool_node → agent_node se répète jusqu'à ce que
   le LLM ait collecté les données des 3 outils et produit son analyse. Une analyse
   typique fait 4 itérations: 3 appels d'outils + 1 compilation du rapport.
  
**Flux d'une analyse complète:**

1. L'utilisateur envoie `POST /analyze` avec un produit
2. Le LLM reçoit le **prompt orchestrateur** → appelle `web_scraper`
3. L'outil retourne les prix → le LLM appelle `sentiment_analyzer`
4. L'outil retourne les avis bruts → le LLM appelle `trend_analyzer`
5. L'outil retourne les tendances → les 3 outils sont collectés
6. Le LLM reçoit le **prompt analyste** → analyse les données brutes
7. Le LLM produit le rapport final avec recommandations

### Fonctionnalités de robustesse

- **Gestion d'erreurs**: si un outil plante, l'agent continue avec les données disponibles
- **Garde-fou itérations**: maximum 10 tours dans la boucle (configurable)
- **Garde-fou timeout**: maximum 60 secondes par analyse (configurable)
- **Sortie forcée**: si un garde-fou se déclenche, le LLM compile un rapport partiel
- **Double prompt**: orchestrateur (collecte) et analyste (rapport) pour une meilleure spécialisation
- **Logging**: chaque étape est tracée avec son temps d'exécution (outil appelé, durée, succès/erreur)

---


## Lancement avec Docker

### Prérequis

- Docker et Docker Compose installés

### Étapes

```bash
# 1. Configurer la clé API
cp .env.example .env
# Éditer .env et ajouter votre clé GROQ_API_KEY

# 2. Construire et lancer
docker compose up --build

# 3. Ouvrir dans le navigateur
# http://localhost:8010/docs

# 4. Arrêter
docker compose down
```

---

## Utilisation de l'API

### Interface Swagger

Ouvrir **http://localhost:8010/docs** dans un navigateur. L'interface permet de
tester tous les endpoints directement, avec des exemples pré-remplis.

### Exemples avec curl

**Analyse simple:**
```bash
curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{"product": "AirPods Pro 2"}'
```

**Analyse avec marché et contexte:**
```bash
curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Nike Air Max 90",
    "market": "france",
    "context": "Je veux ouvrir une boutique de sneakers en ligne"
  }'
```

**Autre produit:**
```bash
curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Nespresso Vertuo",
    "market": "canada",
    "context": "Évaluer le potentiel de revente sur marketplace"
  }'
```

**Health check:**
```bash
curl http://localhost:8010/health
```

### Produits disponibles (données mockées)

| Produit | Catégorie | Plateformes | Avis clients |
|---|---|---|---|
| AirPods Pro 2 | Tech / Audio | Amazon, Fnac, Cdiscount, Darty, Boulanger | 16 avis bruts |
| Nike Air Max 90 | Mode / Sneakers | Nike.com, Zalando, Courir, Foot Locker, Amazon | 15 avis bruts |
| Nespresso Vertuo | Maison / Café | Nespresso.com, Amazon, Boulanger, Darty, Cdiscount | 16 avis bruts |

### Paramètres de la requête

| Champ | Obligatoire | Défaut | Description |
|---|---|---|---|
| `product` | Oui | — | Nom du produit à analyser |
| `market` | Non | `france` | Région: france, usa, canada, uk, global |
| `context` | Non | `""` | Contexte pour personnaliser l'analyse |

---

## Tests


### Lancer les tests dans Docker

```bash
docker compose run market-agent pytest tests/ -v
```

### Couverture des tests (13 tests)

| Groupe | Tests | Ce qu'ils vérifient |
|---|---|---|
| Outils (5) | JSON valide, structure avis bruts, données mensuelles, recherche flexible, produit inconnu |
| Orchestration (4) | Graphe compile, routing vers tools, routing vers end, switch de prompt orchestrateur/analyste |
| Erreurs (3) | Outil inconnu capturé, mix succès/erreur, garde-fou itérations |
| API (1) | Validation: requête vide → 422, produit court → 422, marché invalide → 422, requête valide → 200 |

Tous les tests fonctionnent **sans clé API** — ils testent l'infrastructure, pas le LLM.

---

## Choix techniques

### Pourquoi LangGraph (et pas CrewAI, Google ADK, ou du natif)

**LangGraph** offre le meilleur équilibre entre contrôle et productivité pour ce cas d'usage:

- **Contrôle granulaire**: LangGraph permet de définir explicitement le flux via des nœuds et des arêtes . Chaque décision de l'agent est traçable, ce qui répond à l'exigence d'une architecture claire et maintenable.
- **État typé**: L'utilisation d'un TypedDict garantit que le contexte (l'historique des messages et les résultats des outils) circule de manière fiable entre l'orchestrateur et les outils. Cela sécurise la circulation des données au sein d'une analyse.
- **Routing conditionnel**: le mécanisme `add_conditional_edges` permet de brancher sur 3 chemins (tools, end, force_end) en une seule déclaration. En natif, il faudrait coder un if/elif/else avec la logique de routing, le dispatch vers les bonnes fonctions, et la gestion de la boucle.
- **Pattern ReAct natif**: la boucle agent → outil → agent est le cœur de LangGraph. La boucle "LLM réfléchit → outil s'exécute → LLM réfléchit à nouveau" est exactement ce que LangGraph est conçu pour faire. On n'a pas eu à inventer ce pattern, juste à le configurer.

**CrewAI** a été écarté car il abstrait trop l'orchestration — le debugging est difficile et la personnalisation du flux est limitée. **L'approche native** aurait demandé de recoder le routing, la gestion d'état et le dispatch d'outils — faisable, mais sans valeur ajoutée pour ce cas d'usage. J'ai préféré investir le temps disponible dans les fonctionnalités de robustesse (safe_tool_node, garde-fous, double prompt) plutôt que dans la réinvention de mécanismes que LangGraph fournit nativement.

### Pourquoi deux prompts spécialisés

Un seul prompt long dilue l'attention du LLM. En séparant:

- **Orchestrateur** : court, directif — "appelle les outils dans cet ordre, ne produis pas de rapport"
- **Analyste** : détaillé, analytique — "voici comment lire les données, voici le format attendu"

Le switch est automatique: quand les 3 `ToolMessage` sont dans l'historique, le code bascule vers le prompt analyste. Chaque prompt peut être optimisé indépendamment (A/B testing). Concrètement, on peut modifier le prompt analyste pour améliorer la qualité des rapports sans toucher au code d'orchestration ni aux outils — la séparation en fichier dédié (prompts.py) rend cette itération possible sans risque de casser le reste du système.

Un troisième prompt, **FORCE_END_PROMPT**, intervient uniquement quand un garde-fou se déclenche — il demande au LLM de conclure immédiatement avec les données déjà collectées.

### Pourquoi des données brutes (pas pré-analysées)
Les outils retournent des avis clients en texte brut et des chiffres de tendances sans interprétation. C'est le LLM qui fait le vrai travail d'analyse: identifier les thèmes, calculer les scores, interpréter les tendances. Cela démontre la valeur ajoutée du LLM au-delà du simple reformatage.

### Pourquoi un safe_tool_node custom

Le `ToolNode` standard de LangGraph crashe si un outil lève une exception. Notre `safe_tool_node` capture les erreurs, les retourne au LLM comme message, et permet à l'agent de continuer. En production, c'est indispensable — un timeout réseau ne doit pas tuer toute l'analyse.

### Pourquoi FastAPI
Validation automatique des requêtes via Pydantic, documentation Swagger auto-générée accessible à /docs, et support async natif. L'API peut être utilisée directement dans le navigateur sans outil externe.

### Pourquoi Groq (LLaMA 3.3 70B)
API gratuite, rapide, et compatible avec le format OpenAI. Le modèle LLaMA 3.3 70B supporte le function calling nécessaire au pattern ReAct. Le fournisseur est configurable via .env — on peut basculer vers OpenAI ou DeepSeek en changeant une variable.

---

## Réponses aux questions théoriques (étapes 4 à 7)

Dans le fichier .docx fourni en annexe.

---

## Configuration

Variables d'environnement (fichier `.env`):

| Variable | Défaut | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Clé API Groq (obligatoire) |
| `MODEL_NAME` | `llama-3.3-70b-versatile` | Modèle LLM à utiliser |
| `TEMPERATURE_MODEL` | `0.3` | Température du LLM (0-1) |
| `MAX_ITERATIONS` | `10` | Nombre max de tours dans la boucle |
| `TIMEOUT_SECONDS` | `120` | Timeout global par analyse (secondes) |
