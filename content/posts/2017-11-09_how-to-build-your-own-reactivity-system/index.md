---
title: "How to Build Your Own Reactivity System"
author: "Matthew Dangerfield"
date: 2017-11-09T22:14:34.378Z
lastmod: 2019-08-23T14:14:30-07:00

description: "A couple of months ago, I attended an in-person meetup at Frontend Masters called Vue.js Advanced Features from the Ground Up. It was really awesome because we got to learn about Vue.js from its…"

subtitle: "Based on Vue.js’s reactivity system"

image: "/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/2.gif"
images:
  - "/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/1.jpeg"
  - "/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/2.gif"
  - "/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/3.png"

aliases:
  - "/how-to-build-your-own-reactivity-system-fc48863a1b7c"
---

![image](/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/1.jpeg)

_Want to learn about Vuex? Check out my_ [_hands on course_](https://bit.ly/31v8NPq)_! . Message me to be an early reviewer and get it for free._

A couple of months ago, I attended an in-person meetup at [Frontend Masters](https://medium.com/u/1b199ed2dfd) called _Vue.js Advanced Features from the Ground Up_. It was really awesome because we got to learn about [Vue.js](https://medium.com/u/9b930cf6db26) from its creator, Evan You. Instead of just teaching us how to use Vue, he showed us how to actually implement a few parts of it. Reactivity was the part that interested me the most, so, after the class, I dug into [Vue’s source code](https://github.com/vuejs/vue) to learn more about exactly how its reactivity system works. In this guide, I’ll explain how Vue’s reactivity system is implemented, and show how you to make your own working reactivity system.

### The Problem of Reactivity

What is reactivity? I really like how Evan explained it in his talk, so I’ll use his examples. Say you have a variable `a`.

```js
let a = 3;
```

Now, let’s say you have another variable `b`, such that `b = a * 3` .

```js
let b = a * 3;
console.log(b); // 9
```

That’s working just fine. But what happens if you need to change `a`?

```js
a = 5;
console.log(b); // 9
```

Even though `a` changed, `b` stayed the same. Why? Because you never changed `b`. If you want to make sure `b` is still `a * 3`, you’d have to do it like this:

```js
a = 5;
b = a * 3;
console.log(b); // 15
```

Now, this is working, but it would be annoying to have to type out `b = a * 3`every time `a` changes. We could solve this problem by wrapping the update to `b` in a function

```js
let b;
function onUpdate() {
  b = a * 3;
}

let a = 3;
onUpdate();
console.log(b); // 9

a = 5;
onUpdate();
console.log(b); // 15
```

But, this still isn’t a very nice way of doing things. While it’s not too problematic in this example, imagine if we had 10 different variables, that all had a potentially complex relation to another variable or variables. We’d need a separate `onUpdate()` method for each variable. Instead of this awkward and imperative API, it’d be nice to have a simpler, more declarative API that just does what we want it to do. Evan compared it to a spreadsheet, where we can update one cell and know that any cell that depends on the one we updated will automatically update itself.

![screen capture of a spreadsheet reactively updating](/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/2.gif)

### Solutions

The good thing is that people have already come up with a number of solutions to this reactivity problem. In fact, each of the three major web development frameworks provides a solution to reactivity:

1.  **React’s State Management**: Create a function `setState()`, and use that whenever we need to update `a`. Then, inside `setState()`, call a render function that updates the view to display the proper value of `b`.
2.  **Angular’s Dirty Checking**: Create a function `detectChanges()`, that runs through every property it’s tracking and checks if it’s changed since the last time it was checked. If it finds an updated property (e.g. `a`), then it updates every property that uses the updated property (e.g. `b`). Then, run the `detectChanges()` function every few milliseconds and whenever it’s logical.
3.  **Vue’s reactivity system**: Add ES5 getters and setters to each tracked property. Whenever a tracked property is accessed, mark the function that accessed the property as a “subscriber”. Whenever the property is changed, notify each subscriber of the change.

We’re going to implement Vue’s reactivity system in pure JavaScript. Before we get into the code, let’s go into some more details about exactly what we’re building.

### What We’re Building

![](/posts/2017-11-09_how-to-build-your-own-reactivity-system/images/3.png)

_Diagram of how Vue’s reactivity system works. Source: https://vuejs.org/v2/guide/reactivity.htm_

We’re going to create a class, called **_Watcher_**, that takes in two properties: a **value getter** and a **callback**. The value getter can be any function that has a return value. Example:

```js
let a = 3;
const getter = () => a * 3;
```

The getter will probably have **dependencies**, or variables it depends on to get its value. In the example above, `a` is the only dependency of the getter function. Getter functions can have multiple dependencies, though. For example, `() => x * y` has both `x` and `y` as dependencies.

Whenever a dependency of the getter function changes, we’ll automatically run the callback function, passing in the current value and the previous value. This callback can do anything, from just logging the value to displaying the value in a div.

Finally, we’ll create a `defineReactive()` function, that adds change detection to a property on an object. We’ll also create a `walk()` function that adds change detection to all properties on an object. This will allow properties of the object to be used as dependencies. We will implement this change detection the same way Vue does: by defining ES5 [getters and setters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/get). While this approach does have some limitations (described in the [docs](https://vuejs.org/v2/guide/reactivity.html)), it’s an extremely efficient and simple way of getting reactivity, since the JavaScript engine is ultimately providing the change detection.

> **Footnote:** The unreleased [Vue 3 will use ES6 Proxies](https://blog.cloudboost.io/reactivity-in-vue-js-2-vs-vue-js-3-dcdd0728dcdf) instead of getters and setters, but I believe the rest of Vue’s reactivity system won’t change that much.

When we’re finished, we’ll have a general-purpose reactivity API. Here’s an example of its usage:

```js
const data = {
  name: "World",
  feeling: "like"
};

walk(data); // adds reactivity to the data object
new Watcher(
  () => `Hello, ${data.name}. I ${data.feeling} Vue.js.`, // the value getter we're watching
  (val, oldVal) => console.log(val) // the callback, fired on changes to dependencies of the value getter
); // logs 'Hello, World. I like Vue.js'

data.name = "Universe"; // logs 'Hello, Universe. I like Vue.js'
data.feeling = "love"; // logs 'Hello, Universe. I love Vue.js'
```

### Deps

The first step is to implement the **_Dep_** class. **_Dep_**, short for dependency, is a wrapper around a value. Our implementation will be directly based on [Vue’s **_Dep_** class](https://github.com/vuejs/vue/blob/dev/src/core/observer/dep.js). Each **_Dep_** instance maintains a list of subscribers, or `subs`, that all want to know whenever the dep’s value changes. These subscribers are instances of the **_Watcher_** class, which we will implement in the next section. Each **_Dep_** instance is responsible for calling each subscriber’s `update()` method whenever the dep’s value changes.

Even though **_Dep_** instances are responsible for alerting subscribers of changes to a value, each **_Dep_** instance doesn’t actually know what value it’s watching. So, it each **_Dep_** instance has a `notify()` method, which lets it know when its value changes. We’ll talk more about who calls `notify()` later, but for now just assume it gets called whenever the watched value changes. Here’s a working **_Dep_** implementation:

```js
// See https://github.com/vuejs/vue/blob/be9ac624c81bb698ed75628fe0cbeaba4a2fc991/src/core/observer/dep.js
// for full implementation

class Dep {
  constructor() {
    this.subs = new Set();
  }

  addSub(sub) {
    this.subs.add(sub);
  }

  depend() {
    if (Dep.target) {
      Dep.target.addDep(this);
    }
  }

  notify() {
    this.subs.forEach(sub => sub.update());
  }
}
```

What is `Dep.target`, and when does it get a value? `Dep.target` is a **_Watcher_** instance that lets the **_Dep_** instance know who’s using its value. This is necessary because the **_Dep_** instance needs to register itself as a dependency of the target watcher. There are two functions, `pushTarget()` and `popTarget()`, that manage the current **Dep.target**. Here’s what these look like:

```js
// the current target watcher being evaluated.
// this is globally unique because there could be only one
// watcher being evaluated at any time.
Dep.target = null;
const targetStack = [];

function pushTarget(_target) {
  if (Dep.target) targetStack.push(Dep.target);
  Dep.target = _target;
}

function popTarget() {
  Dep.target = targetStack.pop();
}
```

We’ll discuss these methods more in the next section.

### Watchers

According to the [source code](https://github.com/vuejs/vue/blob/be9ac624c81bb698ed75628fe0cbeaba4a2fc991/src/core/observer/watcher.js):

> A watcher parses an expression, collects dependencies, and fires callbacks when the expression value changes. This is used for both the \$watch() api and directives.

The **_Watcher_** class takes in a **getter** **function** and a **callback function**, and stores an array of dependencies of the value computed by the getter function. It tracks the values of the dependencies, and runs the callback function whenever any of these dependencies change. Here’s an example:

```js
let a = 5,
  b = 4;

const getter = () => a + b;
const callback = val => console.log(val);

const watcher = new Watcher(getter, callback);

a = 6; // 10 is logged to the console`
```

In Vue’s code, the **_Watcher_** class has several methods, but, for our purposes, we just need to implement three of them:

1.  `get()`. This method calls the getter function supplied in the constructor to figure out what the initial value is. Before it calls the getter, it sets itself as the current **_Dep_** target watcher, using the `pushTarget()` \***\* method. This makes it so all values used in the getter function will add the **_Watcher_** instance as a subscriber. This is important because the **_Watcher_\*\* instance needs to be linked to its dependencies in some way so it can be notified whenever the value of one of its dependencies changes.
2.  `addDep(dep)`. This method adds itself as a subscriber to the given dependency. This method is called by the _Dep#depend()_ method, which we’ll discuss in more detail in the next section.
3.  `update()`. This method calls the callback function supplied in the constructor with the old value and new value as arguments. It gets used when the _Dep#notify()_ method calls `update` on each of its subscribers after its value changes.

Here’s the code for our **_Watcher_** class:

```js
// See https://github.com/vuejs/vue/blob/be9ac624c81bb698ed75628fe0cbeaba4a2fc991/src/core/observer/watcher.js
// for full implementation

class Watcher {
  constructor(getter, cb) {
    this.getter = getter; // function that returns a value based on reactive properties
    this.cb = cb; // function that is run on value updates, and is passed value and old value
    this.value = this.get();
    this.cb(this.value, null);
  }

  get() {
    pushTarget(this); // from dep.js
    const value = this.getter();
    popTarget(); // from dep.js

    return value;
  }

  addDep(dep) {
    dep.addSub(this);
  }

  update() {
    const value = this.get();
    const oldValue = this.value;
    this.value = value;

    this.cb(value, oldValue);
  }
}
```

### `defineReactive()`

According to the [source code](https://github.com/vuejs/vue/blob/61187596b9af48f1cb7b1848ad3eccc02ac2509d/src/core/observer/index.js), `defineReactive()` "defines a reactive property on an Object". This is done by adding getters and setters to a given property of a given object. Each property has a **_Dep_** instance associated with it. Whenever a reactive object’s property is accessed, the getter calls _Dep#depend(),_ which adds the current target **_Watcher_** as a subscriber to the property’s **_Dep_** instance. Whenever the property is changed, the setter calls _Dep#notify()_ which calls the _update()_ method of each of the subscribers to the property’s **_Dep_**_._ Here’s _defineReactive()_, based on the source code:

```js
// See https://github.com/vuejs/vue/blob/61187596b9af48f1cb7b1848ad3eccc02ac2509d/src/core/observer/index.js
// for full implementation

/* Walk through each property and convert them into
 * getter/setters. This method should only be called when
 * value type is Object.
 */
function walk(obj) {
  const keys = Object.keys(obj);
  for (let i = 0; i < keys.length; i++) {
    defineReactive(obj, keys[i], obj[keys[i]]);
  }
}

function defineReactive(obj, key, val) {
  if (val !== null && typeof val === "object") {
    walk(val); // Add reactivity to all children of val
  }

  const dep = new Dep();
  Object.defineProperty(obj, key, {
    enumerable: true,
    configurable: true,
    get: function reactiveGetter() {
      dep.depend();

      return val;
    },
    set: function reactiveSetter(newVal) {
      val = newVal;
      dep.notify();
    }
  });
}
```

### How it all works together

Now we’ve written each part of our reactivity system, but how does it all work? Each part of the system is so interconnected with all the other parts that it can be difficult to understand. Let’s walk step by step through what happens in an example usage of our **_Watcher_** class.

We’ll start by setting everything up:

```js
const foods = { apple: 5 };

// make foods reactive, register deps for each property
walk(foods);

// Instantiate the watcher, which takes a getter and a callback
const foodsWatcher = new Watcher(
  () => foods.apple,
  () => console.log("change")
);
```

First, the constructor for the **_Watcher_** class runs the following:

```js
this.value = this.get();
```

Here’s _Watcher#get()_:

```js
pushTarget(this); // Imported from dep.js
const value = this.getter();
popTarget(); // Imported from dep.js

return value;
```

First, it calls the `pushTarget()` function, which assigns `this` (the `foodsWatcher`) to `Dep.target`. Then, it calls `this.getter()`, the first function passed to the **_Watcher_** constructor. The getter for the `foodsWatcher` just returns the value of `foods.apple`. Since `foods.apple` was made reactive by `defineReactive()`, it will also run the reactive getter:

```js
// adds Dep.target as a subscriber to the property's dep instance
dep.depend()
return value
```

This registers `foodsWatcher` as a subscriber to the **_Dep_** instance associated with `foods.apple` . So there’s now a connection between the `foodsWatcher` and `foods.apple`.

How is this helpful? Let’s say we change `foods.apple`.

```js
foods.apple = 6
```

Doing this will call the setter on `foods.apple`. The setter runs `dep.notify()`, which calls `update()`on each of the dep’s subscribers. Since the `foodsWatcher` is a subscriber to the **_Dep_** instance, the `dep.notify()` call will trigger the update method on `foodsWatcher`. What does _Watcher#update()_ do?

```js
update() {
  const value = this.get()
  const oldValue = this.value
  this.value = value

  this.cb(value, oldValue)
}
```

It updates its knowledge of the current value, and then calls the callback supplied in the constructor. Remember that the callback we specified was

```js
() => console.log('change')
```

So, when we change `foods.apple`, our reactivity system will let us know! The cool thing is that this happened without any dirty checking every millisecond. It happened without us having to explicitly set the state. It just _worked_, without us having to think about it at all, just like a spreadsheet. That’s what makes Vue’s reactivity system so incredible.

If you want to see all the code for our reactivity system in one place, I made a [plunker](http://embed.plnkr.co/rMLS2Swq4mz0aXcxqDYA/) with a really cool demo. Thanks for reading!

### Resources

- The [Frontend Masters course](https://frontendmasters.com/live-event/vue-js-advanced-features-ground/) I went to (if you have a Frontend Masters subscription)
- Vue’s [docs on reactivity](https://vuejs.org/v2/guide/reactivity.html)
- A [talk Evan gave](https://www.dotconferences.com/2016/12/evan-you-reactivity-in-frontend-javascript-frameworks) in 2016 on reactivity
- Vue’s [source code](https://github.com/vuejs/vue/tree/dev/src/core/observer) (the ultimate reference)
