from typing import Dict, Any, List, Callable

class PluginHost:
    def __init__(self):
        self.plugins: Dict[int, Callable[[int, List[Any]], Any]] = {}
    def register(self, plugin_id: int, callback: Callable[[int, List[Any]], Any]) -> None:
        self.plugins[plugin_id] = callback
    def call(self, plugin_id: int, cmd_id: int, args: List[Any]) -> Any:
        if plugin_id not in self.plugins: raise RuntimeError(f"Plugin loaded failure: ID {plugin_id}")
        return self.plugins[plugin_id](cmd_id, args)
