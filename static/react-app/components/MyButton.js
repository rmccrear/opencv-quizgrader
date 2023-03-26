import htm from 'https://unpkg.com/htm?module'
const html = htm.bind(React.createElement);

class MyButton extends React.Component {
  render(){
    return (
      html`<button> My Button </button>`
      //React.createElement("button", null, "my b")
    );
  }
}

      //React.createElement("div", null, "hello from my b")
export default MyButton;
