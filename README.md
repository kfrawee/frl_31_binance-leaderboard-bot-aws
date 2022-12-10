# Binance leaderboard serverless bot 🪙🤖
> Using AWS Lambda with a schedule, to get the updates from [Binance leaderboard](https://www.binance.com/en/futures-activity/leaderboard)

---
## **Setup:**
- Setup Telegram Bot:
    - For `TELEGRAM_BOT_API_KEY`: Create a new Bot; Message ([@BotFather](https://web.telegram.org/k/#@BotFather)) to create a new bot and get you bot.
    - For `TELEGRAM_CHAT_ID`:
        - Create a new chat group.
        - Add (`@RawDataBot`) to your group and type: "/start" to get the chat id. *[Reference](https://www.alphr.com/find-chat-id-telegram/)*
        - OR, Send a message to (`@username_to_id_bot`) with invitation link.

- In [serverless.yml](https://github.com/kfrawee/frl_31_binance-leaderboard-bot-aws/blob/main/serverless.yml#L34-L35), replace those two values with yours from above steps:
    - `TELEGRAM_BOT_API_KEY`
    - `TELEGRAM_CHAT_ID`
- In [serverless.yml](https://github.com/kfrawee/frl_31_binance-leaderboard-bot-aws/blob/main/serverless.yml#L59), change schedule rate:
    - [Reference](https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html)

## **Deploy to AWS:**
> This project uses [`serverless`](https://www.serverless.com/) framework ⚡. So, make sure you get that first and give the necessary permissions to `serverless cli`. Follow [this page](https://www.serverless.com/framework/docs/getting-started/) for getting started. <br>

- Deploy the stack:
    ```sh
    $ serverless deploy

    ✔ Service deployed to binance-leaderboard-bot-dev
    ```
- After deployment is successful, you can check the deployed stack details using:
    ```sh
    $ serverless info

    service: binance-leaderboard-bot
    stage: dev
    region: us-east-1
    stack: binance-leaderboard-bot-dev
    functions:
    binanceBot: binance-leaderboard-bot-dev-binanceBot
    layers:
    pybinance: arn:aws:lambda:us-east-1:xxxxx:layer:pybinance:x
    ```
## **Cleaning:**
To remove the stack and all the services and resources:

```sh
$ serverless remove

✔ Service binance-leaderboard-bot has been successfully removed
```
---