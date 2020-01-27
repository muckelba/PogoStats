# PokéStatistics

A mini Monitoring tool to collect performance data of Pokémon, Quests, Raids and Spawnpoints. 

It uses a little bash script to collect data from a Pokémon Scanning DB and write it in its own DB. [Grafana](https://grafana.com/grafana/) is used to display that data and even send notifications.

![Dashboard](https://user-images.githubusercontent.com/34460584/71187549-8ffaf100-227f-11ea-8f85-7497772b2f29.png)

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

```bash
docker-compose up
```

## Configuration

Everything should be configured via the .env file.

### Database:

This is the database to store the performance data. You usually just need to adjust the password, everything else is fine on default

### App:

This is the little app container that runs the data collection. It needs access to the performance data database and to your scanner DB! Now this is the tricky part. Since Docker runs in its own networks, it can not access your DB running on the same server on `127.0.0.1`. You need to somehow expose the database to the app container. You can do that in two ways:

#### Socket File

You can mount the socket file of your mysql host into the app container so it feels like just connecting to `localhost`. The first step is to get the path of that file: `mysqladmin variables |grep "\.sock"`. Add that path to your .env file and change `SCANNER_HOST` to localhost and you're ready to go.

#### Normal Interface (not recommended)

Binding your mysql host to normal interface is usually a security concern since, if your server is accessable from the internet, everybody can access it and thats something you should always avoid. Luckily, you can adjust your iptables to grant access from docker, but from noone else. 

> If you are running your scanner in docker, you can just share the network to the other container.

## Accessing the stats

Grafana is the tool to visualize the collected data. It comes with a preconfigured dashboard and should work out of the box. You can access it on port 3000. The default username and password is `admin`. You are forced to change that on the first login.

## Updating 

Updating this tool is a multi step process. First you need to update the git with  `git pull`. Second step is to re-build the container. Stop your current containers with `docker-compose down` and start and build the new ones with `docker-compse up --build`. When every container is running again, you may need to update the DB by hand since this tool does not have some sort of automatism to do that automatically. Every SQL update is basically a file in the sql directory. Check your current version with the `VERSION` file in the base directory and import the missing versions one by one via the commandline: `docker exec -it pogostats_database_1 mysql -u grafana -pchangeme grafana < sql/02_update.sql` for example. Make sure to adjust the mysql commandline parameters of course.

## Extras

### Notifications

Grafana is able to send messages when a alert is triggered. Set up a notification channel in the Alerting menu on the left side. To recive notifications, you either need to set that notification channel to default or add that channel to the alerting section of the dashboard settings. You need to set the `$GF_SERVER_DOMAIN` variable if you want pictures in your notifications.

### SSL

You may want to secure Grafana with a proper reverse proxy and SSL. You can achieve that by adding a reverse proxy container to the `docker-stack.yml`, using Traefik or use a classic reverse proxy on your Docker host system. Make sure that you are adjusting the Grafana settings in the env file. The port can changed to `127.0.0.1:3000:3000` since Grafana should only be accessable via the proxy and not on its original port. Learn more [here](https://grafana.com/docs/grafana/v4.5/installation/behind_proxy/#running-grafana-behind-a-reverse-proxy).

### Home Dashboard

To change the Home Dashboard go to Configuration-->Preferences on the left side and set your Dashboard. You need to star it first to see it in the list!
