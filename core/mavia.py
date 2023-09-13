from random import choice

import requests
from fake_useragent import UserAgent  # pip install fake-useragent

from core.utils import str_to_file, logger, get_username, CaptchaService
from string import ascii_lowercase, digits
from aiohttp import ClientSession

from inputs.config import (
    MOBILE_PROXY,
    MOBILE_PROXY_CHANGE_IP_LINK
)


class Mavia(ClientSession):
    referral = None

    def __init__(self, email: str, ds_token: str):
        headers = {
            'authority': 'be.mavia.com',
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.5',
            'authorization': 'Bearer null',
            'content-type': 'application/json',
            'origin': 'https://www.mavia.com',
            'referer': 'https://www.mavia.com/',
            'User-Agent': UserAgent().random,
        }

        super().__init__(headers=headers, trust_env=True)

        self.email = email
        self.ds_token = ds_token

        self.proxy = None

    async def define_proxy(self, proxy: str):
        if MOBILE_PROXY:
            await Mavia.change_ip()
            self.proxy = MOBILE_PROXY

        if proxy is not None:
            self.proxy = f"http://{proxy}"

    @staticmethod
    async def change_ip():
        async with ClientSession() as session:
            await session.get(MOBILE_PROXY_CHANGE_IP_LINK)

    async def enter_waitlist(self):
        url = 'https://be.mavia.com/api/wait-list'

        hcaptcha_response = await Mavia.bypass_hcaptcha()

        headers = self.headers.copy()
        headers["captcha"] = hcaptcha_response

        ds_username = await self.get_ds_username() or ""

        json_data = {
            'email': self.email,
            'referralId': int(Mavia.referral),
            'captcha': hcaptcha_response,
            'discordName': ds_username
        }

        async with self.post(url, headers=headers, proxy=self.proxy, json=json_data, ssl=False) as resp:
            return await resp.json()

    @staticmethod
    async def bypass_hcaptcha():
        captcha_service = CaptchaService()
        return await captcha_service.get_captcha_token()

    async def get_ds_username(self):
        if self.ds_token:
            return await get_username(self.ds_token, self.proxy)
        return ""

    def logs(self, file_name: str, msg_result: str = ""):
        file_msg = f"{self.email}|{self.ds_token}|{self.proxy}"
        str_to_file(f"./logs/{file_name}.txt", file_msg)

        if file_name == "success":
            logger.success(f"{self.email} | {msg_result}")
        else:
            logger.error(f"{self.email} | {msg_result}")

    @staticmethod
    def generate_password(k=10):
        return ''.join([choice(ascii_lowercase + digits) for _ in range(k)])
