"""Run the lightweight reranking example with the published preset."""

if __package__:
    from ..demos.ranking import show_lightweight
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from demos.ranking import show_lightweight


def test_base_multi_devices():
    show_lightweight(['cuda:3'], automatic=False)


if __name__ == '__main__':
    test_base_multi_devices()
    
    print("--------------------------------")
    print("Expected Output:")
    print("[25.375, 8.734375, 9.8359375, 26.15625]")
