# **Cashback RecSys Telegram Bot**

Implementing the idea of a recommender system to fix the exploration-exploitation problem. The PGMM (probalistic group management model) is trained for each user, independent of the total sample, which gives good metrics for the startup phase of the recommender system.


### 1. **Configurate your Telegram_id and Bot_Token** ```.env```

### 2.1 **Python:**

#### Install requirements
```
py -m pip install -r requirements.txt
```
#### Start bot
```
python bot_aio.py
``````
### 2.2 **Docker:**

#### Build Image
```
docker build -t recsys_bot .
```

#### Run containder
```
docker run recsys_bot
```
