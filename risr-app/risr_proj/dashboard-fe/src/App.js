/*
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0(the "License")
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https: // www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Main React component that defines the app.
 */

import React, {Component, Fragment} from 'react';
import Header from './components/Header';
import Home from './components/Home';
import './App.css';

/**
 * React App class.
 */
class App extends Component {
  /**
   * Renders the components of the React App.
   * @return {React.Fragment}
   */
  render() {
    return (
      <Fragment>
        <Header />
        <Home />
      </Fragment>
    );
  }
}

export default App;
