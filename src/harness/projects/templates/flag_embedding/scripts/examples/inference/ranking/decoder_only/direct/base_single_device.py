"""Run the base reranking example with the published preset."""

if __package__:
    from ..demos.ranking import show_base
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from demos.ranking import show_base


def test_base_multi_devices():
    show_base(['cuda:3'], automatic=False)


if __name__ == '__main__':
    test_base_multi_devices()
    
    print("--------------------------------")
    print("Expected Output:")
    print("[9.171875, -4.49609375, -5.5234375, 10.2109375]")
