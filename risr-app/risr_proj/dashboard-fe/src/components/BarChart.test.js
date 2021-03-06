// /*
//  * Copyright 2020 Google LLC
//  *
//  * Licensed under the Apache License, Version 2.0(the "License")
//  * you may not use this file except in compliance with the License.
//  * You may obtain a copy of the License at
//  *
//  *     https: // www.apache.org/licenses/LICENSE-2.0
//  *
//  * Unless required by applicable law or agreed to in writing, software
//  * distributed under the License is distributed on an "AS IS" BASIS,
//  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  * See the License for the specific language governing permissions and
//  * limitations under the License.
//  */

import React from 'react';
import {shallow, mount} from 'enzyme';
import BarChart from './BarChart';

const cheerio = require('cheerio');

describe('Bar chart component', () => {
  test('renders a svg element', () => {
    const shallowChart = shallow(<BarChart />);
    expect(shallowChart.find('svg')).toHaveLength(1);
    expect(shallowChart.find('g')).toHaveLength(3);
  });

  test('renders four rectangles with the same height', () => {
    const data = [
      {pr_range: '0-1', repo_count: 10},
      {pr_range: '2-3', repo_count: 10},
      {pr_range: '4-5', repo_count: 10},
      {pr_range: '6-7', repo_count: 10},
    ];
    const shallowChart = mount(<BarChart />);
    shallowChart.setProps({data: data});
    const $ = cheerio.load(shallowChart.html());
    const bars = $('rect').children();
    expect($('rect')).toHaveLength(4);
    const firstHeight = bars.first().attr('height');
    bars.each((bar) => {
      expect(bar.attr('height')).toEqual(firstHeight);
    });
  });

  test('renders three text labels for the chart', () => {
    const data = [
      {pr_range: '0-1', repo_count: 10},
      {pr_range: '2-3', repo_count: 10},
      {pr_range: '4-5', repo_count: 10},
      {pr_range: '6-7', repo_count: 10},
    ];
    const shallowChart = mount(<BarChart />);
    shallowChart.setProps({data: data});
    const $ = cheerio.load(shallowChart.html());
    expect($('svg').children('text')).toHaveLength(3);
  });
});
