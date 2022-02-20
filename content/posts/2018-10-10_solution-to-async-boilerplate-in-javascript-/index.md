---
title: "A solution to async boilerplate in JavaScript ✨"
author: "Matthew Dangerfield"
date: 2018-10-10T00:01:46.285Z
lastmod: 2019-08-23T14:14:32-07:00

description: ""

subtitle: "How to stop writing loading = true every time you make an HTTP request"

image: "/posts/2018-10-10_solution-to-async-boilerplate-in-javascript-/images/1.jpeg"
images:
  - "/posts/2018-10-10_solution-to-async-boilerplate-in-javascript/images/1.jpeg"

aliases:
  - "/a-solution-to-async-boilerplate-in-javascript-2fa717801c3b"
---

![image](/posts/2018-10-10_solution-to-async-boilerplate-in-javascript/images/1.jpeg)

[Source](https://en.wikipedia.org/wiki/Tuxedo#/media/File:Dinner_Jackets,_1898..jpg)

Have you ever written code that looks like this?

```js
function loadStuff() {
  state.loading = true;
  fetch("//myapi.com/stuff")
    .then(res => res.json())
    .then(data => {
      state.loading = false;
      state.stuff = data;
    });
}
```

Maybe you also have error handling or a fancy delayed spinner that adds even more complexity. Writing the same code for every single async task in your project can add a lot of boilerplate, especially if you have a lot of HTTP requests in your application.

Since this is such a common problem, [several](https://medium.com/stashaway-engineering/react-redux-tips-better-way-to-handle-loading-flags-in-your-reducers-afda42a804c6) [solutions](https://medium.com/@lachlanmiller_52885/a-pattern-to-handle-ajax-requests-in-vuex-2d69bc2f8984) [have](https://github.com/f/vue-wait) [already](https://gist.github.com/ddanger/21d7f4bd3580d2041b7c56ca04b25b8b) [been](https://medium.com/@Farzad_YZ/handle-loadings-in-react-by-using-higher-order-components-2ee8de9c3deb) [proposed](https://github.com/abdullah/vuex-module-generator). In fact, the React team is currently working on building a solution into React itself, through [React Suspense](https://medium.com/@baphemot/understanding-react-suspense-1c73b4b0b1e6). With all these potential solutions, it might seem like `isLoading` boilerplate is a solved problem.

However, almost all of these solutions are tied to a framework. This isn’t necessarily a problem — frameworks can be great! However, it’d be better to have a solution that works with pure JavaScript. This would make it so you can track the state of async requests in any situation: whether it’s in your UI framework of choice, Vanilla JS, or your favorite state management solution.

For example, I do a lot of work with Vue, and I found solutions that worked well with Vuex. But, they wouldn’t work at all if I wanted to track the state of request in a component’s state instead of the global store. There’s a similar issue with most of the React solutions. A pure JavaScript solution, on the other hand, would be able to handle all the complexities of async tasks while still being flexible enough to work with almost all frontend technology stacks.

I recently released [tuxi](https://github.com/superMDguy/tuxi), which aims to solve the async state boilerplate problem, while still meeting the flexibility requirements I outlined. Though it has a pretty simple API, it does some really cool things:

- Configurable delayed spinners by distinguishing between “pending” tasks and “spinning” tasks.
- Handles scenarios where multiple instances of a request are fired quickly: only the data from the most recently fired request will be returned.
- It can also handle multiple instances of a request where each request’s state is stored and accessed separately.
- Supports Vue and Vuex without reactivity or strict mode errors, via a plugin.
- Has a plugin API that will make it possible to add integration with React and Redux without too much work (open issue for a React plugin [here](https://github.com/superMDguy/tuxi/issues/1), if you’re interested and want to give a 👍).

### Examples

#### Pure JavaScript

```js
import tuxi from "tuxi";
import api from "./api";

const articlesTask = tuxi.task(api.fetchArticles);

// ⚡ Fire the api call
articlesTask.start();

// The task is immediately set to pending
console.log(articlesTask.pending); // true

// 🌀 The spinning property has a configurable delay
setTimeout(() => console.log(articlesTask.spinning), 1500); // true

// After a while...
console.log(articlesTask.hasValue); // true
console.log(articlesTask.value); // ['New Planet Discovered!', '17 Surprising Superfoods!', ...]
```

#### Vue

```vue
<template>
  <div class="wrapper">
    <div class="empty-message" v-if="articlesTask.empty">
      No articles
    </div>

    <div class="spinner" v-if="articlesTask.spinning">
      Loading articles...
    </div>

    <div class="error-message" v-if="articlesTask.error">
      {{ articlesTask.error.message }}
    </div>

    <ul v-if="articlesTask.hasValue">
      <li v-for="article in articles">
        {{ article.title }}
      </li>
    </ul>
  </div>
</template>

<script>
import tuxi from "tuxi";
import api from "./api";
export default {
  data() {
    return {
      articlesTask: tuxi.task(api.fetchArticles)
    };
  },
  computed: {
    articles() {
      return this.articlesTask.value;
    }
  }
};
</script>
```

#### Vuex

```js
import tuxi from "tuxi";
import Vuex from "vuex";
import Vue from "vue";
import api from "./api";

Vue.use(Vuex);

const store = new Vuex.Store({
  strict: true, // tuxi works in strict mode!

  state: {
    articles: [],
    articlesTask: tuxi.task(api.fetchArticles)
  },

  mutations: {
    SET_ARTICLES(state, articles) {
      state.articles = articles;
    }
  },

  actions: {
    async articles({ commit, state }) {
      const articles = await state.articlesTask.start();
      commit("SET_ARTICLES", articles);
    }
  }
});

tuxi.config.vuexStore = store;
// Now you can access $store.state.articlesTask in your components to look at the task's state
```

### Final Notes

Tuxi is still relatively new, but it’s pretty stable. It has [full](https://codecov.io/github/superMDguy/tuxi?branch=master) [passing](https://circleci.com/gh/superMDguy/tuxi/tree/master) unit test coverage, and I’m using it in production. Though I don’t have full documentation written yet, you can read the [tests](https://github.com/superMDguy/tuxi/tree/master/tests) for complete usage examples. Also, feel free to create an issue if you have any questions, requests, or suggestions, and I’ll get back to you as soon as I can.

UPDATE (10/11/2018): I wrote the [docs](https://github.com/superMDguy/tuxi/blob/HEAD/docs/readme.md).
