#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.12"
# dependencies = ["numpy", "plotly", "scipy", "tqdm", "pandas", "kaleido"]
# ///

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dataclasses import dataclass
from typing import Callable, Optional, Union
from scipy import stats
from scipy.stats.distributions import t
from tqdm import tqdm
import numpy as np


@dataclass
class PIRProduct:
    mu: float
    sigma: float


@dataclass
class SimulationResult:
    product: PIRProduct
    strat1_over: int
    strat2_over: int
    strat1_win: int
    strat2_win: int
    n: int


type PIRStrategy = Union[Callable[[PIRProduct], float], float, np.ndarray]


def simulate(product: PIRProduct, strat1: PIRStrategy, strat2: PIRStrategy, n=100_000):
    true_price = np.maximum(np.random.normal(product.mu, product.sigma, n), np.zeros(n))
    if isinstance(strat1, (int, float)):
        strat1_guess = np.full(n, strat1)
    elif isinstance(strat1, np.ndarray):
        strat1_guess = strat1
    else:
        strat1_guess = np.array([strat1(product) for _ in range(n)])

    if isinstance(strat2, (int, float)):
        strat2_guess = np.full(n, strat2)
    elif isinstance(strat2, np.ndarray):
        strat2_guess = strat2
    else:
        strat2_guess = np.array([strat2(product) for _ in range(n)])

    strat1_over = (strat1_guess > true_price).sum()
    strat2_over = (strat2_guess > true_price).sum()
    # Win if guess is lower than true price, and opponent
    # either goes over or is less than guess
    strat1_win = (
        (strat1_guess <= true_price)
        & ((strat2_guess > true_price) | (strat1_guess > strat2_guess))
    ).sum()
    strat2_win = (
        (strat2_guess <= true_price)
        & ((strat1_guess > true_price) | (strat2_guess > strat1_guess))
    ).sum()

    return SimulationResult(
        product=product,
        strat1_over=strat1_over,
        strat2_over=strat2_over,
        strat1_win=strat1_win,
        strat2_win=strat2_win,
        n=n,
    )


def plot_results(
    results: SimulationResult,
    strat1_name: Optional[str] = "Strategy 1",
    strat2_name: Optional[str] = "Strategy 2",
):
    if strat1_name is None:
        strat1_name = "Strategy 1"
    if strat2_name is None:
        strat2_name = "Strategy 2"

    # Calculate key metrics
    strat1_win_rate = results.strat1_win / results.n * 100
    strat2_win_rate = results.strat2_win / results.n * 100
    strat1_over_rate = results.strat1_over / results.n * 100
    strat2_over_rate = results.strat2_over / results.n * 100
    both_over = results.n - results.strat1_win - results.strat2_win

    # Create simple 2x2 subplot
    fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=[
            "Win Rates",
            "Risk (Going Over)",
            "Price Distribution",
            "Game Outcomes",
        ],
        vertical_spacing=0.2,
        horizontal_spacing=0.15,
    )

    # Panel 1: Win rates comparison
    fig.add_trace(
        go.Bar(
            x=[strat1_name, strat2_name],
            y=[strat1_win_rate, strat2_win_rate],
            marker_color=["#FF6B6B", "#4ECDC4"],
            text=[f"{strat1_win_rate:.1f}%", f"{strat2_win_rate:.1f}%"],
            textposition="auto",
            name="Win Rate",
        ),
        row=1,
        col=1,
    )

    # Panel 2: Risk comparison
    fig.add_trace(
        go.Bar(
            x=[strat1_name, strat2_name],
            y=[strat1_over_rate, strat2_over_rate],
            marker_color=["#FF6B6B", "#4ECDC4"],
            text=[f"{strat1_over_rate:.1f}%", f"{strat2_over_rate:.1f}%"],
            textposition="auto",
            name="Over Rate",
        ),
        row=1,
        col=2,
    )

    # Panel 3: Price distribution
    x_range = np.linspace(
        results.product.mu - 3 * results.product.sigma,
        results.product.mu + 3 * results.product.sigma,
        300,
    )
    pdf_values = stats.norm.pdf(x_range, results.product.mu, results.product.sigma)

    fig.add_trace(
        go.Scatter(
            x=x_range,
            y=pdf_values,
            fill="tozeroy",
            name="Price Distribution",
            line=dict(color="gray", width=2),
            fillcolor="rgba(128,128,128,0.3)",
        ),
        row=2,
        col=1,
    )

    # Add strategy lines
    fig.add_vline(
        x=results.product.mu, line_dash="dash", line_color="red", row=2, col=1
    )
    fig.add_vline(
        x=results.product.mu - 0.1 * results.product.sigma,
        line_dash="dash",
        line_color="blue",
        row=2,
        col=1,
    )

    # Panel 4: Outcomes
    outcomes = [f"{strat1_name} Wins", f"{strat2_name} Wins", "Both Over"]
    values = [results.strat1_win, results.strat2_win, both_over]

    fig.add_trace(
        go.Bar(
            x=outcomes,
            y=values,
            marker_color=["#FF6B6B", "#4ECDC4", "#95A5A6"],
            text=[f"{v:,}" for v in values],
            textposition="auto",
            name="Outcomes",
        ),
        row=2,
        col=2,
    )

    # Update layout
    fig.update_layout(
        title={
            "text": f"Price Is Right Strategy Analysis<br><sub>{results.n:,} simulations</sub>",
            "x": 0.5,
            "font": {"size": 20},
        },
        showlegend=False,
        height=700,
        font=dict(size=11),
    )

    # Update axes
    fig.update_yaxes(title_text="Win Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Over Rate (%)", row=1, col=2)
    fig.update_xaxes(title_text="Price ($)", row=2, col=1)
    fig.update_yaxes(title_text="Density", row=2, col=1)
    fig.update_yaxes(title_text="Count", row=2, col=2)

    fig.show()


def guess_mean(product: PIRProduct):
    return product.mu


def guess_percentile(percentile: float, product: PIRProduct) -> float:
    res = stats.norm.ppf(percentile / 100, product.mu, product.sigma)
    return float(res)


def guess_random(product: PIRProduct):
    return np.random.normal(product.mu, product.sigma)


def compare_to_mean():
    compare = []
    percentiles = np.linspace(0, 100, 1000)
    print("comparing...")
    for percentile in tqdm(percentiles):
        sim = simulate(
            television,
            guess_mean(television),
            guess_percentile(percentile, television),
            n=100_000,
        )
        compare.append((sim.strat1_win, sim.strat2_win))
    print("done!")

    # Graph strat2 win rate vs multiple
    compare = np.array(compare)
    strat1_wins = compare[:, 0]
    strat2_wins = compare[:, 1]
    strat2_win_rate = strat2_wins / (strat1_wins + strat2_wins) * 100
    fig = px.line(
        x=percentiles,
        y=strat2_win_rate,
        labels={
            "x": "Percentile",
            "y": "Percentile Win Rate (%)",
        },
        title="Median vs. Other Percentiles Win Rate (n=100,000)",
    )
    fig.add_hline(y=50, line_dash="dash", line_color="red")
    fig.update_layout(yaxis_range=[0, 100])
    fig.show()


def compare_all_percentiles(product):
    results = np.zeros((100, 100))
    for i, q1 in enumerate(np.linspace(0, 100, 100)):
        for j, q2 in enumerate(np.linspace(0, 100, 100)):
            if q1 >= q2:
                continue
            sim = simulate(
                television,
                guess_percentile(q1, product),
                guess_percentile(q2, product),
                n=100_000,
            )

            results[i, j] = sim.strat2_win / (sim.strat1_win + sim.strat2_win) * 100
            results[j, i] = 100 - results[i, j]

    net_win_rates = results.mean(axis=1)
    print(net_win_rates)
    print(
        "Best percentile",
        np.linspace(0, 100, 100)[np.argmax(net_win_rates)],
        "with win rate",
        np.max(net_win_rates),
    )

    fig = px.imshow(
        results,
        labels={
            "x": "Strategy 2 Percentile",
            "y": "Strategy 1 Percentile",
            "color": "Win Rate (%)",
        },
        x=np.linspace(0, 100, 100),
        y=np.linspace(0, 100, 100),
        title="Percentile vs. Percentile Win Rate (n=100,000)",
        color_continuous_scale="RdBu",
        zmin=0,
        zmax=100,
    )
    fig.add_shape(
        type="line",
        x0=0,
        y0=0,
        x1=100,
        y1=100,
        line=dict(color="black", dash="dash"),
    )
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )
    fig.show()
    # save fig
    fig.write_image("percentile_vs_percentile.png", scale=3)


def sample_g(n_samples: int):
    # Draw uniform(0,1) samples
    u = np.random.rand(n_samples)
    # Inverse CDF transform
    q = 1 - np.exp(-u)
    # Enforce support explicitly
    q = np.minimum(q, 1 - np.exp(-1))
    return q


def compare_g_to_percentiles(product: PIRProduct):
    n_samples = 100_000
    # Generate original samples
    g_sample_quantiles = sample_g(n_samples)
    g_sample_bids = stats.norm.ppf(g_sample_quantiles, product.mu, product.sigma)

    percentiles = np.arange(1, 100)
    results = []
    for p in tqdm(percentiles):
        sim = simulate(
            product, g_sample_bids, guess_percentile(p, product), n=n_samples
        )
        results.append((p, sim.strat1_win / sim.n * 100, sim.strat2_win / sim.n * 100))

    results = np.array(results)
    fig = px.line(
        x=results[:, 0],
        y=[results[:, 1], results[:, 2]],
        labels={"x": "Percentile", "value": "Win Rate (%)", "variable": "Strategy"},
        title="Mixed Strategy vs. Percentile Win Rate (n=100,000)",
    )
    fig.data[0].name = "Mixed Strategy"
    fig.data[1].name = "Fixed Percentile Strategy"
    fig.update_layout(yaxis_range=[0, 100], legend_title_text="")
    fig.show()
    # save
    fig.write_image("g_vs_percentile.svg", scale=3)


def draw_optimal():
    # Define grid for plotting
    q_grid = np.linspace(0, 1, 500)

    # Define true PDF with support restriction
    pdf = np.zeros_like(q_grid)
    support_end = 1 - np.exp(-1)
    mask = (q_grid >= 0) & (q_grid < support_end)
    pdf[mask] = 1 / (1 - q_grid[mask])
    # Create plotly figure
    fig = go.Figure()

    # Add filled PDF trace
    fig.add_trace(
        go.Scatter(
            x=q_grid,
            y=pdf,
            mode="lines",
            line=dict(color="blue", width=2),
            fill="tozeroy",
            fillcolor="rgba(0, 0, 255, 0.3)",  # Light blue fill
            name="True PDF",
        )
    )

    # Update layout with axis labels and title
    fig.update_layout(
        xaxis_title="q",
        yaxis_title="Density",
        title="Mixed Strategy Distribution",
        xaxis=dict(range=[0, 1]),
        yaxis=dict(rangemode="nonnegative"),  # Sets minimum to 0, maximum auto
    )

    # Display figure
    fig.show()

    # Save figure
    fig.write_image("optimal_strategy.svg", scale=3)


if __name__ == "__main__":
    television = PIRProduct(mu=550, sigma=300)

    # simulation = simulate(television, guess_mean, guess_percentile(51, television))
    # plot_results(simulation, "Guess Mean", "Guess 51st Percentile")

    # compare_all_percentiles(television)

    draw_optimal()
    compare_g_to_percentiles(television)
