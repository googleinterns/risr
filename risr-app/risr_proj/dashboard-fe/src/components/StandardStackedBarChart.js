/* eslint-disable no-invalid-this */
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
 * @fileoverview Stand stacked bar chart component of the React app.
 */

import React, {Component} from 'react';
import * as d3 from 'd3';
import PropTypes from 'prop-types';
import * as Constants from '../constants/index';

// Set the dimensions and margins of the graph
const width = Constants.CHART_WIDTH;
const height = Constants.CHART_HEIGHT;
const margin = {
  top: 30,
  right: 30,
  bottom: 40,
  left: 50,
};

/**
 * Standard stacked bar chart component.
 */
class StandardStackedBarChart extends Component {
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
        .range([margin.left, width - margin.right - Constants.LEGEND_OFFSET])
        .padding(Constants.XSCALE_PADDING),
      yScale: d3.scaleLinear().range([height - margin.bottom, margin.top]),
    };
    this.xAxis = d3.axisBottom().scale(this.state.xScale).tickSizeOuter(0);
    this.yAxis = d3.axisLeft().scale(this.state.yScale);
    this.divRef = React.createRef();
    this.chartRef = React.createRef();
    this.barRef = React.createRef();
    this.xAxisRef = React.createRef();
    this.yAxisRef = React.createRef();
  }

  /**
   * Append bars to the SVG chart based on data in the component props.
   */
  drawBars() {
    const data = JSON.parse(JSON.stringify(this.props.data));

    // Check if the data has been loaded.
    if (!data) return;

    const categories = d3.keys(data[0]).slice(1);

    const weeks = d3
      .map(data, function(d) {
        return d.week;
      })
      .keys();

    const totalCountMax = d3.max(data, function(d) {
      let total = 0;
      for (let i = 0; i < categories.length; i++) {
        const name = categories[i];
        total += +d[name];
      }
      return total;
    });

    // Round up to the nearest ten
    const roundedMax = Math.ceil(totalCountMax / 10) * 10;

    const {xScale, yScale} = this.state;
    xScale.domain(weeks);
    yScale.domain([0, roundedMax]);

    const stackedData = d3.stack().keys(categories)(data);

    const colors = d3.scaleOrdinal().domain(data).range(d3.schemeSet3);

    // Create tooltip
    const tooltip = d3
      .select(this.divRef.current)
      .append('div')
      .style('opacity', 0)
      .attr('class', 'tooltip')
      .style('background-color', 'white')
      .style('border', 'solid')
      .style('border-width', '1px')
      .style('border-radius', '5px')
      .style('padding', '10px');

    const mouseover = function(d) {
      const categoryName = d3.select(this.parentNode).datum().key;
      const categoryValue = d.data[categoryName];
      tooltip
        .html('category: ' + categoryName + '<br> count: ' + categoryValue)
        .style('opacity', 1);
    };
    const mousemove = function(d) {
      tooltip
        .style('left', d3.event.pageX + Constants.TOOLTIP_LEFT + 'px')
        .style('top', d3.event.pageY + 'px');
    };
    const mouseleave = function(d) {
      tooltip.style('opacity', 0);
    };

    d3.select(this.barRef.current)
      .selectAll('g')
      .data(stackedData)
      .enter()
      .append('g')
      .attr('fill', function(d) {
        return colors(d.key);
      })
      .selectAll('rect')
      .data(function(d) {
        return d;
      })
      .enter()
      .append('rect')
      .attr('x', (d) => xScale(d.data.week))
      .attr('y', (d) => yScale(d[1]))
      .attr('width', xScale.bandwidth())
      .attr('height', (d) => yScale(d[0]) - yScale(d[1]))
      .on('mouseover', mouseover)
      .on('mousemove', mousemove)
      .on('mouseleave', mouseleave);

    // Create legend
    const legend = d3
      .select(this.barRef.current)
      .selectAll('.legend')
      .data(categories.reverse())
      .enter()
      .append('g')
      .attr('class', 'legend')
      .attr('transform', function(d, i) {
        return 'translate(0,' + i * Constants.LEGEND_GAP + ')';
      })
      .style('font', '10px sans-serif');

    legend
      .append('rect')
      .attr('x', width - Constants.LEGEND_SQUARE_SIZE)
      .attr('width', Constants.LEGEND_SQUARE_SIZE)
      .attr('height', Constants.LEGEND_SQUARE_SIZE)
      .attr('fill', colors);

    legend
      .append('text')
      .attr('x', width - Constants.LEGEND_TEXT_START)
      .attr('y', Constants.LEGEND_SQUARE_SIZE / 2)
      .attr('dy', Constants.LEGEND_SIZE)
      .attr('text-anchor', 'end')
      .text(function(d) {
        return d;
      });
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
      .attr('font-size', Constants.CHART_TITLE_FONT_SIZE + 'px')
      .text('Comment categories by week');
    // Add y-axis label
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', margin.top / 2 - height / 2)
      .attr('y', margin.left / 3)
      .attr('transform', 'rotate(-90)')
      .attr('text-anchor', 'middle')
      .text('Comment Count');
    // Add x-axis label
    d3.select(this.chartRef.current)
      .append('text')
      .attr('x', width / 2 + margin.right / 2)
      .attr('y', height)
      .attr('text-anchor', 'middle')
      .text('Week');
  }

  /**
   * Renders the stacked bar chart component using information passed in via
   * the component props.
   * @return {object} React element that describes what to render.
   */
  render() {
    return (
      <div ref={this.divRef} style={{padding: Constants.CHART_PADDING + 'px'}}>
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

StandardStackedBarChart.propTypes = {
  data: PropTypes.array,
};

export default StandardStackedBarChart;
