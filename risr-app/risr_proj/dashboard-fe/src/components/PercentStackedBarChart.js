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
 * @fileoverview Percent stacked bar chart component of the React app.
 */

import React, {Component} from 'react';
import * as d3 from 'd3';
import PropTypes from 'prop-types';
import {color} from 'd3';

// Set the dimensions and margins of the graph
const margin = {
  top: 30,
  right: 30,
  bottom: 40,
  left: 50,
};
const width = 650;
const height = 400;

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
        .range([margin.left, width - margin.right])
        .padding(0.2),
      yScale: d3
        .scaleLinear()
        .range([height - margin.bottom, margin.top])
        .domain([0, 100]),
    };
    this.xAxis = d3.axisBottom().scale(this.state.xScale).tickSizeOuter(0);
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

    // Check if the data has been loaded.
    if (!data) return;

    const categories = d3.keys(data[0]).slice(1);

    const weeks = d3
      .map(data, function (d) {
        return d.group;
      })
      .keys();

    const {xScale, yScale} = this.state;
    xScale.domain(weeks);

    data.forEach(function (d) {
      let total = 0;
      for (let cat in categories) {
        const name = categories[cat];
        total += +d[name];
      }
      for (let cat in categories) {
        const name = categories[cat];
        d[name] = (d[name] / total) * 100;
      }
    });

    const stackedData = d3.stack().keys(categories)(data);
    const colors = d3.scaleOrdinal().domain(data).range(d3.schemeSet3);

    d3.select(this.barRef.current)
      .selectAll('g')
      .data(stackedData)
      .enter()
      .append('g')
      .attr('fill', function (d) {
        return colors(d.key);
      })
      .selectAll('rect')
      .data(function (d) {
        return d;
      })
      .enter()
      .append('rect')
      .attr('x', (d) => xScale(d.data.group))
      .attr('y', (d) => yScale(d[1]))
      .attr('width', xScale.bandwidth())
      .attr('height', (d) => yScale(d[0]) - yScale(d[1]));
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
      .attr('x', width / 2)
      .attr('y', margin.top / 2)
      .attr('text-anchor', 'middle')
      .attr('font-size', '20px')
      .text('Comment categories by week');
    // Add y-axis label
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', margin.top - height / 2)
      .attr('y', margin.left / 3)
      .attr('transform', 'rotate(-90)')
      .attr('text-anchor', 'middle')
      .text('Percentage');
    // Add x-axis label
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', width / 2 + margin.right)
      .attr('y', height)
      .attr('text-anchor', 'middle')
      .text('Week');
  }

  /**
   * Renders the bar chart component using information stored in the local
   * state.
   * @return {object} React element that describes what to render.
   */
  render() {
    return (
      <svg ref={this.chartRef} width={width} height={height}>
        <g ref={this.barRef} />
        <g
          ref={this.xAxisRef}
          transform={`translate(0, ${height - margin.bottom})`}
        />
        <g ref={this.yAxisRef} transform={`translate(${margin.left}, 0)`} />
      </svg>
    );
  }
}

BarChart.propTypes = {
  data: PropTypes.array,
};

export default BarChart;
