import os
import json
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    try:
        from langchain_community.chat_models import ChatOpenAI
    except ImportError:
        try:
            from langchain.chat_models import ChatOpenAI
        except ImportError:
            ChatOpenAI = None


def get_llm(temperature: float = 0.2, max_tokens: Optional[int] = None, streaming: bool = False):
    """Factory function to retrieve LLM instance based on configuration.
    
    Guarantees zero hardcoded credentials, endpoints, or model defaults in the source code.
    """
    # Dynamically disable SSL verification for enterprise proxy certificates if configured
    verify_ssl = os.getenv("LITELLM_VERIFY_SSL", "true").lower().strip() != "false"
    if not verify_ssl:
        try:
            import httpx
            if not getattr(httpx.Client, "_ssl_patched", False):
                orig_client_init = httpx.Client.__init__
                httpx.Client.__init__ = lambda self, *args, **kwargs: orig_client_init(self, *args, **dict(kwargs, verify=False))
                orig_async_init = httpx.AsyncClient.__init__
                httpx.AsyncClient.__init__ = lambda self, *args, **kwargs: orig_async_init(self, *args, **dict(kwargs, verify=False))
                httpx.Client._ssl_patched = True
        except Exception:
            pass

    provider = os.getenv("LLM_PROVIDER", "").lower().strip()
    
    # Parse custom headers dynamically from JSON env configuration
    extra_headers = {}
    litellm_headers_env = os.getenv("LITELLM_HEADERS")
    if litellm_headers_env:
        try:
            extra_headers.update(json.loads(litellm_headers_env))
        except Exception:
            pass
            
    # Dynamically inject enterprise project / client identifiers from env
    project_id = os.getenv("LITELLM_PROJECT_ID")
    if project_id:
        extra_headers["X-Project-Id"] = project_id
        
    client_id = os.getenv("LITELLM_CLIENT_ID")
    if client_id:
        extra_headers["client-id"] = client_id

    if provider == "litellm":
        api_key = os.getenv("LITELLM_API_KEY")
        api_base = os.getenv("LITELLM_API_BASE")
        model_name = os.getenv("LITELLM_MODEL")
        
        # Verify mandatory parameters are set in environment
        if not api_key or not api_base or not model_name:
            # Resiliency fallback to Gemini if keys are available
            gemini_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            gemini_model = os.getenv("GEMINI_MODEL")
            if gemini_key and gemini_model:
                print("[LLM Factory] LITELLM configuration incomplete. Falling back to Gemini.")
                provider = "gemini"
            else:
                return None
        else:
            return ChatOpenAI(
                model=model_name,
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=temperature,
                max_tokens=max_tokens,
                streaming=streaming,
                default_headers=extra_headers if extra_headers else None
            )

    if provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        model_name = os.getenv("GEMINI_MODEL")
        
        if not api_key or not model_name:
            return None
            
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=temperature,
            max_output_tokens=max_tokens,
            streaming=streaming
        )
        
    return None
