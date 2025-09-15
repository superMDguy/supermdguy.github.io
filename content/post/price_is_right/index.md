---
title: "Is the Price Right?"
date: 2025-09-10T22:54:53-06:00
math: true
---

In the game show "The Price is Right", contestants try to guess the price of a prize without going over. Assume you're a contestant, and you somehow know the exact distribution of prices for the prize. Would you be able to win?

## Pure Strategy Equilibrium

Let $V \sim \mathcal{D}$ be a random variable representing the true value of the prize, with CDF $F(v)$, supported on $(0, \infty)$ (we assume $F$ is strictly increasing and the corresponding PDF is continuous for simplicity). Suppose we're playing with two contestants, who simultaneously makes guesses $x_1, x_2 \in (0, \infty)$. They receive a reward of 1 if they are closest to the randomly selected price $v$ without going over, and 0 otherwise (we'll ignore ties throughout the analysis). This leads to symmetric (expected) payoff functions

$$
f_1(x_1, x_2) = \begin{cases}
1 - F(x_1) &  x_1 > x_2 \\\\
F(x_2) - F(x_1) & x_1 < x_2 \\\\
\end{cases}
$$

and

$$
f_2(x_1, x_2) = \begin{cases}
F(x_1) - F(x_2) &  x_1 > x_2 \\\\
1 - F(x_2) &  x_1 < x_2 \\\\
\end{cases}
$$

Let's analyze the [best response](https://en.wikipedia.org/wiki/Best_response) [function](https://math.stackexchange.com/questions/293404/finding-mixed-nash-equilibria-in-continuous-games) for each contestant. This is a concept from game theory that finds the optimal choice for one player, given what the other player has chosen. When an action is a mutual best response, neither player would be choose to play differently, given what the other player has played. This leads to [Nash Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium). So finding the best response for each player is the first step to determining if an equilibrium solution is possible.

We seek to prove that there's no best response to any opponent moves. For any proposed best response to Player 2's choice, we can always find a Player 1 choice that's better. If the proposed best response is above Player 2's, you'd do better if you dropped your guess so it's just a little bit higher than Player 2, to minimize your risk of going over while still ensuring you're closer to the true price than Player 2. On the other hand, if the proposed best response is below Player 2's, then you'd do better dropping your guess even further to more fully capitalize on the times when Player 2 goes over.

<div id="price-viz">
<style>
    #price-viz { border: 1px solid #ccc; padding: 20px; border-radius: 10px; max-width:900px; }
    .controls-container { margin: 12px 0; display:flex; align-items:center; gap:10px; }
    .value { min-width:48px; text-align:right; font-variant-numeric: tabular-nums; }
    .toggle-buttons { display: flex; gap: 5px; }
    .toggle-btn {
        padding: 2px 4px;
        border: 1px solid #ccc;
        background: white;
        cursor: pointer;
        border-radius: 3px;
        font-size: 12px;
        color: #333;
    }
    .toggle-btn.active {
        background: #4a90e2;
        border-color: #357abd;
        color: white;
    }
    #plot { width:100%; height:400px; }
</style>

<div id="plot"></div>

<div class="controls-container">
    <label>x₁:</label>
    <input type="range" id="slider-x1" min="0" max="10" step="0.1" value="2" />
    <div class="value" id="label-x1">2.00</div>
    <div style="flex-grow: 1;"></div>
    <div class="toggle-buttons">
        <button class="toggle-btn" id="btn-low" data-value="low">Low x₂</button>
        <button class="toggle-btn active" id="btn-high" data-value="high">High x₂</button>
    </div>
    <div class="value" id="label-x2">6.50</div>
</div>

<p>Expected payoff f₁(x₁, x₂): <span id="payoff">0.000</span></p>

<script src="https://cdnjs.cloudflare.com/ajax/libs/plotly.js/3.1.0/plotly.min.js" integrity="sha512-iXeIWNSxrG0kro2hgWe7onPrTS2g9AeLbojfGJM89zhrunfCSEkHUux9ACjjpem5ob1J2uJ5cNxAn7gJOwygrQ==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jstat/1.9.6/jstat.js" integrity="sha512-MN0us5YWgC/39SjILvwt7/54yevWDlXVmzhVEfxGfnLGdyEoGisHb4ycAnk4BrT+47w8qj2LMjRr4bNeGZfYNA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
<script>
  // Distribution parameters
  const mu = 5, sigma = 1.5;

  // jStat provides normal.pdf(x, mean, sd) and normal.cdf(x, mean, sd)
  function pdf(x) { return jStat.normal.pdf(x, mu, sigma); }
  function cdf(x) { return jStat.normal.cdf(x, mu, sigma); }

  // grid for plotting
  const xs = Array.from({length: 400}, (_,i)=> i*0.05); // 0..19.95
  const pdfVals = xs.map(pdf);
  const maxPdf = Math.max(...pdfVals);

  // initial guesses
  let x1 = parseFloat(document.getElementById('slider-x1').value);
  let x2 = mu + sigma; // start with high x2 (1 sd above mean)

  function payoff(x1, x2) {
    if (x1 > x2) return 1 - cdf(x1);
    if (x1 < x2) return cdf(x2) - cdf(x1);
    return 0;
  }

  function buildRegionTrace(x1, x2) {
    // Return a well-formed Plotly trace even when empty so plotly doesn't complain
    if (x1 < x2) {
      const rx = xs.filter(v => v >= x1 && v <= x2);
      return {
        x: rx,
        y: rx.map(pdf),
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        fillcolor: 'rgba(0,0,255,0.25)',
        line: {color: 'transparent'},
        name: 'x₁ wins'
      };
    } else if (x1 > x2) {
      const rx = xs.filter(v => v >= x1);
      return {
        x: rx,
        y: rx.map(pdf),
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        fillcolor: 'rgba(0,0,255,0.25)',
        line: {color: 'transparent'},
        name: 'x₁ wins'
      };
    }
    // empty region
    return {
      x: [], y: [], type: 'scatter', mode: 'lines', name: 'x₁ wins', visible: false
    };
  }

  function updatePlot() {
    // update labels & payoff
    document.getElementById('label-x1').textContent = x1.toFixed(2);
    document.getElementById('label-x2').textContent = x2.toFixed(2);
    document.getElementById('payoff').textContent = payoff(x1, x2).toFixed(3);

    const tracePDF = {
      x: xs,
      y: pdfVals,
      type: 'scatter',
      mode: 'lines',
      name: 'PDF',
      line: {color: 'gray'}
    };

    const region = buildRegionTrace(x1, x2);

    const lineX1 = {
      x: [x1, x1], y: [0, maxPdf * 1.05],
      mode: 'lines', name: 'x₁', line: {color: 'blue', width: 2}
    };
    const lineX2 = {
      x: [x2, x2], y: [0, maxPdf * 1.05],
      mode: 'lines', name: 'x₂', line: {color: 'red', width: 2}
    };

    const layout = {
      margin: {t:20, b:40}, showlegend: false,
      xaxis: {title: 'Value'},
      yaxis: {title: 'PDF'}
    };

    // Use Plotly.react to efficiently update the plot
    Plotly.react('plot', [tracePDF, region, lineX1, lineX2], layout, {responsive: true});
  }

  // wire up slider
  document.getElementById('slider-x1').addEventListener('input', e => {
    x1 = parseFloat(e.target.value);
    updatePlot();
  });

  // wire up toggle buttons
  document.getElementById('btn-low').addEventListener('click', e => {
    x2 = mu - sigma; // 1 sd below mean
    document.getElementById('btn-low').classList.add('active');
    document.getElementById('btn-high').classList.remove('active');
    updatePlot();
  });

  document.getElementById('btn-high').addEventListener('click', e => {
    x2 = mu + sigma; // 1 sd above mean
    document.getElementById('btn-high').classList.add('active');
    document.getElementById('btn-low').classList.remove('active');
    updatePlot();
  });

  // initial render
  updatePlot();
</script>
</div>

### Proof

**Theorem:** Under the above assumptions, no pure strategy Nash Equilibrium exists.

Given $x_2$, suppose by way of contradiction that there's some $x_1 \in \beta_1(x_2)$. This leads us to two cases:

**(i)** If $x_1 > x_2$, we can always reduce $x_1$ to something arbitrarily close to $x_2$ to improve the payoff. Fix some $\epsilon > 0$ such that $x_2 + \epsilon < x_1$. Then $f_1(x_1, x_2) = 1 - F(x_1) < 1- F(x_2 + \epsilon) = f_1(x_2 + \epsilon, x_2)$ (note we used the strict monotinicity of $F$ here).

**(ii)** On the other hand, if $x_1 < x_2$, we payoff would only increase if $x_1$ were reduced. Fix some $\epsilon > 0$. We have $f_1(x_1, x_2) = F(x_2) - F(x_1) < F(x_2) - F(x_1 - \epsilon) = f_1(x_1 - \epsilon, x_2)$.

In either case, there's a better strategy than $x_1$ when Player 2 plays $x_2$, so $x_1 \notin \beta_1(x_2)$. Hence no best response $\beta_1(x_2)$ is attained. By symmetry of the payoff functions, the same applies to $\beta_2(x_1)$.

## Mixed Strategy Equilibrium

It's tempting to stop there and say there's no optimal way to play the game. But Game Theory gives us another option: [mixed strategy equilibria](https://saylordotorg.github.io/text_introduction-to-economic-analysis/s17-03-mixed-strategies.html). The idea is that even in games where there's no pure mutual best response, we can still find probability distributions over potential actions such that if each player chooses their actions according to their distribution, we can reach equilibrium.

A classic example is the "matching pennies" game. Both players choose either heads or tails. If they choose the same value, Player 1 wins. If they choose different values, Player 2 wins. In either case, the losing player will regret not having chosen the opposite side of the coin, meaning there's no equilibrium solution. However, if both players choose to select their side randomly (50% heads and 50% tails), there's no more room for regret. Even though a player might wish they'd chosen differently in an individual loss, they still know that they couldn't have chosen a better _strategy_ to maximize their overall expected payoff.

_To be continued_

<!--## Original Approach

Let $p \sim \mathcal{N}(\mu, \sigma^2)$ be the price of the prize, and let $\hat{p}$ be the contestant's guess. The contestant wins if $\hat{p} \leq p$. Let's model this with a reward function $R$:

$$
R(p, \hat{p}) = \begin{cases}
\exp\left({-\frac{p-\hat{p}}{\sigma}}\right) & \text{if } \hat{p} \leq p \\\\\\
0 & \text{if } \hat{p} > p \end{cases}
$$

This is pretty arbitrary, but it meets the goal of giving 0 reward when the guess is over the price, and giving higher reward for guesses that are closer to the actual price.

The expected reward for a guess $\hat{p}$ is:

$$
\mathbb{E}[R(p, \hat{p})] = \int\_{-\infty}^{\infty} R(p, \hat{p}) f(p) dp \\\\\\
$$

Note that this integral is 0 where $p < \hat{p}$, so we can simplify the limits. Expanding the product in the integrand gives:

$$
\mathbb{E}[R(p, \hat{p})] = \int\_{\hat{p}}^{\infty} \frac{1}{\sqrt{2\pi\sigma^2}}\exp\left(\frac{\hat{p}-p}{\sigma}-\frac{1}{2}\left(\frac{p-\mu}{\sigma}\right)^{2}\right)dp
$$-->
