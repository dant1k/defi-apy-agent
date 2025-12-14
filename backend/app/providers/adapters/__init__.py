"""DEX adapters for parsing swap events"""
from app.providers.adapters.base_adapter import DexAdapter
from app.providers.adapters.pancake_aptos_adapter import PancakeAptosAdapter
from app.providers.adapters.aux_aptos_adapter import AuxAptosAdapter
from app.providers.adapters.hyperion_aptos_adapter import HyperionAptosAdapter

# Registry of adapters by DEX slug
ADAPTER_REGISTRY: dict[str, DexAdapter] = {
    "pancakeswap-amm": PancakeAptosAdapter(),
    "aux-exchange": AuxAptosAdapter(),
    "hyperion": HyperionAptosAdapter(),
    # Add more adapters as needed
}

def get_adapter(dex_slug: str) -> DexAdapter | None:
    """Get adapter for a DEX slug"""
    return ADAPTER_REGISTRY.get(dex_slug)

__all__ = [
    "DexAdapter",
    "PancakeAptosAdapter",
    "AuxAptosAdapter",
    "HyperionAptosAdapter",
    "get_adapter",
    "ADAPTER_REGISTRY",
]

