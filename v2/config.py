from pathlib import Path

GENERATED_ROOT = Path("generated")
CONTEXT_DIR = GENERATED_ROOT / "context"
CACHE_ROOT = Path("cache") / "received"
SENT_ROOT = Path("cache") / "sent"

AGENTS = {
    "orchestrator_agent": "prompts/orchestrator_agent.yml",
    "springboot_agent": "prompts/springboot_agent.yml",
    "spring_controller_agent": "prompts/spring_controller_agent.yml",
    "spring_service_agent": "prompts/spring_service_agent.yml",
    "spring_repository_agent": "prompts/spring_repository_agent.yml",

}

PROMPT_VERSION = "0.0.1"
