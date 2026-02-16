# Deployer un nouveau projet sur Elestio (VPS 159.195.104.193)

> Guide pas-a-pas pour ajouter un projet Django (ou autre) sur le VPS Elestio
> partage, sans galerer avec le SSL, les 502, ou les conflits de ports.
>
> Ecrit a partir de toutes les erreurs deja rencontrees avec Latigue et MinIO.

---

## Table des matieres

1. [Architecture du VPS](#1-architecture-du-vps)
2. [Avant de commencer (checklist)](#2-avant-de-commencer)
3. [Etape 1 — Preparer le projet](#3-etape-1--preparer-le-projet)
4. [Etape 2 — Deployer sur Elestio](#4-etape-2--deployer-sur-elestio)
5. [Etape 3 — Configurer le reverse proxy (SSL)](#5-etape-3--configurer-le-reverse-proxy-ssl)
6. [Etape 4 — DNS (Gandi)](#6-etape-4--dns-gandi)
7. [Etape 5 — Verification](#7-etape-5--verification)
8. [Etape 6 — Post-deploiement](#8-etape-6--post-deploiement)
9. [Les pieges a eviter (retour d'experience)](#9-les-pieges-a-eviter)
10. [Commandes de reference](#10-commandes-de-reference)
11. [Arborescence du VPS](#11-arborescence-du-vps)

---

## 1. Architecture du VPS

```
Internet (HTTPS, port 443)
         |
         v
  ┌─────────────────────────────────────────────────────┐
  │  elestio-nginx (OpenResty)                          │
  │  /opt/elestio/nginx/                                │
  │  - Ports 80/443                                     │
  │  - SSL automatique (resty-auto-ssl + Let's Encrypt) │
  │  - Reverse proxy vers les services Docker           │
  └──────────┬──────────┬──────────┬────────────────────┘
             |          |          |
     port 8000    port 9001    port 18789
             |          |          |
        ┌────┴───┐ ┌────┴───┐ ┌───┴────────┐
        │Latigue │ │ MinIO  │ │ OpenClaw   │
        │(Django)│ │Console │ │            │
        └────────┘ └────────┘ └────────────┘
```

### Services actuels

| Service | Port interne | Domaine | Fichier conf.d |
|---------|-------------|---------|----------------|
| Latigue (Django) | 8000 | bolibana.net, www.bolibana.net | `latigue-u67346.vm.elestio.app.conf` |
| MinIO Console | 9001 | minio.bolibana.net | `minio.conf` |
| MinIO API S3 | 9000 | s3.bolibana.net | `minio.conf` |
| OpenClaw | 18789 | openclaw-u67346.vm.elestio.app | `openclaw-u67346.vm.elestio.app.conf` |
| PostgreSQL | 5432 (local) / 25432 (externe) | postgres-u67346.vm.elestio.app | `postgres-u67346.vm.elestio.app.conf` |
| PgAdmin | 8080 | - | - |

### Ports deja utilises (ne pas reutiliser)

`80, 443, 8000, 8080, 9000, 9001, 18789, 25432`

---

## 2. Avant de commencer

### Checklist pre-deploiement

- [ ] Le projet a un `Dockerfile` fonctionnel
- [ ] Le projet a un `docker-compose.yml` (voir regles ci-dessous)
- [ ] Le port interne est defini et ne conflicte pas avec les ports ci-dessus
- [ ] Le nom de domaine est achete et le DNS est geré (Gandi)
- [ ] Les variables d'environnement sont listees (DB, secrets, etc.)
- [ ] Il reste assez d'espace disque sur le VPS (`df -h /`, minimum 5 Go libres)

### Regles du docker-compose.yml pour Elestio

```yaml
# CE QU'IL FAUT :
services:
  web:
    build: .
    restart: unless-stopped
    ports:
      - "XXXX:XXXX"    # Port unique, pas deja utilise
    env_file:
      - .env            # PAS .env.production (Elestio cree .env)
    volumes:
      - ./data:/app/data

# CE QU'IL NE FAUT JAMAIS :
#   - container_name: ...      (cause "already in use" au redeploiement)
#   - service nginx/certbot    (Elestio gere deja le proxy + SSL)
#   - ports: "80:80" ou "443:443"  (deja pris par elestio-nginx)
```

**Important** : Elestio ecrase le `docker-compose.yml` a chaque deploiement
avec la version stockee dans le Dashboard. Les modifs dans Git ne suffisent pas :
il faut AUSSI mettre a jour le docker-compose dans le Dashboard Elestio.

---

## 3. Etape 1 — Preparer le projet

### 3.1 Dockerfile

Points essentiels :

```dockerfile
# Utiliser une image recente (pas de version patch fixe type python:3.9.4-slim)
FROM python:3.11-slim-bookworm

# Installer curl pour le healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE XXXX

# Healthcheck : OBLIGATOIRE pour eviter les 502
HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
  CMD curl -f http://localhost:XXXX/health/ || exit 1

CMD ["votre_commande_de_demarrage"]
```

Regles :
- **start_period: 90s** minimum (temps pour migrations + collectstatic)
- **Pas de `set -e`** dans le script d'entree (si une etape echoue, le serveur
  doit quand meme demarrer pour eviter le 502)
- Endpoint `/health/` qui repond 200

### 3.2 Variables d'environnement

Creer un fichier `.env.example` dans le repo (sans les vrais secrets) :

```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=changeme
DB_HOST=postgres-u67346.vm.elestio.app
DB_PORT=25432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=changeme
```

Regles :
- Pas d'espace en debut de ligne
- Valeurs avec `$`, `(`, `)`, `!` : entourer de guillemets simples `'...'`
- Sur Elestio, le fichier `.env` est cree automatiquement (pas `.env.production`)

### 3.3 elestio.yml

Creer a la racine du projet :

```yaml
ports:
  - protocol: "HTTPS"
    targetProtocol: "HTTP"
    listeningPort: "443"
    targetPort: "XXXX"       # <-- Le port de votre app
    targetIP: "172.17.0.1"
    public: true
    path: "/"
    isAuth: false

environments:
  - key: "DJANGO_DEBUG"
    value: "False"
  - key: "DOMAIN"
    value: "[CI_CD_DOMAIN]"

config:
  runTime: "dockerCompose"
  buildCommand: "docker-compose build"
  buildDir: "/"
  runCommand: "docker-compose up -d"

webUI:
  - url: "https://[CI_CD_DOMAIN]"
    label: "Mon Projet"
```

---

## 4. Etape 2 — Deployer sur Elestio

### Option A : Pipeline CI/CD (recommande)

1. **Elestio Dashboard** → Create CI/CD Pipeline
2. Source : GitHub, branche `main`, path `docker-compose.yml`
3. Copier le `docker-compose.yml` dans le Dashboard (rappel : Elestio ecrase celui du repo)
4. Definir les variables d'environnement dans le Dashboard
5. Deployer

### Option B : Deploiement manuel (SSH)

```bash
ssh root@159.195.104.193
cd /opt/app

# Cloner le projet
git clone https://github.com/<user>/<projet>.git
cd <projet>

# Creer le .env
cp .env.example .env
nano .env   # Remplir les vrais secrets

# Build et lancer
docker compose build
docker compose up -d

# Verifier
docker compose ps
docker compose logs -f
```

### Verifier que le service repond

```bash
curl -s http://localhost:XXXX/health/
# Doit repondre 200 ou "ok"
```

---

## 5. Etape 3 — Configurer le reverse proxy (SSL)

C'est l'etape ou on a le plus galere. Suivre ces 3 sous-etapes **dans l'ordre**.

### 5.1 Ajouter le domaine dans ALLOWED_DOMAINS

```bash
nano /opt/elestio/nginx/.env
```

Ajouter votre domaine a la fin de `ALLOWED_DOMAINS` (separateur `|`) :

```
ALLOWED_DOMAINS=...existants...|monprojet.bolibana.net
```

### 5.2 Creer le fichier conf.d

```bash
nano /opt/elestio/nginx/conf.d/monprojet.conf
```

**Template a copier-coller :**

```nginx
map $http_upgrade $connection_upgrade_monprojet {
  default upgrade;
  '' close;
}

server {
  listen 443 ssl;
  http2 on;

  # ┌──────────────────────────────────────────────────────────────┐
  # │  IMPORTANT : utiliser resty-auto-ssl pour le SSL            │
  # │  NE PAS utiliser :                                          │
  # │    ssl_certificate /etc/nginx/certs/cert.pem;               │
  # │    ssl_certificate_key /etc/nginx/certs/key.pem;            │
  # │  Car ce certificat est wildcard *.elestio.app et ne couvre  │
  # │  PAS les domaines personnalises (bolibana.net, etc.)        │
  # └──────────────────────────────────────────────────────────────┘
  include /usr/local/openresty/nginx/conf/resty-server-https.conf;

  server_name monprojet.bolibana.net monprojet-u67346.vm.elestio.app;

  location / {
    proxy_http_version 1.1;
    proxy_pass http://172.17.0.1:XXXX/;       # <-- Port de votre service
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Port $server_port;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $connection_upgrade_monprojet;

    proxy_read_timeout 180s;
    proxy_send_timeout 180s;
    proxy_connect_timeout 180s;
  }
}
```

### 5.3 Recreer le conteneur OpenResty

**ATTENTION** : `docker compose restart` ne suffit PAS si vous avez modifie
`ALLOWED_DOMAINS`. Le fichier `resty-http.conf` (qui contient la liste Lua des
domaines autorises) est genere **au demarrage** du conteneur, pas au restart.

```bash
cd /opt/elestio/nginx
docker compose down && docker compose up -d
```

Attendez 15 secondes pour que resty-auto-ssl obtienne le certificat Let's Encrypt.

### 5.4 Verifier le SSL

```bash
echo | openssl s_client -connect monprojet.bolibana.net:443 \
  -servername monprojet.bolibana.net 2>/dev/null \
  | openssl x509 -noout -subject

# ATTENDU :   subject=CN = monprojet.bolibana.net
# PAS BON :   subject=CN = *.elestio.app
```

Si vous voyez `*.elestio.app` : le fichier conf.d utilise encore le certificat
wildcard statique. Verifiez qu'il contient bien
`include resty-server-https.conf` et pas `ssl_certificate /etc/nginx/certs/cert.pem`.

---

## 6. Etape 4 — DNS (Gandi)

Ajouter un enregistrement A chez Gandi :

```
monprojet  10800  IN  A  159.195.104.193
```

**Ne PAS toucher** aux enregistrements existants (MX, TXT, SRV, _domainkey, webmail).

Verification de la propagation :

```bash
dig +short monprojet.bolibana.net
# Doit retourner : 159.195.104.193
```

La propagation DNS peut prendre 15 min a 48h (souvent ~15 min avec Gandi).

---

## 7. Etape 5 — Verification

### Tests en ligne de commande

```bash
# 1. Le service repond localement ?
curl -s http://localhost:XXXX/health/

# 2. Le proxy HTTPS fonctionne ?
curl -sI https://monprojet.bolibana.net/
# Attendu : HTTP/2 200

# 3. Le certificat est valide ?
echo | openssl s_client -connect monprojet.bolibana.net:443 \
  -servername monprojet.bolibana.net 2>/dev/null \
  | openssl x509 -noout -subject -dates
```

### Tests navigateur

- [ ] Le site charge sans erreur SSL
- [ ] Le cadenas est vert
- [ ] Les fonctionnalites principales marchent

---

## 8. Etape 6 — Post-deploiement

### 8.1 Backups

```bash
# Backup de la base de donnees
docker exec -e PGPASSWORD=XXX <conteneur> pg_dump -h DB_HOST -p DB_PORT -U DB_USER DB_NAME \
  | gzip > /var/backups/monprojet_$(date +%Y%m%d).sql.gz

# Cron quotidien a 3h du matin
(crontab -l; echo "0 3 * * * /opt/app/monprojet/backup.sh >> /var/log/monprojet-backup.log 2>&1") | crontab -
```

### 8.2 Monitoring

Ajouter un healthcheck cron :

```bash
# Toutes les 5 minutes
(crontab -l; echo "*/5 * * * * curl -sf http://localhost:XXXX/health/ || docker restart monprojet-web-1") | crontab -
```

### 8.3 Nettoyage Docker regulier

Le VPS a 58 Go. Nettoyer regulierement :

```bash
# Voir l'espace
df -h /
docker system df

# Nettoyer (images/volumes inutilises)
docker system prune -a --volumes -f
```

---

## 9. Les pieges a eviter

Retour d'experience de tous les problemes rencontres.

### Piege 1 : ERR_CERT_COMMON_NAME_INVALID (SSL)

| Cause | Le fichier conf.d utilise `ssl_certificate /etc/nginx/certs/cert.pem` |
|-------|------|
| **Pourquoi** | Ce certificat couvre uniquement `*.elestio.app`, pas vos domaines |
| **Solution** | Remplacer par `include resty-server-https.conf;` |
| **Ref** | `SSL_ELESTIO.md` |

### Piege 2 : `docker compose restart` ne prend pas les nouveaux domaines

| Cause | `resty-http.conf` (liste Lua des domaines) est genere au **demarrage** |
|-------|------|
| **Solution** | `docker compose down && docker compose up -d` (pas juste restart) |

### Piege 3 : 502 Bad Gateway

| Cause possible | Solution |
|----------------|----------|
| Le conteneur n'est pas encore pret | Ajouter `start_period: 90s` au healthcheck |
| Le port dans `proxy_pass` est faux | Verifier : `grep proxy_pass /opt/elestio/nginx/conf.d/*.conf` |
| Le script d'entree fait `set -e` et crash | Utiliser `set +e`, rendre les etapes non bloquantes |
| Variables d'env manquantes | Verifier : `docker exec <conteneur> env` |

### Piege 4 : `container_name already in use`

| Cause | Directive `container_name` fixe dans docker-compose.yml |
|-------|------|
| **Solution** | Ne JAMAIS utiliser `container_name`. Docker gere les noms automatiquement |

### Piege 5 : `.env.production not found`

| Cause | Elestio cree `.env`, pas `.env.production` |
|-------|------|
| **Solution** | Utiliser `env_file: .env` dans docker-compose.yml |

### Piege 6 : Port 80/443 deja utilise

| Cause | `elestio-nginx` utilise deja ces ports |
|-------|------|
| **Solution** | Ne JAMAIS mettre de service nginx/certbot dans le docker-compose |

### Piege 7 : Les modifs du docker-compose.yml dans Git ne prennent pas effet

| Cause | Elestio ecrase le fichier avec sa copie interne a chaque build |
|-------|------|
| **Solution** | Modifier AUSSI dans Dashboard Elestio → Docker Compose |

### Piege 8 : Variables avec `$` dans la SECRET_KEY

| Cause | `$buhd` dans la valeur est interprete comme variable shell |
|-------|------|
| **Solution** | Entourer de guillemets simples : `DJANGO_SECRET_KEY='ma$cle'` |

### Piege 9 : Espaces en debut de ligne dans .env

| Cause | Docker ignore les lignes avec espaces au debut |
|-------|------|
| **Solution** | Chaque ligne commence directement par `NOM_VARIABLE=valeur` |

### Piege 10 : Elestio ecrase les conf.d apres un redeploiement

| Cause | Elestio peut regenerer les fichiers conf.d avec le cert wildcard |
|-------|------|
| **Solution** | Relancer le script : `bash /opt/app/latigue/scripts/elestio-fix-ssl-domains.sh` |

---

## 10. Commandes de reference

### Gestion des conteneurs

```bash
# Voir tous les conteneurs
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Logs d'un service
docker logs <nom-conteneur> -f --tail 100

# Entrer dans un conteneur
docker exec -it <nom-conteneur> bash

# Commandes Django
docker exec <nom-conteneur> python manage.py migrate
docker exec <nom-conteneur> python manage.py createsuperuser
docker exec <nom-conteneur> python manage.py collectstatic --noinput
```

### Gestion d'OpenResty (proxy + SSL)

```bash
# Voir la config active
cat /opt/elestio/nginx/conf.d/<fichier>.conf

# Voir les domaines autorises
cat /opt/elestio/nginx/.env

# Voir la liste Lua des domaines (dans le conteneur)
docker exec elestio-nginx cat /usr/local/openresty/nginx/conf/resty-http.conf | grep allow_domain -A5

# Tester la config sans redemarrer
docker exec elestio-nginx openresty -t

# Recharger la config (si modif conf.d uniquement)
docker exec elestio-nginx nginx -s reload

# Recreer le conteneur (si modif ALLOWED_DOMAINS)
cd /opt/elestio/nginx && docker compose down && docker compose up -d
```

### Diagnostic SSL

```bash
# Verifier le certificat d'un domaine
echo | openssl s_client -connect DOMAINE:443 -servername DOMAINE 2>/dev/null \
  | openssl x509 -noout -subject -issuer -dates

# Verifier tous les domaines bolibana.net
for d in bolibana.net www.bolibana.net minio.bolibana.net s3.bolibana.net; do
  echo -n "$d : "
  echo | openssl s_client -connect "$d:443" -servername "$d" 2>/dev/null \
    | openssl x509 -noout -subject 2>/dev/null || echo "ERREUR"
done
```

### Espace disque

```bash
df -h /                  # Espace disque global
docker system df         # Espace utilise par Docker
du -sh /opt/app/*/       # Taille de chaque projet
docker system prune -a --volumes -f   # Nettoyer
```

### Script de reparation SSL (si ca casse)

```bash
bash /opt/app/latigue/scripts/elestio-fix-ssl-domains.sh
```

---

## 11. Arborescence du VPS

```
/opt/app/
├── latigue/           # Django (bolibana.net)
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── .env
│   ├── manage.py
│   ├── latigue/       # settings, urls, wsgi
│   ├── portfolio/
│   ├── blog/
│   ├── services/
│   ├── formations/
│   ├── marketing/
│   ├── scripts/
│   │   └── elestio-fix-ssl-domains.sh
│   └── ...
├── minio/             # MinIO (stockage S3)
│   ├── docker-compose.yml
│   ├── .env
│   └── data/
├── openclaw/          # OpenClaw
│   ├── docker-compose.yml
│   └── .env
└── postgres/          # PostgreSQL + PgAdmin
    ├── docker-compose.yml
    └── data/

/opt/elestio/
└── nginx/             # OpenResty (reverse proxy + SSL)
    ├── .env           # ALLOWED_DOMAINS
    ├── docker-compose.yml
    ├── conf.d/        # Configs des services
    │   ├── latigue-u67346.vm.elestio.app.conf
    │   ├── minio.conf
    │   ├── openclaw-u67346.vm.elestio.app.conf
    │   └── postgres-u67346.vm.elestio.app.conf
    ├── ssl_data/      # Certificats resty-auto-ssl
    └── logs/
```

---

## Resume : les 5 etapes pour un nouveau projet

```
1. Preparer le projet (Dockerfile, docker-compose.yml, .env, elestio.yml)
2. Deployer (git clone + docker compose up, ou CI/CD Elestio)
3. Proxy SSL :
   a. Ajouter domaine dans ALLOWED_DOMAINS
   b. Creer conf.d avec « include resty-server-https.conf »
   c. docker compose down && up (PAS juste restart)
4. DNS : A record vers 159.195.104.193
5. Verifier : curl, openssl, navigateur
```

---

## Documentation liee

| Document | Contenu |
|----------|---------|
| `SSL_ELESTIO.md` | Comment fonctionne le SSL, diagnostic et correction |
| `DEPLOIEMENT_VPS_ELESTIO.md` | Historique complet du deploiement Latigue |
| `ELESTIO_TROUBLESHOOTING.md` | Tous les problemes rencontres avec le pipeline CI/CD |
| `MINIO_SETUP.md` | Integration MinIO avec Django |
| `minio/README.md` | Deploiement MinIO et configuration SSL |

---

*Derniere mise a jour : 16 fevrier 2026*
