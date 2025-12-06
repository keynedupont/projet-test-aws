# 📖 Guide Utilisateur

> Guide d'utilisation de la plateforme ML

## 🚀 Démarrage rapide

### 1. Créer un compte

1. Accédez à la page d'accueil : `http://localhost:8001`
2. Cliquez sur **"S'inscrire"** ou allez sur `/signup`
3. Remplissez le formulaire :
   - **Email** : Votre adresse email
   - **Mot de passe** : Au moins 8 caractères, avec majuscule, minuscule, chiffre et caractère spécial
   - **Prénom** et **Nom** (optionnels)
4. Cliquez sur **"Créer mon compte"**

### 2. Vérifier votre email

Après l'inscription, vous recevrez un email de vérification (selon la configuration) :
- **Mode développement** : L'email s'affiche dans la console ou est écrit dans un fichier
- **Mode production** : L'email est envoyé via SMTP

**Option 1 : Vérification automatique (dev)**
- Si `SKIP_EMAIL_VERIFICATION=true` dans `.env`, votre compte est automatiquement vérifié

**Option 2 : Vérification manuelle**
- Cliquez sur le lien dans l'email reçu
- Ou allez sur `/verify-email` et entrez le token reçu
- Ou utilisez `/resend-verification` pour recevoir un nouveau token

### 3. Se connecter

1. Allez sur `/login`
2. Entrez votre **email** et **mot de passe**
3. Cliquez sur **"Se connecter"**
4. Vous êtes redirigé vers le **dashboard**

## 📊 Utilisation de l'application

### Dashboard

Le dashboard (`/dashboard`) affiche :
- Vos informations personnelles
- Statistiques de votre compte
- Accès rapide aux fonctionnalités

### Mon compte

Accédez à `/account` pour :
- Voir vos informations personnelles
- Modifier votre profil (prénom, nom)
- Changer votre mot de passe

### Paramètres

Accédez à `/settings` pour :
- Gérer vos préférences
- Configurer les notifications

## 🔐 Gestion du mot de passe

### Changer son mot de passe

1. Allez sur `/account` ou `/change-password`
2. Entrez votre **mot de passe actuel**
3. Entrez votre **nouveau mot de passe** (2 fois pour confirmation)
4. Cliquez sur **"Changer le mot de passe"**
5. Vous serez déconnecté et devrez vous reconnecter avec le nouveau mot de passe

### Mot de passe oublié

1. Allez sur `/forgot-password`
2. Entrez votre **email**
3. Cliquez sur **"Envoyer le lien de réinitialisation"**
4. Vous recevrez un email avec un lien de réinitialisation
5. Cliquez sur le lien ou copiez le token
6. Allez sur `/reset-password` et entrez :
   - Le **token** reçu par email
   - Votre **nouveau mot de passe** (2 fois)
7. Cliquez sur **"Réinitialiser le mot de passe"**

## 👨‍💼 Panel d'administration

> **Accès réservé aux administrateurs**

### Accès au panel admin

1. Connectez-vous avec un compte **admin**
2. Allez sur `/admin` ou cliquez sur **"Administration"** dans le menu

### Créer un compte admin

Si aucun admin n'existe, créez-en un :

```bash
make create-admin ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=AdminPass123!
```

Ou manuellement :

```bash
python scripts/create_admin.py --email admin@example.com --password AdminPass123!
```

### Fonctionnalités admin

#### Tableau de bord (`/admin`)
- Vue d'ensemble des statistiques
- Nombre d'utilisateurs, rôles, etc.

#### Gestion des utilisateurs (`/admin/users`)
- **Liste des utilisateurs** : Voir tous les utilisateurs
- **Modifier un utilisateur** (`/admin/users/{id}/edit`) :
  - Modifier email, prénom, nom
  - Activer/désactiver le compte
  - Forcer la vérification email
  - Réinitialiser le mot de passe
  - Gérer les rôles

#### Gestion des rôles (`/admin/roles`)
- Voir tous les rôles disponibles
- Nombre d'utilisateurs par rôle

#### Statistiques (`/admin/stats`)
- Statistiques détaillées de la plateforme

#### Logs d'audit (`/admin/logs`)
- Historique des actions (à venir)

#### Configuration (`/admin/settings`)
- Paramètres système (à venir)

### Navigation dans le panel admin

- **Sidebar** : Navigation rapide entre les sections
- **Collapsible** : Cliquez sur la flèche en bas de la sidebar pour la replier/déplier
- **Responsive** : Sur mobile, la sidebar s'affiche en overlay

## 🔧 Configuration email

### Mode développement

Par défaut, les emails ne sont pas envoyés en développement. Configurez dans `.env` :

```bash
# Backend email : console, file, ou smtp
EMAIL_BACKEND=console  # Affiche l'email dans la console
# ou
EMAIL_BACKEND=file     # Écrit l'email dans un fichier
# ou
EMAIL_BACKEND=smtp     # Envoie l'email via SMTP
```

### Mode production (SMTP)

Pour envoyer de vrais emails, configurez SMTP dans `.env` :

```bash
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=votre-email@gmail.com
SMTP_PASSWORD=votre-app-password  # App Password pour Gmail
SMTP_FROM=noreply@example.com
```

**Note Gmail** : Utilisez un **App Password** (pas votre mot de passe principal). Voir [Gmail App Passwords](https://support.google.com/accounts/answer/185833).

### Skip email verification (dev)

Pour tester sans vérification email :

```bash
SKIP_EMAIL_VERIFICATION=true
```

Les nouveaux comptes seront automatiquement vérifiés.

## 🆘 Dépannage

### Je ne reçois pas l'email de vérification

1. Vérifiez votre configuration email dans `.env`
2. En mode `console`, regardez les logs du serveur
3. En mode `file`, vérifiez le fichier de logs
4. Vérifiez vos spams
5. Utilisez `/resend-verification` pour recevoir un nouveau token

### Je ne peux pas me connecter

1. Vérifiez que votre email est vérifié (si requis)
2. Vérifiez que votre compte est actif (contactez un admin si nécessaire)
3. Utilisez "Mot de passe oublié" pour réinitialiser

### J'ai oublié mon mot de passe

Utilisez la fonctionnalité "Mot de passe oublié" (`/forgot-password`).

### Je veux devenir admin

Contactez un administrateur existant pour qu'il vous attribue le rôle `admin`.

## 📝 Notes importantes

- **Sécurité** : Ne partagez jamais vos identifiants
- **Mots de passe** : Utilisez des mots de passe forts et uniques
- **Sessions** : Déconnectez-vous après utilisation sur un ordinateur partagé
- **Email** : Gardez votre email à jour pour recevoir les notifications

## 🔗 Liens utiles

- **API Documentation** : `http://localhost:8000/docs` (Swagger UI)
- **Health Check** : `http://localhost:8000/health` (Auth service)
- **Health Check** : `http://localhost:8001/health` (Web app)

---

*Pour plus d'informations techniques, consultez la [documentation technique](README.md).*

