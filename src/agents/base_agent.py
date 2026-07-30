from abc import ABC, abstractmethod
from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv

from src.utils.types import AgentResponse
from src.data.dataset_handle import DatasetHandle
from src.utils.token_tracker import TokenTracker

load_dotenv()


class BaseAgent(ABC):
    """Base class for all EDA agents"""

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.1):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        TokenTracker.initialize()

    @abstractmethod
    def get_agent_name(self) -> str:
        """Return the agent's name"""
        pass

    @abstractmethod
    def analyze(self, dataset_handle: DatasetHandle, context: Dict[str, Any] = None) -> AgentResponse:
        """
        Perform analysis and return structured response

        Args:
            dataset_handle: DatasetHandle instance
            context: Additional context from previous steps

        Returns:
            AgentResponse with result, reasoning, impact, recommendations, confidence
        """
        pass

    def create_structured_prompt(self, system_message: str, user_message: str) -> ChatPromptTemplate:
        """Create a structured prompt template"""
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("user", user_message)
        ])

    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response as JSON"""
        parser = JsonOutputParser()
        try:
            return parser.parse(response)
        except Exception as e:
            # Fallback if parsing fails
            return {
                "error": f"Failed to parse response: {str(e)}",
                "raw_response": response
            }

    def invoke_with_tracking(self, messages, **kwargs):
        """
        Invoke LLM and track token usage

        Args:
            messages: Messages to send to LLM
            **kwargs: Additional arguments for LLM invoke

        Returns:
            LLM response
        """
        response = self.llm.invoke(messages, **kwargs)

        # Extract token usage from response metadata
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            usage = response.response_metadata['token_usage']
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)

            # Track the usage
            TokenTracker.track_usage(
                agent_name=self.get_agent_name(),
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                metadata={
                    'temperature': self.temperature
                }
            )

        return response

    def track_chain_response(self, response):
        """
        Track token usage from a chain response

        Args:
            response: Response from chain.invoke()
        """
        # Extract token usage from response metadata
        if hasattr(response, 'response_metadata') and 'token_usage' in response.response_metadata:
            usage = response.response_metadata['token_usage']
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)

            # Track the usage
            TokenTracker.track_usage(
                agent_name=self.get_agent_name(),
                model_name=self.model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                metadata={
                    'temperature': self.temperature
                }
            )
