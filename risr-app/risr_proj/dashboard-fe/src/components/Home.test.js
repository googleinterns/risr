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

import axios from 'axios';
import React from 'react';
import {mount} from 'enzyme';
import Home from './Home';
import BarChart from './BarChart';
import {API_URL} from '../constants';

jest.mock('axios');

describe('Home component', () => {
  test('renders a bar chart component', async () => {
    const resData = {
      data: '{"bar_data": [{"test": "0"}], "stacked_data": [{"test": "1"}]}',
    };
    const spy = jest.spyOn(Home.prototype, 'componentDidMount');
    axios.get.mockImplementation(() => Promise.resolve(resData));
    const shallowHome = await mount(<Home />);
    expect(spy).toHaveBeenCalled();
    expect(shallowHome.find(BarChart)).toHaveLength(1);
  });

  test('updates state with data from the API', async () => {
    const resData = {
      data: '{"bar_data": [{"test": "0"}], "stacked_data": [{"test": "1"}]}',
    };
    axios.get.mockImplementation(() => Promise.resolve(resData));
    const stateData = {bar_data: [{test: '0'}], stacked_data: [{test: '1'}]};
    const shallowHome = await mount(<Home />);
    expect(axios.get).toHaveBeenCalledWith(API_URL);
    expect(shallowHome.state('data')).toEqual(stateData);
  });

  test('catches errors from API request', async () => {
    const errorMessage = 'Request error';
    jest.spyOn(console, 'log').mockImplementation();
    axios.get.mockImplementation(() => Promise.reject(new Error(errorMessage)));
    const shallowHome = await mount(<Home />);
    expect(shallowHome.state('data')).toEqual([]);
  });
});
