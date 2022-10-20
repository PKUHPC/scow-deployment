python generate.py

if docker compose version &> /dev/null
then
  docker compose -f docker-compose.json $@

elif docker-compose version &> /dev/null
then
    docker-compose -f docker-compose.json $@
else
    echo -e  "\033[31mDocker Compose is not installed, refer to this connection for installation:\nhttps://docs.docker.com/compose/install/linux/#install-the-plugin-manually\033[0m"
fi