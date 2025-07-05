from langchain_core.language_models import BaseLLM
from langchain_core.outputs import Generation, LLMResult
from langchain_core.callbacks.manager import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
import inspect
import asyncio
from functools import partial
import requests
import os
from typing import Union, Optional, Any, List

class MyEnterpriseLLM(BaseLLM):
    """Integração simples com a API corporativa do SerproLLM."""

    def __init__(
        self,
        model: str,
        client_id: str,
        client_secret: str,
        temperature: float = 0.0,
        verify: Union[bool, str, None] = None,
    ):
        super().__init__(model=model, temperature=temperature)
        self.model = model
        self.client_id = client_id
        self.client_secret = client_secret
        self.temperature = temperature
        self.access_token = None
        if verify is None:
            ca_bundle = os.getenv("SERPRO_CA_BUNDLE")
            self.verify = ca_bundle if ca_bundle else True
        else:
            self.verify = verify

    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "my-enterprise"

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompts."""
        generations = []
        new_arg_supported = inspect.signature(self._call).parameters.get("run_manager")
        for prompt in prompts:
            text = (
                self._call(prompt, stop=stop, run_manager=run_manager, **kwargs)
                if new_arg_supported
                else self._call(prompt, stop=stop, **kwargs)
            )
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    async def _agenerate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Asynchronously run the LLM on the given prompts."""
        generations = []
        new_arg_supported = inspect.signature(self._call).parameters.get("run_manager")
        loop = asyncio.get_running_loop()
        for prompt in prompts:
            func = (
                partial(self._call, prompt, stop=stop, run_manager=run_manager, **kwargs)
                if new_arg_supported
                else partial(self._call, prompt, stop=stop, **kwargs)
            )
            text = await loop.run_in_executor(None, func)
            generations.append([Generation(text=text)])
        return LLMResult(generations=generations)

    def _get_access_token(self) -> str:
        response = requests.post(
            "https://e-api-serprollm.ni.estaleiro.serpro.gov.br/oauth2/token",
            data={"grant_type": "client_credentials"},
            auth=(self.client_id, self.client_secret),
            verify=self.verify,
        )
        response.raise_for_status()
        return response.json().get("access_token")

    def _call(self, prompt: str, stop=None) -> str:
        if self.access_token is None:
            self.access_token = self._get_access_token()

        payload = {
            "model": self.model,
            "prompt": [prompt],
            "temperature": self.temperature,
            "max_tokens": 1000,
            "stream": False,
        }

        resp = requests.post(
            "https://api-serprollm.ni.estaleiro.serpro.gov.br/gateway/v1/completions",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            verify=self.verify,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("choices"):
            return data["choices"][0].get("text", "")
        return ""
