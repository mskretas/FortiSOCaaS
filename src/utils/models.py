from dataclasses import dataclass


@dataclass
class Config:
    url: str
    api_id: str
    password: str
    client_id: str
    allow_insecure_http: bool = False

    @property
    def formatted_url(self) -> str:
        if self.url.startswith("https://"):
            f_url = self.url
        elif self.url.startswith("http://") and self.allow_insecure_http:
            f_url = self.url
        elif self.url.startswith("http://"):
            raise ValueError(f'The URL you provided needs to be HTTPS. URL: "{self.url}"')
        else:
            f_url = f"https://{self.url}"

        return f_url

    def __str__(self) -> str:
        return f"{self.formatted_url}, {self.api_id}"
