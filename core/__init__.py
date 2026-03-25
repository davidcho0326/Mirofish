"""
FnF Marketing Simulator — Core Engine (forked from MiroFish)
Lazy imports for modules that depend on optional packages (camel-oasis).
"""

# ── Always available (no OASIS dependency) ──
from .ontology_generator import OntologyGenerator
from .graph_builder import GraphBuilderService
from .text_processor import TextProcessor
from .zep_entity_reader import ZepEntityReader, EntityNode, FilteredEntities
from .oasis_profile_generator import OasisProfileGenerator, OasisAgentProfile
from .simulation_config_generator import (
    SimulationConfigGenerator,
    SimulationParameters,
    AgentActivityConfig,
    TimeSimulationConfig,
    EventConfig,
    PlatformConfig,
)

# ── OASIS-dependent modules (lazy import) ──
# These require camel-oasis which needs Python <3.12
# Import them explicitly when needed:
#   from core.simulation_runner import SimulationRunner
#   from core.simulation_manager import SimulationManager

__all__ = [
    'OntologyGenerator',
    'GraphBuilderService',
    'TextProcessor',
    'ZepEntityReader', 'EntityNode', 'FilteredEntities',
    'OasisProfileGenerator', 'OasisAgentProfile',
    'SimulationConfigGenerator', 'SimulationParameters',
    'AgentActivityConfig', 'TimeSimulationConfig',
    'EventConfig', 'PlatformConfig',
]
