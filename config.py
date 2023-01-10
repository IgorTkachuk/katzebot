from dataclasses import dataclass

from environs import Env


@dataclass
class Apininjas:
    key: str


@dataclass
class TgBot:
    token: str


@dataclass
class Unsplash:
    client_id: str
    client_secret: str
    redirect_uri: str
    code: str


@dataclass
class Config:
    tgbot: TgBot
    unsplash: Unsplash
    apininjas: Apininjas


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tgbot=TgBot(
            token=env.str("BOT_TOKEN")
        ),
        unsplash=Unsplash(
            client_id=env.str("UNSPALSH_CLIENT_ID"),
            client_secret=env.str("UNSPALSH_CLIENT_SECRET"),
            redirect_uri=env.str("UNSPLASH_REDIRECT_URI"),
            code=env.str("UNSPLASH_CODE")
        ),
        apininjas=Apininjas(
            key=env.str("API_NINJAS_KEY")
        )
    )