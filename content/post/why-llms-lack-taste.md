---
title: "Why LLMs (still) lack taste"
date: 2026-06-09
tags: ["ai", "reinforcement-learning"]
---

Frontier LLMs are really smart, and they're [becoming particularly good at software development](https://metr.org/time-horizons/). It feels like [every week](https://artificialanalysis.ai/trends) there's a new model release that achieves SOTA scores on a handful of benchmarks. I use LLMs to build software every day, and they're incredibly useful, and getting better. But I'm still frequently surprised by the _types_ of mistakes they make.

I don't expect LLMs to be perfect. Even smart humans make mistakes! But LLMs often make errors that a human with a similar depth of knowledge would _never_ make. Their capabilities feel jagged; they'll brilliantly pull together thousands of error logs into a coherent analysis that would've taken me hours, but then use blatantly flawed reasoning to derive the root cause. So why does "PhD-level intelligence" make these kinds of mistakes?

It feels like, despite all the benchmarks, there's some orthogonal "taste" property that LLMs lack.

## What is "taste"?

It's really easy to shift goalposts when talking about LLM performance. So to be precise, I'll define _taste_ as **the capacity to choose the _best_ option from a set of _correct_ options**. In software, for example, it's the ability to look at two pieces of code that both pass tests performantly, and choose the one that's going to cause the least pain six months later. Of course, this is often context-dependent and subjective. But that's what makes it so valuable and difficult!

The more LLMs are used, the more taste matters. If you're reviewing every line of code that a model spits out, you can use your own taste to identify code smells, ask the model to use a different approach, and move on. This gets harder as LLMs do more work and create large PRs to review, but it's manageable. If you're taking the dark factory approach, though, subtle taste errors will compound into an unmaintainable mess.

Often, you can work around taste issues by giving the LLM better context on the problem. But I see the need for context engineering as a failure of taste! If I woke up in a dark void with no memories and was told to build an analytics dashboard, I'd probably ask for some context before blindly writing code. How many users does it need to support? What does the business do? What metrics are important and actionable? Gathering the right degree of context is itself an art that requires taste. In an ideal world, context management would be an emergent ability of tasteful models, not something managed from the outside.

## How do humans acquire taste?

So how do humans develop the ability to decide between two options that seem equally good? Matheus Lima [writes](https://terriblesoftware.org/2026/03/27/good-taste-is-just-experience/)

> When I was junior, I’d review PRs myself and genuinely have no idea if the code was good. I’d read through it and think “this… seems fine?” I hadn’t lived through enough production incidents to recognize what “this will break at scale” actually looks like. I hadn’t read enough good code to spot bad code by feel. Now, after years (16!) of this, I can look at a PR and something just catches.

That really clicked for me! Taste isn't some magical ability to reason about some intrinsic property of code, it's something that comes from _experiencing_ code either working or failing in a particular production context. People often try to compile lists of rules for writing maintainable/performant/debuggable code. But all of these rules are context-dependent, which means they often conflict with one another. Developing taste requires learning which properties of code are desirable in different contexts. For humans, developing taste takes place over years of working on a variety of projects with different contextual goals and constraints.

## Why do LLMs struggle?

Billions (trillions?) of dollars have been poured into training ever-more-capable coding agents, so why isn't this a solved problem? At first, LLMs were trained on next token prediction, which taught them to write perfectly mediocre code. At this point, they were great for replacing StackOverflow, but not much else. As frontier labs poured more money and compute into post-training, with instruction fine-tuning and then RLHF, LLMs got better at writing good code, but still struggled to demonstrate good taste.

Without explicit context on the problem at hand, good taste is an ill-defined problem. Imagine two terraform configs for a web server, one with a load balancer and multiple container instances, and one running on a single machine. Which is better? It depends!

Fine-tuning and RLHF allowed LLMs to write code that matched the distribution of "good code". But code alone doesn't contain enough context for any number of weights to capture why it was written the way it was. To go further, LLMs needed to learn from experience, just like humans. Luckily, there was already decades of research into learning from experience with reinforcement learning (RL) [^1].

## Can you RLVR your way to taste?

After fine-tuning and RLHF, the next wave of research focused on Reinforcement Learning from Verifiable Rewards (RLVR), a way to allow LLMs to learn directly from rewards in their environment. As part of post-training, LLMs are placed in a coding harness with the ability to call tools, and then given tasks with "verifiable" rewards. For example, they'll be given a codebase with a known bug, and instructed to fix the bug. The verification part comes from a reward signal, typically pass/fail from unit tests. RLVR has led to the largest leaps in coding ability over the last ~1.5 years, since it allows LLMs to learn directly from experience, instead of just mimicking human output.

In theory, this should be the end of the story. Taste comes from experience, RLVR lets LLMs learn from experience, done. So why do frontier models still struggle?

RLVR is often focused on short tasks like those in [SWE-bench](https://www.swebench.com/). Because of the need for objectively verifiable rewards, they're scoped to narrowly specificified tasks with objective pass/fail criteria. That can't capture something like "should I add a load balancer in front of my backend", which depends entirely on production context, and probably won't make a difference in whether tests are passing [^2]. There are hundreds of ways to write code that gets tests to pass, but there are often other real-world goals and constraints that aren't captured by pass/fail metrics. Goals like maintainability, uptime, and debuggability aren't "verifiable", so they can't be captured in a typical RLVR framework[^3]. RLVR taught LLMs how to write _correct_ code, but they weren't able to learn from the long-term effects of the code they wrote.

Because of this, we get headlines like ["Many SWE-bench passing PRs would not be merged into main"](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/). But what if agents were able to learn like a human software developer does, from production outages and frustrated users?

## An idea

Here's my crazy idea for a long-horizon RLVR harness that I think could solve this issue. Create a clone of some common SaaS. It doesn't matter if it's buggy, in fact that'll just provide more "learning opportunities" down the line! Get it deployed on a cloud hosting provider like AWS. Then, unleash thousands of agents that each simulate thousands of users of this SaaS: common and uncommon use-cases, different usage patterns, people trying to hack it, anything that a real-world product would run into. Then put one coding agent in charge of the whole thing, with full access to the code and the cloud hosting provider, and instruct it to run the business. Respond to customer complaints, fix bugs, maintain high uptime, implement feature requests, keep the hackers out. Give it a basic coding harness, but also allow it to change its own harness for better context management, etc. And then RL it up!

Of course you'd need a good reward signal, which would probably take some tuning. You could have metrics based on uptime, feature completion, or things like "user" bug reports, but all of those could be reward hacked pretty easily. I think a monetary reward signal would be the most interesting. Each simulated "user" would have a set of feature requests with a corresponding monetary value. They'd also have costs associated with crashes or downtime, and given enough downtime they'd cancel their subscription. Each agent would decide on different priorities for each of their simulated users, and over a large enough simulated customer base, that shouldn't be an easily hackable metric.

Overall, it would certainly be more expensive than a typical RL harness, but I think it would be much more similar to real-world software development than what you'd get from something like SWE-bench. And I think that would translate into LLMs with taste.

Feel free to wire me $10 million and I'll make it happen.

[^1]: My psychologist wife wanted me to mention that Reinforcement Learning is also an aspect of several theories in human psychology!

[^2]: (unless you have load tests on your prod infrastructure in your e2e test suite, in which case you have my respect)

[^3]: Recently Cognition released [a new benchmark](https://cognition.ai/blog/frontier-code) that captures some of these goals. I think it's really cool, but many of these goals are inherently subjective and difficult to measure objectively.
