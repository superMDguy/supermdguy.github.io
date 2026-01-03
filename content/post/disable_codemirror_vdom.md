---
title: "Getting CMD+F Working in CodeMirror 6"
date: 2026-01-02
tags: ["frontend"]
---

I use a lightweight CodeMirror setup for an editor that has some custom inline badges to represent variable interpolation. Over time though, I noticed that the browser search (<kbd>Cmd+F</kbd>) wouldn't find text in the editor. Finally, I looked into it some more, and realized that it's due to CodeMirror's use of virtual DOM for rendering the editor content. This makes a lot of sense for performance reasons, but for my case it wasn't really needed (I was editing at most ~300 lines).

This was easy to disable in CodeMirror 5 by setting `viewportMargin: Infinity`. However, CodeMirror v6 made this [intentionally](https://discuss.codemirror.net/t/how-to-disable-virtual-scroll-in-code-mirror/8339) [difficult](https://discuss.codemirror.net/t/improve-scroll-performance-tradeoff/8825) (apparently [because a lot of CodeMirror 5 users disabled it and then complained about performance](https://discuss.codemirror.net/t/viewport-issues-with-cm-6/3586/2)).

Finally, with a little help from AI, I found the `viewportMargin` hack still works in CodeMirror 6, just through a different config (`VP.Margin`). Unfortunately, this wasn't something I could monkey-patch at runtime since it was hard-coded into the bundled JavaScript. I didn't want to maintain a fork, so decided to use a Vite plugin to hackily rewrite the relevant parts of the code. This was the first time I'd used Vite like this, so I was pleasantly surprised by how simple it was:

```js
// HACK: Disable CodeMirror virtual DOM by replacing VP.Margin with a huge value
// This forces CodeMirror to render all content instead of virtualizing
function disableCodeMirrorVirtualDom(): Plugin {
  return {
    name: 'disable-codemirror-virtual-dom',
    transform(code, id) {
      if (id.includes('@codemirror/view')) {
        return code.replaceAll('1000 /* VP.Margin */', '1e9 /* VP.Margin (HACKED) */')
      }
    },
  }

export default defineConfig({
  plugins: [
    ...
    disableCodeMirrorVirtualDom(),
    ...
  ],
  ...
})
```

This worked perfectly! Now I can <kbd>Cmd-F</kbd> to my heart's content. And don't worry @marijn, I promise I won't complain about performance.
