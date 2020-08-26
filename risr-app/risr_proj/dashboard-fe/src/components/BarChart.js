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
const margin = {
  top: 40,
  right: 5,
  bottom: 50,
  left: 60,
};
const blue = '#52b6ca';

/**
 * Bar chart component. Currently only supports data for the capstone repository
 * pull request counts.
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
    this.barRef = React.createRef();
    this.xAxisRef = React.createRef();
    this.yAxisRef = React.createRef();
  }

  /**
   * Append bars to the SVG chart based on data in the component props.
   */
  drawBars() {
    const {data} = this.props;

    // Check if the data has been loaded and it has the expected 'pr_range' and
    // 'repo_count' keys from the currently supported data set.
    if (
      !data ||
      !data.length ||
      !('pr_range' in data[0]) ||
      !('repo_count' in data[0])
    ) {
      return;
    }

    // Calculate scale domains based on data.
    const {xScale, yScale} = this.state;
    const prRangeDomain = data.map((d) => d.pr_range);
    const repoCountMax = d3.max(data, (d) => d.repo_count);
    xScale.domain(prRangeDomain);
    yScale.domain([0, repoCountMax]);
    d3.select(this.barRef.current)
      .attr('fill', blue)
      .selectAll('rect')
      .data(data)
      .join('rect')
      .attr('x', (d) => xScale(d.pr_range))
      .attr('y', (d) => yScale(d.repo_count))
      .attr('width', xScale.bandwidth())
      .attr('height', (d) => yScale(0) - yScale(d.repo_count));
  }

  /**
   * Draw axes and titles after bars are rendered. Constants for label
   * positions were chosen based on what looked aesthetically pleasing.
   */
  componentDidUpdate() {
    // Add chart bars
    this.drawBars();
    // Add axes
    d3.select(this.xAxisRef.current).call(this.xAxis);
    d3.select(this.yAxisRef.current).call(this.yAxis);
    // Add chart title
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', width / 2 + margin.right)
      .attr('y', margin.top / 2)
      .attr('text-anchor', 'middle')
      .attr('font-size', '20px')
      .text('Capstone Repositories');
    // Add y-axis label
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', margin.top - height / 2)
      .attr('y', margin.left / 3)
      .attr('transform', 'rotate(-90)')
      .attr('text-anchor', 'middle')
      .text('Number of repositories');
    // Add x-axis label
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', width / 2 + margin.right)
      .attr('y', height - margin.bottom / 8)
      .attr('text-anchor', 'middle')
      .text('Number of pull requests');
  }

  /**
   * Renders the bar chart component using information stored in the local
   * state.
   * @return {object} React element that describes what to render.
   */
  render() {
    return (
      <div style={{padding: '20px'}}>
        <svg ref={this.chartRef} width={width} height={height}>
          <g ref={this.barRef} />
          <g
            ref={this.xAxisRef}
            transform={`translate(0, ${height - margin.bottom})`}
          />
          <g ref={this.yAxisRef} transform={`translate(${margin.left}, 0)`} />
        </svg>
      </div>
    );
  }
}

BarChart.propTypes = {
  data: PropTypes.array,
};

export default BarChart;
