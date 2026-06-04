import time
from dataclasses import dataclass, field


@dataclass
class ConsumerState:
    name: str
    last_heartbeat: float = field(default_factory=time.time)
    thread_alive: bool = False

    def heartbeat(self) -> None:
        self.last_heartbeat = time.time()
        self.thread_alive = True

    def is_healthy(self, max_stale_seconds: float = 10.0) -> bool:
        if not self.thread_alive:
            return False
        return (time.time() - self.last_heartbeat) <= max_stale_seconds
