import { html, render, useState } from  '../preact-lib.js'


  function HelloButton (props) {
    const [count, setCount]  = useState(0);
    const incr = () => setCount((state) => state+1);

    return html`<button onClick=${incr}>Hello ${props.name} ${count}!</button>`;
  }

export default HelloButton;
