---
title: "How to control bootstrap’s css"
author: "Matthew Dangerfield"
date: 2017-08-10T17:05:43.937Z
lastmod: 2019-08-23T14:14:29-07:00

description: ""

subtitle: "In our Angular 4 project, we’re using a datepicker from ng-bootstrap. It has a lot of features (such as date ranges, minimum/maximum date…"

image: "/posts/2017-08-10_how-to-control-bootstraps-css/images/1.jpeg"
images:
  - "/posts/2017-08-10_how-to-control-bootstraps-css/images/1.jpeg"

aliases:
  - "/how-to-control-bootstraps-css-394f9928a499"
---

![image](/posts/2017-08-10_how-to-control-bootstraps-css/images/1.jpeg)

Source: [https://teckstack.com](https://teckstack.com)

In our Angular 4 project, we’re using a datepicker from [ng-bootstrap](https://ng-bootstrap.github.io/#/home). It has a lot of features (such as date ranges, minimum/maximum date validation, etc.) that are really useful to us. The only issue? As you can probably tell from the name, it uses bootstrap.

Bootstrap works great when it’s used to style an entire app. But as soon as we included it in our app, it changed a ton of our styling. I couldn’t just increase specificity in our styles, because bootstrap was targeting tags that we hadn’t styled at all. I thought I would have to manually create style rules that reverted everything that bootstrap added.

But then, I had a better idea. We use bootstrap by installing its [npm package](https://www.npmjs.com/package/bootstrap), and then @import-ing it into in our `app.component.scss` file. So, I crossed my fingers, and added a couple of lines around the import:

```scss
.allow-bootstrap {
  @import "~bootstrap/dist/css/bootstrap.min";
}
```

Surprisingly, it worked! Now, everywhere I use an ng-bootstrap component, I just add the `allow-bootstrap` class, and it works perfectly, without changing styles anywhere else on the page.
