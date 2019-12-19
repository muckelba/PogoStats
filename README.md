# PokéStatistics

A mini Monitoring tool to collect performance data of Pokémon, Quests, Raids and Spawnpoints. 

It uses a little bash script to collect data from a Pokémon Scanning DB and write it in its own DB. [Grafana](https://grafana.com/grafana/) is used to display that data and even send notifications.

## Installation

To simplify the setup, this tool is running on Docker. Install Docker and docker-compose first if you haven't already.

1. Create enviroment file

Just copy the example .env file and adjust the values:

```bash 
cp .env.example .env
```
2. Start

```bash
docker-compose up
```

## Configuration

Everything should be configured via the .env file.

### Database:

This is the database to store the performance data. You usually just need to adjust the password, everything else is fine on default

### App:

This is the little app container that runs the data collection. It needs access to the performance data database and to your scanner DB! Now this is the tricky part. Since Docker runs in its own networks, it can not access your DB running on the same server on `127.0.0.1`. You need to expose the database to your normal interface so docker can connect to it. That step is a security concern since if your server is accessable from the internet, everybody can access it and thats something you should always avoid. Luckely, you can adjust your iptables to grant access from docker, but from noone else. 

If you are running your scanner in docker, you can just share the network to the other container.

## Accessing the stats

Grafana is the tool to visualize the collected data. It comes with a preconfigured dashboard and should work out of the box. You can access it on port 3000. The default username and password is `admin`. You are forced to change that on the first login.

## Extras

### Notifications

Grafana is able to send messages when a alert is triggered. Set up a notification channel in the Alerting menu on the left side. To recive notifications, you either need to set that notification channel to default or add that channel to the alerting section of the dashboard settings. You need to set the `$GF_SERVER_DOMAIN` variable if you want pictures in your notifications.

### SSL

You may want to secure Grafana with a proper reverse proxy and SSL. You can achieve that by adding a reverse proxy container to the `docker-stack.yml`, using Traefik or use a classic reverse proxy on your Docker host system.

### Home Dashboard

To change the Home Dashboard go to Configuration-->Preferences on the left side and set your Dashboard. You need to star it first to see it in the list!