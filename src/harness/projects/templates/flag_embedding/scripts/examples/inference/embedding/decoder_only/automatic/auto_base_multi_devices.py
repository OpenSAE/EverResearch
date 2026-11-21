"""Run the base embedding example with the published preset."""

if __package__:
    from ..demos.embedding import show_base
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from demos.embedding import show_base


def test_base_multi_devices():
    show_base(['cuda:0', 'cuda:1'], automatic=True)


if __name__ == '__main__':
    test_base_multi_devices()

    print("--------------------------------")
    print("Expected Output:")
    print("[[0.558   0.02113 ]\n [0.01643 0.526  ]]")
