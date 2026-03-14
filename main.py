import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("output_plots", exist_ok=True)
payoff_matrix = {('C', 'C'): (3, 3),('C', 'D'): (0, 5),('D', 'C'): (5, 0),('D', 'D'): (1, 1)}
def always_cooperate(history_self, history_opponent):
    return 'C'
def always_defect(history_self, history_opponent):
    return 'D'
def tit_for_tat(history_self, history_opponent):
    if len(history_opponent) == 0:
        return 'C'
    return history_opponent[-1]
def grim_trigger(history_self, history_opponent):
    if 'D' in history_opponent:
        return 'D'
    return 'C'
def win_stay_lose_shift(history_self, history_opponent):
    """Cooperate first; then repeat last move if payoff was good, else switch."""
    if len(history_self) == 0:
        return 'C'
    last_move = history_self[-1]
    last_opp  = history_opponent[-1]
    payoff, _ = payoff_matrix[(last_move, last_opp)]
    if payoff >= 3:
        return last_move
    else:
        return 'D' if last_move == 'C' else 'C'
strategies = {
    "TitForTat":tit_for_tat,
    "GrimTrigger":grim_trigger,
    "AlwaysDefect":always_defect,
    "AlwaysCooperate":always_cooperate,
    "WinStayLoseShift":win_stay_lose_shift,
}

def play_game(strategy1, strategy2, rounds=200, noise=0.0):
    history1, history2 = [], []
    score1, score2 = 0, 0
    records = []
    for r in range(rounds):
        move1 = strategy1(history1, history2)
        move2 = strategy2(history2, history1)
        if noise > 0:
            if np.random.rand() < noise:
                move1 = 'D' if move1 == 'C' else 'C'
            if np.random.rand() < noise:
                move2 = 'D' if move2 == 'C' else 'C'
        history1.append(move1)
        history2.append(move2)
        p1, p2 = payoff_matrix[(move1, move2)]
        score1 += p1
        score2 += p2
        records.append({
            "Round": r + 1,
            "Player1": move1,
            "Player2": move2,
            "Payoff1": p1,
            "Payoff2": p2
        })
    df = pd.DataFrame(records)
    return score1, score2, df

print(f"Strategies: {list(strategies.keys())}")
print(f"Rounds per match: 200\n")

names = list(strategies.keys())
results = pd.DataFrame(0, index=names, columns=names, dtype=float)

for s1_name, s1 in strategies.items():
    for s2_name, s2 in strategies.items():
        score1, score2, _ = play_game(s1, s2)
        results.loc[s1_name, s2_name] = score1
print("Tournament Payoff Table:")
print(results.to_string())

total_scores = results.sum(axis=1).sort_values(ascending=False)
print("\n Strategy Rankings (Total Payoff):")
for rank, (name, score) in enumerate(total_scores.items(), 1):
    print(f"   {rank}. {name}: {score:.0f}")

plt.figure(figsize=(9, 5))
bars = plt.bar(total_scores.index, total_scores.values,color=['steelblue', 'mediumseagreen', 'coral', 'gold', 'mediumpurple'])
plt.title("Strategy Performance – Iterated Prisoner's Dilemma", fontsize=13)
plt.ylabel("Total Payoff Across All Matches")
plt.xlabel("Strategy")
for bar, val in zip(bars, total_scores.values):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,f"{val:.0f}", ha='center', fontsize=10)
plt.tight_layout()
plt.savefig("output_plots/1_strategy_performance.png", dpi=150)
plt.close()

plt.figure(figsize=(7, 5))
import matplotlib.colors as mcolors
im = plt.imshow(results.values, cmap='YlGn')
plt.colorbar(im, label="Payoff")
plt.xticks(range(len(names)), names, rotation=30, ha='right', fontsize=9)
plt.yticks(range(len(names)), names, fontsize=9)
for i in range(len(names)):
    for j in range(len(names)):
        plt.text(j, i, f"{results.values[i,j]:.0f}", ha='center', va='center', fontsize=9)
plt.title("Payoff Heatmap (Row vs Column)")
plt.tight_layout()
plt.savefig("output_plots/2_payoff_heatmap.png", dpi=150)
plt.close()

_, _, df_tft = play_game(tit_for_tat, always_defect, rounds=200)
_, _, df_coop = play_game(tit_for_tat, tit_for_tat, rounds=200)

plt.figure(figsize=(10, 4))
plt.plot(df_tft["Payoff1"].cumsum(), label="TitForTat vs AlwaysDefect", color='coral')
plt.plot(df_coop["Payoff1"].cumsum(), label="TitForTat vs TitForTat", color='steelblue')
plt.title("Cumulative Payoff Over 200 Rounds")
plt.xlabel("Round")
plt.ylabel("Cumulative Payoff")
plt.legend()
plt.tight_layout()
plt.savefig("output_plots/3_cumulative_payoff.png", dpi=150)
plt.close()

print("\nCooperation Rates (vs all opponents):")
coop_rates = {}
for s1_name, s1 in strategies.items():
    rates = []
    for s2_name, s2 in strategies.items():
        _, _, df = play_game(s1, s2, rounds=200)
        rates.append((df["Player1"] == 'C').mean())
    coop_rates[s1_name] = np.mean(rates)
    print(f" {s1_name}: {coop_rates[s1_name]*100:.1f}%")

plt.figure(figsize=(9, 4))
plt.bar(coop_rates.keys(), [v * 100 for v in coop_rates.values()],
        color='steelblue', edgecolor='black', alpha=0.8)
plt.title("Average Cooperation Rate by Strategy")
plt.ylabel("Cooperation Rate (%)")
plt.xlabel("Strategy")
plt.ylim(0, 110)
for i, (k, v) in enumerate(coop_rates.items()):
    plt.text(i, v * 100 + 2, f"{v*100:.0f}%", ha='center', fontsize=10)
plt.tight_layout()
plt.savefig("output_plots/4_cooperation_rates.png", dpi=150)
plt.close()

noise_levels = [0.0, 0.01, 0.05, 0.10, 0.20]
tft_scores_vs_noise = []
for noise in noise_levels:
    scores = []
    for _ in range(200):
        s, _, _ = play_game(tit_for_tat, tit_for_tat, rounds=100, noise=noise)
        scores.append(s)
    tft_scores_vs_noise.append(np.mean(scores))

plt.figure(figsize=(8, 4))
plt.plot([n*100 for n in noise_levels], tft_scores_vs_noise, marker='o', color='steelblue')
plt.title("TitForTat Robustness Under Noise (vs TitForTat)")
plt.xlabel("Noise Level (%)")
plt.ylabel("Average Payoff per Game")
plt.tight_layout()
plt.savefig("output_plots/5_noise_robustness.png", dpi=150)
plt.close()
