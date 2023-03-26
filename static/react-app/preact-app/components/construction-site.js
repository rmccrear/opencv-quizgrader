import { html, render } from  '../preact-lib.js'

import HelloButton from './HelloButton.js'

console.log('hello');

render(html`<${HelloButton} name="Steve" />`, document.getElementById('hello-button'));
