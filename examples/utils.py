import matplotlib.pyplot as plt

def plot_active_difficulty_histogram(result, bins: int = 10) -> None:
    difficulties = [
        candidate.difficulty.score
        for candidate in result.active_candidates
        if candidate.difficulty is not None
    ]

    if not difficulties:
        raise ValueError(
            "No difficulty reports found for active candidates. "
            "Did you run validation and difficulty assessment?"
        )

    plt.figure(figsize=(8, 5))
    plt.hist(difficulties, bins=bins, edgecolor="black")

    plt.title("Difficulty Distribution of Valid Generated Candidates")
    plt.xlabel("Difficulty score")
    plt.ylabel("Number of candidates")

    plt.xlim(0.0, 1.0)
    plt.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.show()