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
 * @fileoverview Bar chart component of the React app.
 */

import React, {Component} from 'react';
import * as d3 from 'd3';
import PropTypes from 'prop-types';

const width = 650;
const height = 400;
const margin = {top: 20, right: 5, bottom: 20, left: 35};
const blue = '#52b6ca';

/**
 * Bar chart component.
 */
class BarChart extends Component {
  /**
   *  Constructor to initialize local state.
   *  @param {props} props
   */
  constructor(props) {
    super(props);
    this.state = {
      // Array of rectangles for the bar chart.
      bars: [],
      // Helper functions for d3.
      xScale: d3
        .scaleBand()
        .rangeRound([margin.left, width - margin.right])
        .padding(0.1),
      yScale: d3.scaleLinear().range([height - margin.bottom, margin.top]),
    };
    this.xAxis = d3.axisBottom().scale(this.state.xScale);
    this.yAxis = d3.axisLeft().scale(this.state.yScale);
    this.chartRef = React.createRef();
    this.xAxisRef = React.createRef();
    this.yAxisRef = React.createRef();
  }

  /**
   * Calculate and set bar characteristics based on data from the API.
   * @param {object} nextProps
   * @param {object} prevState
   * @return {object}
   */
  static getDerivedStateFromProps(nextProps, prevState) {
    // Check if data has been loaded.
    if (!nextProps.data) return null;

    const {data} = nextProps;
    const {xScale, yScale} = prevState;

    // Calculate scale domains based on data.
    const prRangeDomain = data.map((d) => d.pr_range);
    const repoCountMax = d3.max(data, (d) => d.repo_count);
    xScale.domain(prRangeDomain);
    yScale.domain([0, repoCountMax]);

    // Calculate bar characteristics based on data.
    const bars = data.map((d) => {
      const y1 = yScale(d.repo_count);
      const y2 = yScale(0);
      return {
        x: xScale(d.pr_range),
        y: y1,
        height: y2 - y1,
        fill: blue,
      };
    });
    return {bars};
  }

  /**
   * Set axes characteristics after the bar characteristics have been set.
   */
  componentDidUpdate() {
    d3.select(this.xAxisRef.current).call(this.xAxis);
    d3.select(this.yAxisRef.current).call(this.yAxis);
  }

  /**
   * Renders the bar chart component using information stored in the local
   * state.
   * @return {object} React element that describes what to render.
   */
  render() {
    return (
      <svg ref={this.chartRef} width={width} height={height}>
        {this.state.bars.map((d, i) => (
          <rect
            key={i}
            x={d.x}
            y={d.y}
            width={this.state.xScale.bandwidth()}
            height={d.height}
            fill={d.fill}
          />
        ))}
        <g>
          <g
            ref={this.xAxisRef}
            transform={`translate(0, ${height - margin.bottom})`}
          />
          <g ref={this.yAxisRef} transform={`translate(${margin.left}, 0)`} />
        </g>
      </svg>
    );
  }
}

BarChart.propTypes = {
  data: PropTypes.array,
};

export default BarChart;
