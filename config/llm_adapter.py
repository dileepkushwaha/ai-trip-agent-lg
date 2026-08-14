"""
LLM Adapter for multi-provider support.
Provides a unified interface for different LLM providers.
"""

import logging
from typing import Any, Optional, List, Dict
import requests


from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatOllama
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from pydantic import Field

from config import Settings

logger = logging.getLogger(__name__)


class AbacusAIChatModel(BaseChatModel):
    """Custom LangChain wrapper for Abacus AI API."""
    
    api_key: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 120
    
    @property
    def _llm_type(self) -> str:
        return "abacusai"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate response from Abacus AI."""
        try:
            # Convert LangChain messages to Abacus AI format
            formatted_messages = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    formatted_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    formatted_messages.append({"role": "assistant", "content": msg.content})
                elif isinstance(msg, SystemMessage):
                    formatted_messages.append({"role": "system", "content": msg.content})
            
            # Call Abacus AI Chat LLM API
            url = "https://api.abacus.ai/api/v0/chatLLM"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": formatted_messages,
                "llmName": self.model,
                "temperature": self.temperature,
                "maxTokens": self.max_tokens,
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the response content
            if "content" in result:
                content = result["content"]
            elif "response" in result:
                content = result["response"]
            elif "message" in result:
                content = result["message"]
            else:
                # Fallback: try to get any text response
                content = str(result)
            
            message = AIMessage(content=content)
            generation = ChatGeneration(message=message)
            
            return ChatResult(generations=[generation])
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Abacus AI API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Abacus AI generation failed: {e}")
            raise

class LLMAdapter:
    """Adapter for multiple LLM providers with unified interface."""
    
    def __init__(self, settings: Settings):
        """Initialize LLM adapter with settings."""
        self.settings = settings
        self._llm: Optional[BaseChatModel] = None
    
    def get_llm(self) -> BaseChatModel:
        """Get LLM instance based on configured provider."""
        if self._llm is not None:
            return self._llm
        
        llm_config = self.settings.get_llm_config()
        provider = llm_config["provider"]
        
        logger.info(f"Initializing LLM provider: {provider}")
        
        try:
            if provider == "lmstudio":
                self._llm = self._create_lmstudio_llm(llm_config)
            elif provider == "openai":
                self._llm = self._create_openai_llm(llm_config)
            elif provider == "anthropic":
                self._llm = self._create_anthropic_llm(llm_config)
            elif provider == "azure":
                self._llm = self._create_azure_llm(llm_config)
            elif provider == "ollama":
                self._llm = self._create_ollama_llm(llm_config)
            elif provider == "abacusai":
                self._llm = self._create_abacusai_llm(llm_config)
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
            
            logger.info(f"Successfully initialized {provider} LLM")
            return self._llm
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM provider {provider}: {e}")
            raise
    
    def _create_lmstudio_llm(self, config: dict) -> BaseChatModel:
        """Create LM Studio LLM instance (OpenAI-compatible)."""
        return ChatOpenAI(
            base_url=config["base_url"],
            api_key="lm-studio",  # LM Studio doesn't require real API key
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            timeout=self.settings.llm_timeout,
        )
    
    def _create_openai_llm(self, config: dict) -> BaseChatModel:
        """Create OpenAI LLM instance."""
        kwargs = {
            "model": config["model"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"],
            "timeout": self.settings.llm_timeout,
        }
        
        if config.get("api_key"):
            kwargs["api_key"] = config["api_key"]
        
        if config.get("base_url"):
            kwargs["base_url"] = config["base_url"]
        
        return ChatOpenAI(**kwargs)
    
    def _create_anthropic_llm(self, config: dict) -> BaseChatModel:
        """Create Anthropic (Claude) LLM instance."""
        return ChatAnthropic(
            api_key=config["api_key"],
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            timeout=self.settings.llm_timeout,
        )
    
    def _create_azure_llm(self, config: dict) -> BaseChatModel:
        """Create Azure OpenAI LLM instance."""
        return AzureChatOpenAI(
            api_key=config["api_key"],
            azure_endpoint=config["endpoint"],
            deployment_name=config["deployment"],
            api_version=config["api_version"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            timeout=self.settings.llm_timeout,
        )
    
    def _create_ollama_llm(self, config: dict) -> BaseChatModel:
        """Create Ollama LLM instance."""
        return ChatOllama(
            base_url=config["base_url"],
            model=config["model"],
            temperature=config["temperature"],
        )

    def _create_abacusai_llm(self, config: dict) -> BaseChatModel:
        """Create Abacus AI LLM instance (OpenAI-compatible API)."""
        return ChatOpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"],
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            timeout=self.settings.llm_timeout,
        )
    
    def reset(self):
        """Reset LLM instance (useful for testing or switching providers)."""
        self._llm = None
        logger.info("LLM instance reset")
