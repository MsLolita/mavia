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
            'accept-language': 'en-US,en;q=0.9',
            'authorization': 'Bearer null',
            'captcha': 'P1_eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.hKdwYXNza2V5xQR_EGuKYW3EVJR-vgzA3LQR-gJP8xttg4_7IvkBV8eCDaFXlyMpy4uSflDt1pJLooqgfahkvjbytPG9ZMs7-1odGQkUu3Gif92EBUoA18LNsSrmwVIA_Sw2Fyg2394YE3DSl97D6Zf5C6HVz6Ll6fRbQCm-XshO0lVoMRz5C6XtFfC4RqExOT8ovmjEiAONnapDnEc6AJx_JhFfTijqD-PtTOKgXjo9rkcPezeGBkMUrxkRnNUSyeqsGdOIywCxCeyDE6UJLSfDXwFT6mHcirpwYISZwZPyJu-LvwnTS5mvf8rWRPYSdAFS4h45QsCAYWZhwZ7ZtV0wfpx_gDI8ebVIcMo-kXM-JSsK5170TaI2BRzfl8wGiLaXsaRoeC2Zbh53CRoKetAp5olLsB98lUdPCKR7n9QBELQTbqdgfByVqUaHw3g9HcK5-lbVjBcxINgmDwvTSZDA1zKb9765yRI8oWBNypLZCQCTJfIqHx0tAc_Pt8JEk6GeD8BrBwoVleomiIW8wWPB8XppvI6LFC1hScwaau5l7Y745fzaxjTjdw3W27cJ4l97REATDSIjTeFZN62EIiCUlVO77mVAqzAedITJN2PcTLVu1ytDVdOLSMm7flUdlwhTg63q5FURmN6FwWUz9HG-PyB5FQbyOnDy1VZGBOGYK3JbnF2KzH7_UVcGd4m0VNyjsbdOvj_WEjOlOZAzYBJCbEid1REn-vuO_04vwENIAU_V9sBMPtg5xKOJDlcipKiENRQ4wP-fyBFRoGziSr9qeYclyhF0kxS4livnYakfT-KY9DfEEMyUVUASF2oohu5M3FiIP6TnnwWmhGduD-yP-0_1XU9efAQvJ2Lobu7jTaVKj49YuGfHhFVaGFA_5rv_U-vt27N7KlezdekmOA-Jl6FPDIvx-r29SGVFNyomTo0LnJQxefM3Pu1vmfpOUPM4ec4UzScDUsORIQIsNXPv0bgKLpSedFBShrKzR2USqNzsUldB6q4ml92CzQ9WOCHQ35Ow6c414f1i6-UXcdCBivMmaFIC4gj67Cic5Cy8QzFH-kZvv5uC0X3B8JkDa-Myq88ArnyEQOQnBXDupxqTFePStIpEyqF5NPF5m31pse22owf9GD8znjvBm27UKycJvD-v4ZrqvrzcebxEiJeCUfn5YjO_5mUUTg2ydRqgkxhgFjgOjHrWTOb-zLHdFakfLcGPn3D8yHY-NW6TQsDUohsy3NHlz_R_a5MFU3HzD-MAH0cg3C4F1Z-NEjr-cHVRUTEBGGNGc0_0paEUfkDNK6tXOP6Cpvq3s1K1B5H5Pn4JLiiL7DFecESZvh-ChhyE39YfYNEwsleqRd4nw5pPXtUCLQ-yBVlGzdI2QxKxqtpaRi1--0h3-TGkudpOWdrDnUZ_YcBrNMfzz618CxFjtBN8rWIRlmZ8JZkrFGY4sRu75xvAkygC9ZWQxOWOqYYVhFR6uRBH6Qj35eKImLG5HT2-s9Z_bdGowmv5mjFUJy2ifxqE_5QerCF37KJTqEl7zJ435FOBRyWjZXhwzmT-0Wqoc2hhcmRfaWTOFDyEH6JwZAA.zQuypeJI8D4oWbQq7gqtygvei0OcteaVmruvk5SxlQw',
            'content-type': 'application/json',
            'origin': 'https://www.mavia.com',
            'referer': 'https://www.mavia.com/',
            'User-Agent': UserAgent().random,
        }

        super().__init__(headers=headers, trust_env=True)

        self.email = email
        self.ds_token = ds_token

        self.proxy = None
        # self.session = requests.Session()
        #
        # self.session.headers.update(self.headers)
        # self.session.proxies.update({'https': self.proxy, 'http': self.proxy})

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

        async with self.post(url, headers=headers, json=json_data) as resp:
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
