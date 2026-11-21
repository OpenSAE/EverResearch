"""Run the icl embedding example with the published preset."""

if __package__:
    from ..demos.embedding import show_icl
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from demos.embedding import show_icl


def test_icl_multi_devices():
    show_icl(['cuda:0', 'cuda:1'], automatic=False)


if __name__ == '__main__':
    test_icl_multi_devices()

    print("--------------------------------")
    print("Expected Output:")
    print("[[0.579  0.2776]\n [0.2249 0.5146]]")
