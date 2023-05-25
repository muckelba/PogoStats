# PokéStatistics

A mini monitoring tool to collect performance data of Pokémon, quests, raids and spawnpoints. 

It uses a little bash script to collect data from a Pokémon scanning DB and write it in its own DB. [Grafana](https://grafana.com/grafana/) is used to display that data and even send notifications.

Current collected stats are:

- Live Pokémon
- Live Pokémon with IV
- Raids (split into their levels)
- Unkown spawnpoints
- Quests
- Pokéstops with incidents
- Uptime statistics for devices

![Dashboard](https://github.com/muckelba/PogoStats/assets/34460584/a630c726-614d-4cd4-9c7b-5876363b9e1c)

![Device stats overview](https://github.com/muckelba/PogoStats/assets/34460584/d4c5b11a-c5cb-48cd-b626-ff38e06ebeb4)

![Device uptime graph](https://github.com/muckelba/PogoStats/assets/34460584/74d4dab2-8bda-4b56-a982-149fd092bb14)

## Installation

To simplify the setup, this tool is running on Docker. Install Docker and docker-compose first if you haven't already.

1. Create enviroment file

Just copy the example .env file and adjust the values:

```bash 
cp .env.example .env
```

2. Create grafana_data dir and change ownership

The grafana container needs a special user ID of that volume:

```bash
mkdir grafana_data && chown 472:472 grafana_data/
```

3. Start

Start the containers in the background and watch the logs:

```bash
docker-compose up -d && docker-compose logs -f
```

## Configuration

Everything should be configured via the .env file.

### Database:

This is the database to store the performance data. You usually just need to adjust the password, everything else is fine on default

### App:

This is the little app container that runs the data collection. It needs access to the performance data database and to your scanner DB! Now this is the tricky part. Since Docker runs in its own networks, it can not access your DB running on the same server on `127.0.0.1`. You need to somehow expose the database to the app container. You can do that in two ways:

#### Socket File

You can mount the socket file of your mysql host into the app container so it feels like just connecting to `localhost`. The first step is to get the path of that file: `mysqladmin variables |grep "\.sock"`. Add that path to your .env file, change `SCANNER_HOST` to `localhost` and you're ready to go.

> Make sure to use `localhost` and not `127.0.0.1`!

#### Normal Interface (not recommended)

Binding your mysql host to normal interface is usually a security concern since, if your server is accessable from the internet, everybody can access it and thats something you should always avoid. Luckily, you can adjust your iptables to grant access from docker, but from noone else. **Make sure to change `MYSQL_CONNECTION_TYPE` to `tcp` in the .env file!**

> If you are running your scanner in docker, you can just share the network to the other container.

## Accessing the stats

Grafana is the tool to visualize the collected data. It comes with a preconfigured dashboard and should work out of the box. You can access it on port 3000. The default username and password is `admin`. You are forced to change that on the first login.

## Updating 

Updating this tool is a multi step process:

1. Update the git with  `git pull`
2. Compare your `.env` with `.env.example` and adjust it when needed
3. Update the containers. Stop your current containers with `docker-compose down`, re-build the monitoring and grafana container with `docker-compose build --pull` and update the database container with `docker-compose pull`
4. Start the containers again with `docker-compose up`. You may need to update the DB by hand since this tool does not have some sort of automatism to do that automatically. Every SQL update is basically a file in the sql directory. Check your current version with the `VERSION` file in the base directory and import the missing versions one by one via the commandline: `docker exec -i pogostats_database_1 mysql -u grafana -pchangeme grafana < sql/02_update.sql` for example. Make sure to adjust the mysql commandline parameters of course.


## Extras

### Notifications

Grafana is able to send messages when a alert is triggered. Set up a notification channel in the alerting menu on the left side. To recive notifications, you either need to set that notification channel to default or add that channel to the alerting section of the dashboard settings. You need to set the `$GF_SERVER_DOMAIN` variable if you want pictures in your notifications.

### SSL

You may want to secure Grafana with a proper reverse proxy and SSL. You can achieve that by adding a reverse proxy container to the `docker-stack.yml`, using Traefik or use a classic reverse proxy on your Docker host system. Make sure that you are adjusting the Grafana settings in the env file. The port can changed to `127.0.0.1:3000` since Grafana should only be accessable via the proxy and not on its original port. Learn more [here](https://grafana.com/docs/grafana/v4.5/installation/behind_proxy/#running-grafana-behind-a-reverse-proxy).

### Home Dashboard

To change the Home Dashboard go to Configuration-->Preferences on the left side and set your Dashboard. You need to star it first to see it in the list!
