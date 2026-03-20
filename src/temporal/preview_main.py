from temporal.app import run_with_bridge
from temporal.preview_bridge import PreviewBridge


def main() -> int:
    return run_with_bridge(PreviewBridge())


if __name__ == "__main__":
    raise SystemExit(main())
