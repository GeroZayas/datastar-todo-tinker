class MyGreeting extends HTMLElement {
      // This runs when the element is created
      constructor() {
        super(); // always call super() first
        this.innerHTML = `<h1>This is my custom element!</h1>`;
      }
    }

    // Tell the browser about our new tag
    customElements.define('my-greeting', MyGreeting);