//import React from 'react';
//import ReactDom from 'react-dom';
import htm from 'https://unpkg.com/htm?module'
const html = htm.bind(React.createElement);

import QuizItemButton from './QuizItemButton.js';
import MyButton from './MyButton.js'

  // <QuizItemButton height="100" width="100" x="543" y="368" quiz-url="/sheet-img/rmcc/109-2--109C1--Midterm-Exam-2/1.jpeg" />
  // <MyButton />,
  // <h2> hello from mod </h2>,

const qProps = {
  height: 80,
  width: 150,
  left: -543,
  top: -368,
  quizUrl: "/sheet-img/rmcc/109-2--109C1--Midterm-Exam-2/1.jpeg",
  score: 0
}

ReactDOM.render(
  // React.createElement(MyButton),
  html`<${MyButton} /> 
  <${QuizItemButton} ...${qProps} />`,
  // html`<button> hello </button>`,
  document.getElementById('quiz-item-button')
);
