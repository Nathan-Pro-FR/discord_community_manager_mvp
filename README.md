# Discord Community Manager — MVP 0.1

Bot Discord communautaire SFW en Python : installation de structure, statistiques agrégées, embed live, rapports périodiques et API de dashboard.

## 1. Pré-requis
- Python 3.12+ ou Docker
- Une application/bot créé dans le Discord Developer Portal
- Les intents `SERVER MEMBERS INTENT` et `MESSAGE CONTENT INTENT` activés si nécessaires dans le portail
- Permissions Discord : Manage Channels, View Channels, Send Messages, Embed Links, Read Message History

Ne partage jamais ton token. Il doit rester dans `.env`.

## 2. Installation locale
```bash
python -m venv .venv
# Windows :
.venv\\Scripts\\activate
# Linux/macOS :
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Renseigne `DISCORD_TOKEN` dans `.env`. Pour PostgreSQL local, modifie `DATABASE_URL`. SQLite est accepté pour les premiers essais.

Lance le bot :
```bash
python -m bot.main
```
Lance l'API dans un second terminal :
```bash
uvicorn dashboard.app:app --host 127.0.0.1 --port 8000
```
API de test : `http://127.0.0.1:8000/health`. Avec Docker Compose, le dashboard est exposé sur le port 8000.

## 3. Avec Docker
Modifie le mot de passe PostgreSQL dans `docker-compose.yml` et `DATABASE_URL` dans `.env`, puis :
```bash
docker compose up -d --build
docker compose logs -f bot
```

## 4. Première utilisation
1. Invite le bot sur ton serveur avec les permissions minimales nécessaires.
2. Exécute `/setup` en tant qu'administrateur.
3. Le bot crée les catégories et salons communautaires SFW.
4. Le salon `#activité` reçoit une embed actualisée chaque minute.
5. Le salon `#rapports` reçoit les rapports planifiés.
6. Utilise `/stats` et `/report`.

## 5. Rapports
- Hebdomadaire : lundi à 09:00, sur les 7 jours précédents.
- Mensuel : premier jour du mois à 09:05, sur le mois précédent.
- Trimestriel : 1er janvier, avril, juillet et octobre à 09:10, sur le trimestre précédent.
Fuseau par défaut : Europe/Paris.

## 6. Limites connues de cette première version
- Les statistiques commencent au moment où le bot est installé ; Discord ne fournit pas rétroactivement tous les événements de messages. Les jours sont calculés dans le fuseau `TIMEZONE`.
- Les compteurs journaliers utilisent la date du serveur Python ; configure le serveur en UTC ou adapte la gestion des dates pour une exploitation multi-fuseaux.
- Les rapports trimestriels planifiés sont déclenchés au début du trimestre suivant.
- Les statistiques individuelles sont des compteurs d'activité, pas une évaluation des membres.
- L'API dashboard est un prototype sans authentification : ne l'expose pas publiquement avant d'ajouter OAuth Discord, contrôle d'accès et HTTPS.
- La détection de pics, l'export PDF/CSV et l'interface graphique complète sont prévus pour les versions suivantes.
- Les événements de suppression/édition ne sont pas encore comptabilisés.
- Il faut mettre en place migrations, sauvegardes et politique de conservation avant la production.

## 7. Intents Discord
Dans Discord Developer Portal > Bot, active les intents privilégiés uniquement si ton fonctionnement les exige. Le bot ne stocke pas le contenu des messages ; l'intent Message Content est utilisé ici pour accéder aux pièces jointes via les événements de message.
