import { Tasks } from './tasksIO';
import { Notes } from './notesIO';
import { Tags } from './tagsIO';
import { Categories } from './categoriesIO';
import { User } from './userIO';

// Eslint no-undef exceptions
/* global Headers */
/* global Blob */

class IO {
  constructor () {
    this.headers = null;
    this.root = './api';

    this.user = null;
    this.userSettings = null;
    this.tasks = null;
    this.notes = null;
    this.tags = null;
    this.milestones = null;
    this.worklog = null;

    // this.initialized = fetch('./api/settings/', {
    // credentials: 'same-origin'
    // })
    const dummyFetch = async function () {
      return {
        json () {
          return { csrftoken: '' };
        }
      };
    };

    this.initialized = dummyFetch()
      .then(v => v.json())
      .then(data => {
        this.headers = new Headers({
          'X-CSRFToken': data.csrftoken
        });
        this.updateHeader();

        this.user = new User(this);
        this.userSettings = null;
        this.tasks = new Tasks(this);
        this.notes = new Notes(this);
        this.tags = new Tags(this);
        this.categories = new Categories(this);
        this.milestones = null;
        this.worklog = null;
      });
  }
  toJson (data) {
    return {
      body: new Blob([JSON.stringify(data)], { type: 'application/json' }),
      headers: this.headers
    };
  }
  updateHeader () {
    const token = localStorage.getItem('token');
    // console.log('Token', { token, self: this });
    this.headers.set('Authorization', token ? 'Bearer ' + token : null);
  }
}

export default new IO();
