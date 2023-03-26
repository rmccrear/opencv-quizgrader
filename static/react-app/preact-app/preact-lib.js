// https://unpkg.com/htm@3.0.4/preact/index.mjs?module
// import { h as r, Component as o, render as t } from "https://unpkg.com/preact@latest?module";
// export { h, render, Component } from "https://unpkg.com/preact@latest?module";
// import e from "https://unpkg.com/htm@latest?module";
// var m = e.bind(r);export { m as html };

// import { h as r, Component as o, render as t } from "./preact.module.js";
// export { h, render, Component } from "./preact.module.js";
import { h as r, Component as o, render as t } from "https://cdn.skypack.dev/preact@10";
export { h, render, Component } from "https://cdn.skypack.dev/preact@10";

import e from "./htm.module.js";
var m = e.bind(r);
export { m as html };



export { useState } from "https://cdn.skypack.dev/preact/hooks";
// export { useState } from "./hooks.module.js";
