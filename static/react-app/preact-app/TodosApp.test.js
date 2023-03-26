// import { html } from  './preact-lib.js'
import htm  from 'https://cdn.skypack.dev/htm';
import {adjust, remove} from 'https://cdn.skypack.dev/ramda';

const html = htm;

// import { render, screen } from '@testing-library/preact';
// import testingLibraryPreact from 'https://cdn.skypack.dev/@testing-library/preact';
import preactTestUtils from 'https://cdn.skypack.dev/preact-test-utils';
import { render  } from 'https://cdn.skypack.dev/@testing-library/preact';



import TodosApp from './TodosApp.js';
const assert = chai.assert;

it('adds 1 + 2 to equal 3', () => {
  assert.equal(1+2, 3);
});
it('adds 1 + 2 to equal 5', () => {
  assert.equal(1+2, 5);
});

describe('TodosApp', () => {
  it('should render', () => {
    const { container } = render(html`<${TodosApp} />}`);
    expect(container.textContent).toMatch('Todos');
  });

});
