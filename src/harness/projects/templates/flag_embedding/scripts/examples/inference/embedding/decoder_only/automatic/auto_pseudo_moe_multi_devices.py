"""Run the pseudo moe embedding example with the published preset."""

if __package__:
    from ..demos.embedding import show_pseudo_moe
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from demos.embedding import show_pseudo_moe


def test_auto_pseudo_moe_multi_devices():
    show_pseudo_moe(['cuda:0', 'cuda:1'], automatic=True, domain='coding', batch_repeats=100)


if __name__ == "__main__":
    test_auto_pseudo_moe_multi_devices()

    print("--------------------------------")
    print("Expected Output:")
    print("[[0.700  0.246]\n [0.158 0.654]]")
