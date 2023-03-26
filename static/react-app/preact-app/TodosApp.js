// import { html, render, useState } from  './preact-lib.js'
import htm from 'https://cdn.skypack.dev/htm';
const html = htm;
import {h , Component, render } from "https://cdn.skypack.dev/preact@10";
import { useState } from "https://cdn.skypack.dev/preact/hooks";
import {adjust, remove} from 'https://cdn.skypack.dev/ramda';


  function TodoItem (props) {
    const notCompleteStyles = {
      color: "blue"
    };
    const completeStyles = {
      color: "salmon",
      textDecoration: "line-through"
    };
    const idx = props.index
    return html`
          <div key=${idx} style=${props.isComplete ? completeStyles : notCompleteStyles}> 
          <span onClick=${() => props.setComplete(idx)}>[V] </span>
             ${props.content}  
          <span onClick=${() => props.deleteTodo(idx)}>[X]</span> 
          </div>`;
  }

  function TodosApp (props) {
    const [toDos, setTodos]  = useState([]);
    const [myTodo, setMyTodo] = useState('');

    const addTodo = () => {
      const newTodo = {
        value: myTodo,
        isComplete: false
      };
      setTodos((toDos)=>toDos.concat(newTodo));
      setMyTodo('');
    };

//     const addTodo = () => setTodos((state) => {
//       const myState = state.concat(
//         {
//           value: myTodo,
//           isComplete: false
//         }
//       );
//       setMyTodo('');
//       return myState;
//     });
    const handleMyTodoChange = (event) => setMyTodo(event.target.value);
    const deleteTodo = (idx) => {
      console.log('deleting', idx);
      // const newTodos = Array.from(toDos);
      // newTodos.splice(idx, 1);
      // setTodos(newTodos);
      setTodos( remove(idx, 1) );
    };
    const setComplete = (idx) => {
//       const todo = {
//         ...toDos[idx],
//         isComplete: !toDos[idx].isComplete
//       };
//       setTodos([
//         ...toDos.slice(0,idx),
//         todo,
//         ...toDos.slice(idx+1)
//       ]);
      // setTodos(adjust(idx, (todo)=>({...todo, isComplete: !todo.isComplete}), toDos));
      // setTodos(adjust(idx, (todo)=>({...todo, isComplete: !todo.isComplete})));
      setTodos(adjust(idx, todo => ({...todo, isComplete: !todo.isComplete}) ));
    };

//     const notCompleteStyles = {
//       color: "blue"
//     };
//     const completeStyles = {
//       color: "salmon",
//       textDecoration: "line-through"
//     };

    return html`
      <input type="text" onChange=${handleMyTodoChange} value=${myTodo}></div>
      <button onClick=${addTodo}>Add Todo</button>
      <div>
        ${toDos.map((todo, idx) => html`<${TodoItem} ...${
          {deleteTodo, setComplete, content: todo.value, index: idx, isComplete: todo.isComplete}
        }  />`
//           html`
//           <div key=${idx} style=${todo.isComplete ? completeStyles : notCompleteStyles}> 
//           <span onClick=${() => setComplete(idx)}>[V] </span>
//              ${todo.value}  
//           <span onClick=${() => deleteTodo(idx)}>[X]</span> 
//           </div>`
        )}
      </div>
      `;
  }

render(html`<${TodosApp} />`, document.getElementById('todos-app'));

export default TodosApp;
