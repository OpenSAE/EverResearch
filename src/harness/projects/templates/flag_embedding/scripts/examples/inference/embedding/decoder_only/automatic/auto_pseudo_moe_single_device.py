"""Run the pseudo moe embedding example with the published preset."""

if __package__:
    from ..demos.embedding import show_pseudo_moe
else:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from demos.embedding import show_pseudo_moe


def test_auto_pseudo_moe_single_device():
    show_pseudo_moe('cuda:0', automatic=True, domain='reasoning', batch_repeats=10)


if __name__ == "__main__":
    test_auto_pseudo_moe_single_device()

    print("--------------------------------")
    print("Expected Output:")
    print("[[0.844 0.466 ]\n [0.395 0.684 ]]")
