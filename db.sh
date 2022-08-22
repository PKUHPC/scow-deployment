source .env

docker compose exec db mysql -hlocalhost -P3306 -uroot -p"$MIS_DB_PASSWORD" --default-character-set=utf8mb4