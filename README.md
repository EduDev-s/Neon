<div align="center">
  <h1>Neon</h1>
</div>

<h3>Learning bot with easy management of homework and schedules</h3>

<div>
  <img src="https://img.shields.io/github/issues/NIKTO-IZ-NIOTKYDA/Nion?style=flat-square&label=🔴 Issues&color=red">
  <img src="https://img.shields.io/github/issues-pr/NIKTO-IZ-NIOTKYDA/Nion?style=flat-square&label=🟢 PRs&color=green">
</div>

<div>
  <img src="https://img.shields.io/github/actions/workflow/status/NIKTO-IZ-NIOTKYDA/Nion/Lint.yml?branch=master&label=⚙️ Lint&style=flat-square&color=">
  <img src="https://img.shields.io/github/actions/workflow/status/NIKTO-IZ-NIOTKYDA/Nion/Build.yml?branch=master&label=📑 Build&style=flat-square&color=">
  <img src="https://img.shields.io/github/actions/workflow/status/NIKTO-IZ-NIOTKYDA/Nion/Deploy.yml?branch=master&label=🎉 Deploy&style=flat-square&color=">
</div>

<div>
  <img src="https://img.shields.io/github/license/NIKTO-IZ-NIOTKYDA/Nion?style=flat-square&label=📜 License">
  <img src="https://img.shields.io/github/contributors/NIKTO-IZ-NIOTKYDA/Nion?style=flat-square&label=👤 Contributors">
  <img src="https://img.shields.io/github/repo-size/NIKTO-IZ-NIOTKYDA/Nion?style=flat-square&label=💾 Repo size">
</div>

## Installation
### Unix:
```bash
git clone https://github.com/EduDev-s/Neon
cd Neon
cp .env.template .env
```

## Configuration  
<details>
<summary><h3>Env File</h3></summary>

| Variable                     | Description                                                             | Default Value                                |
|------------------------------|-------------------------------------------------------------------------|----------------------------------------------|
| `PROJECT_NAME`               | Project name                                                            | `Neon`                                       |
| `VERSION_MAJOR`              | Major version (SemVer)                                                  | `2`                                          |
| `VERSION_MINOR`              | Minor version (SemVer)                                                  | `0`                                          |
| `VERSION_PATCH`              | Patch version (SemVer)                                                  | `1`                                          |
| `VERSION_TYPE`               | Release type (`stable`, `unstable`, `develop`)                          | `stable`                                     |
| `RELEASE`                    | Full version (auto-generated)                                           | `${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH} [${VERSION_TYPE}]` |
| `LOG_LEVEL`                  | Logging level: `0=DEBUG`, `1=INFO`, `2=WARN`, `3=ERROR`, `4=CRITICAL`   | `1`                                          |
| `LOG_FILE_NAME`              | Log file name                                                           | `log.log`                                    |
| `BOT_TOKEN`                  | Telegram bot token (from BotFather)                                     | `1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA` |
| `NO_FOUND_HOMEWORK_MSG`      | Message when no homework is found                                       | `Не добавлено домашнее задание`              |
| `TG_ID_OWNER`                | Bot owner's Telegram UserID                                             | `1234567890`                                 |
| `TG_USERNAME_OWNER`          | Bot owner's Telegram username                                           | *Empty*                                      |
| `TG_FIRST_NAME_OWNER`        | Bot owner's first name in Telegram                                      | *Empty*                                      |
| `TG_LAST_NAME_OWNER`         | Bot owner's last name in Telegram (optional)                            | *Empty*                                      |
| `NAME_ROLE_OWNER`            | Owner role name                                                         | `Owner`                                      |
| `ID_ROLE_OWNER`              | Unique owner role ID                                                    | `-1`                                         |
| `NAME_ROLE_DEFAULT`          | Default user role name                                                  | `User`                                       |
| `ID_ROLE_DEFAULT`            | Default user role ID                                                    | `0`                                          |
| `REQUESTS_TIMEOUT`           | HTTP request timeout (seconds)                                          | `3`                                          |
| `BACKEND_HOST`               | Backend host                                                            | `localhost`                                  |
| `BACKEND_PORT`               | Backend port                                                            | `8000`                                       |
| `ENCRYPTION_KEY`             | Encryption key (32-byte Base64 string)                                  | `JHeUV1v6fQ_8FtDjeLyg8FSgO7Alsc8Mgy-0nYmBwY0=` |
| `POSTGRES_USER`              | PostgreSQL username                                                     | `postgres`                                   |
| `POSTGRES_PASSWORD`          | PostgreSQL password                                                     | `password`                                   |
| `POSTGRES_PORT`              | PostgreSQL port                                                         | `9999`                                       |
| `POSTGRES_DB`                | Database name                                                           | `app`                                        |
| `POSTGRES_URL`               | PostgreSQL connection URL (auto-generated)                              | `postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${DATABASE_CONTAINER_NAME}:${POSTGRES_PORT}/${POSTGRES_DB}` |
| `POSTGRES_DATA`              | PostgreSQL data path in container                                       | `/var/lib/postgresql/data/pgdata`            |
| `TEST_PORT_HTTP`             | NGINX HTTP test port                                                    | `5555`                                       |
| `TEST_PORT_HTTPS`            | NGINX HTTPS test port                                                   | `5556`                                       |
| `DATABASE_CONTAINER_NAME`    | PostgreSQL Docker container name                                        | `DB`                                         |
| `BOT_CONTAINER_NAME`         | Telegram bot Docker container name                                      | `BOT`                                        |
| `BACKEND_CONTAINER_NAME`     | Backend Docker container name                                           | `BACKEND`                                    |
| `NGINX_CONTAINER_NAME`       | NGINX Docker container name                                             | `NGINX`                                      |
| `VOLUME_DATABASE`            | PostgreSQL volume name                                                  | `DATABASE`                                   |

---

### Notes:
1. **VERSION_TYPE**:
   - `stable` - Production-ready version
   - `unstable` - Version for testing new features
   - `develop` - Actively developed version

2. **LOG_LEVEL**:
   - Log severity levels: `DEBUG < INFO < WARN < ERROR < CRITICAL`

3. **POSTGRES_URL**:
   - Format: `postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>`
   - Uses async `asyncpg` driver for SQLAlchemy

4. **Docker**:
   - Container and volume names correspond to variables for easier `docker-compose` management

</details>
