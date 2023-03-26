// import htm from 'https://unpkg.com/htm?module'
// const html = htm.bind(React.createElement);
import React from 'react';

class QuizItemButton extends React.Component {

  myStyle() {
    return {
        height: this.props.height + 'px',
        width:  this.props.width +'px',
        backgroundPosition: `left -${this.props.y}px top -${this.props.x}px`, // left -543px top -368px;
        backgroundImage:  `url(${this.props.quizUrl})`, // `url(/sheet-img/rmcc/109-2--109C1--Midterm-Exam-2/1.jpeg)`;
        backgroundRepeat: 'no-repeat',
        backgroundSize: 'auto'
    };
  }

  render() {
    return (
      html`
      <div>
        <div style=${this.myStyle()}></div>
      </div>`
    );
  }
}

export default QuizItemButton;
