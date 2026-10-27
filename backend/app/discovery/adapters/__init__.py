from typing import Dict, Type
from backend.app.discovery.adapters.base import BaseDiscoveryAdapter, EventCandidate
from backend.app.discovery.adapters.devpost import DevpostAdapter
from backend.app.discovery.adapters.devfolio import DevfolioAdapter
from backend.app.discovery.adapters.unstop import UnstopAdapter
from backend.app.discovery.adapters.foss_united import FOSSUnitedAdapter
from backend.app.discovery.adapters.tech_conferences import TechConferencesAdapter
from backend.app.discovery.adapters.gdg import GDGAdapter
from backend.app.discovery.adapters.cybersecurity import CybersecurityAdapter

ADAPTER_REGISTRY: Dict[str, Type[BaseDiscoveryAdapter]] = {
    "devpost": DevpostAdapter,
    "devfolio": DevfolioAdapter,
    "unstop": UnstopAdapter,
    "foss-united": FOSSUnitedAdapter,
    "tech-conferences": TechConferencesAdapter,
    "gdg-india": GDGAdapter,
    "cybersecurity-events": CybersecurityAdapter
}

def get_adapter_for_source(slug: str) -> BaseDiscoveryAdapter:
    adapter_cls = ADAPTER_REGISTRY.get(slug)
    if adapter_cls:
        return adapter_cls()
    raise ValueError(f"No adapter registered for source slug '{slug}'")

def get_all_adapters():
    return [cls() for cls in ADAPTER_REGISTRY.values()]
