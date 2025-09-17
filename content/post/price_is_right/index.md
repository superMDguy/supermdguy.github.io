---
title: "Is the Price Right?"
date: 2025-09-10T22:54:53-06:00
math: true
localKatex: true
---

In the game show "The Price is Right", contestants try to guess the price of a prize without going over. Assume you're a contestant, and you somehow know the exact distribution of prices for the prize. Would you be able to win?

## Pure Strategy Equilibrium

Let $V \sim \mathcal{D}$ be a random variable representing the true value of the prize, with CDF $F(v)$, supported on $[0, v_{\text{max}})$ (we assume $F$ is strictly increasing and the corresponding PDF is continuous for simplicity). Suppose we're playing with two contestants, who simultaneously makes guesses $x_1, x_2 \in [0, \infty]$. They receive a reward of 1 if they are closest to the randomly selected price $v$ without going over, and 0 otherwise (we'll ignore ties throughout the analysis). This leads to symmetric (expected) payoff functions

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

Note that the payoff depends only on $F(x)$. To simplify, we'll assume $F$ has an inverse, allowing us to express each player's action as a quantile: $q_1 = F(x_1)$ and $q_2 = F(x_2)$. Once we find the optimal quantile $q \in [0, 1]$, we can compute $F^{-1}(q) = x$ to get the correct bid. This will make it easier to work with arbitrary price distributions $\mathcal{D}$.

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
    <input type="range" id="slider-x1" min="0" max="10" step="0.01" value="2" />
    <div class="value" id="label-x1">2.00</div>
    <div style="flex-grow: 1;"></div>
    <div class="toggle-buttons">
        <button class="toggle-btn" id="btn-low" data-value="low">Low x₂</button>
        <button class="toggle-btn active" id="btn-median" data-value="median">Median x₂</button>
        <button class="toggle-btn" id="btn-high" data-value="high">High x₂</button>
    </div>
    <div class="value" id="label-x2">5</div>
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
  let x2 = mu; // start with median x2 (1 sd above mean)

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
    document.getElementById('btn-median').classList.remove('active');
    document.getElementById('btn-high').classList.remove('active');
    updatePlot();
  });

   document.getElementById('btn-median').addEventListener('click', e => {
      x2 = mu
      document.getElementById('btn-low').classList.remove('active');
      document.getElementById('btn-median').classList.add('active');
      document.getElementById('btn-high').classList.remove('active');
      updatePlot();
    });

  document.getElementById('btn-high').addEventListener('click', e => {
    x2 = mu + sigma; // 1 sd above mean
    document.getElementById('btn-high').classList.add('active');
    document.getElementById('btn-median').classList.remove('active');
    document.getElementById('btn-low').classList.remove('active');
    updatePlot();
  });

  // initial render
  updatePlot();
</script>
</div>

Let's analyze the [best response](https://en.wikipedia.org/wiki/Best_response) [function](https://math.stackexchange.com/questions/293404/finding-mixed-nash-equilibria-in-continuous-games) for each contestant. This is a concept from game theory that finds the optimal choice for one player, given what the other player has chosen. When an action is a mutual best response, neither player would be choose to play differently, given what the other player has played. This leads to [Nash Equilibrium](https://en.wikipedia.org/wiki/Nash_equilibrium). So finding the best response for each player is the first step to determining if an equilibrium solution is possible.

We seek to prove that there's no best response to any opponent moves. For any proposed best response to Player 2's choice, we can always find a Player 1 choice that's better. If the proposed best response is above Player 2's, you'd do better if you dropped your guess so it's just a little bit higher than Player 2, to minimize your risk of going over while still ensuring you're closer to the true price than Player 2. On the other hand, if the proposed best response is below Player 2's, then you'd do better dropping your guess even further to more fully capitalize on the times when Player 2 goes over.

### Proof

**Theorem:** Under the above assumptions, no pure strategy Nash Equilibrium exists.

Given $x_2$, suppose by way of contradiction that there's some $x_1 \in \beta_1(x_2)$. This leads us to two cases:

**(i)** If $x_1 > x_2$, we can always reduce $x_1$ to something arbitrarily close to $x_2$ to improve the payoff. Fix some $\epsilon > 0$ such that $x_2 + \epsilon < x_1$. Then $f_1(x_1, x_2) = 1 - F(x_1) < 1- F(x_2 + \epsilon) = f_1(x_2 + \epsilon, x_2)$ (note we used the strict monotinicity of $F$ here).

**(ii)** On the other hand, if $x_1 < x_2$, we payoff would only increase if $x_1$ were reduced. Fix some $\epsilon > 0$. We have $f_1(x_1, x_2) = F(x_2) - F(x_1) < F(x_2) - F(x_1 - \epsilon) = f_1(x_1 - \epsilon, x_2)$.

In either case, there's a better strategy than $x_1$ when Player 2 plays $x_2$, so $x_1 \notin \beta_1(x_2)$. Hence no best response $\beta_1(x_2)$ is attained. By symmetry of the payoff functions, the same applies to $\beta_2(x_1)$.

## Mixed Strategy Equilibrium

It's tempting to stop there and say there's no optimal way to play the game. But Game Theory gives us another option: [mixed strategy equilibria](https://saylordotorg.github.io/text_introduction-to-economic-analysis/s17-03-mixed-strategies.html). The idea is that even in games where there's no pure mutual best response, we can still find probability distributions over potential actions such that if each player chooses their actions according to their distribution, we can reach equilibrium.

A classic example is rock paper scissors. If you play rock and your opponent plays paper, you'll regret not doing scissors instead. In fact, no matter what, the losing player will wish they'd chosen a different strategy. However, if both players choose to select randomly between rock/paper/scissors, there's no more room for regret. Even though a player might wish they'd chosen differently in an individual loss, they still know that they couldn't have chosen a better _strategy_ to maximize their overall expected payoff.

The key idea in finding a mixed strategy equilibrium is ensuring you're **indifferent** to the action you choose, meaning all actions have equal expected value for you. If this wasn't the case, you'd be better off playing a different strategy that doesn't leave your action up to chance. We can solve for indifference by finding a distribution over your opponent's actions that make it so your expected value is constant. Put mathematically, this means solving

$$
\mathbb{E}_{q_2}\big[ f_1(q_1, q_2) \big] = c,
\quad \forall q_1
$$

In integral form, this means

$$
\int_0^1 f_1(q_1, q_2) g(q_2) dq_2 \\\\
= \int_0^{q_1} (1 - q_1) g(q_2) dq_2 + \int_{q_1}^1 (q_2 - q_1) g(q_2) dq_2 = c
$$

Differentiating both sides with respect to $q_1$ gives

$$
g(q_1) - q_1 g(q_1) - \int_0^1 g(q_2) dq_2 = 0
$$

Since $g$ must be a PDF that integrates to 1, we can simplify to

$$
g(q_1)(1 -q_1) = 1 \\\\
g(q_1) = \frac{1}{1-q_1}
$$

Note that this doesn't integrate to 1 over the full $[0, 1]$ domain of our quantile support, so we need to set it to 0 some places. We need to choose some $a$ and $b$ such that $\int_a^b \frac{1}{1-q} dq = 1$. Evaluating the integral gives $\ln\left(\frac{1-a}{1-b}\right)=1$, which means we need $\frac{1-a}{1-b} = e$ or $b = \frac{a + e - 1}{e}$. Plugging this back into our original payoff function gives:

$$
\int_a^{q_1} \frac{1 - q_1}{1 - q_2} dq_2 + \int_{q_1}^{\frac{a + e - 1}{e}} \frac{q_2 - q_1}{1 - q_2} dq_2
= \frac{1-a}{e}
$$

So to maximize our payoff, we should minimize $a$, leading to $a = 0$, $b = \frac{e-1}{e} = 1 - e^{-1}$. So our final mixed strategy distribution is:

$$
g(q) = \begin{cases}
\frac{1}{1-q} & 0 \leq q < 1 - e^{-1} \\\\
0 & \text{otherwise}
\end{cases}
$$

![Mixed Strategy Distribution](optimal_strategy.svg)

This gives us an expected payoff of $e^{-1} \approx 0.368$.

### Analysis

To see how well this strategy performs, I ran a simulation where two players play against each other 100,000 times. Player 1 uses the optimal mixed strategy above, while Player 2 bids a fixed quantile. The price distribution is $V \sim \mathcal{N}(550, 300)$ (truncated).

![Mixed Strategy Win Comparison](g_vs_percentile.svg)

I thought this would be my moment! I'd show how the equilbrium strategy smokes any pure strategy, and move on. However, that's not what happened at all. Around the 33-68 percentile range (exactly where a normal player would be guessing), the pure strategy performs _better_ than the mixed strategy! How did that happen?

It turns out that because it's possible for both players to go over, this isn't a zero-sum game. Because of that, the equilibrium strategy isn't necessarily dominant. It's only optimal against a player who's also using the equilibrium strategy. So if you actually were to get on the show, it'd probably be best to go for either the 50 or 0 percentile strategy, as described above.

The mixed strategy shines because it puts a cap on the win rate of your opponent. No matter what strategy your opponent plays, they cannot win more than ~36.8% of the time. In the rock paper scissors example from earlier, you'll only win 1/3 of the time against someone who plays rock, so it might seem like a paper-only strategy would be better. But that would remove the protection you get from playing the mixed strategy, which guarantees you're unpredictable enough to not get defeated more than 1/3 of the time

## Conclusion

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

$$
-->

<style>
img { border-radius: 16px; }
</style>
