from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OLLAMA_MODEL: str
    OLLAMA_BASE_URL: str
    OLLAMA_TOKEN: str

    TRANSCRIPTION_BASE_URL: str
    TRANSCRIPTION_USERNAME: str
    TRANSCRIPTION_PASSWORD: str

    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_QUEUE: str

    @property
    def RABBITMQ_URL(self):
        return (
            f"amqp://{self.RABBITMQ_USERNAME}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
        )


settings = Settings()
