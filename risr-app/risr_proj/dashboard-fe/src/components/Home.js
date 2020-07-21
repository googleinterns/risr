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
 * @fileoverview Home component of the React app.
 */

import React, {Component} from 'react';
import {Container} from 'reactstrap';
import BarChart from './BarChart';

import axios from 'axios';

import {API_URL} from '../constants';

/**
 * Home component.
 */
class Home extends Component {
  /**
   * Constructor to initialize local state.
   * @param {props} props
   */
  constructor(props) {
    super(props);
    this.state = {
      data: [],
    };
  }

  /**
   * Load data from the dashboard API into local state.
   */
  componentDidMount() {
    axios
      .get(API_URL)
      .then((res) => {
        this.setState({data: JSON.parse(res.data)});
      })
      .catch((error) => {
        console.log(error);
      });
  }

  /**
   * Render the home component using data from the API.
   * @return {Component} Home component.
   */
  render() {
    return (
      <Container style={{marginTop: '20px'}} className='text-center'>
        <BarChart data={this.state.data} />
      </Container>
    );
  }
}

export default Home;
