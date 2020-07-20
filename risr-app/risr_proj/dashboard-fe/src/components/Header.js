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
 * @fileoverview Header component of the React app.
 */

import React, {Component} from 'react';

/**
 * Header class definition.
 */
class Header extends Component {
  /**
   * Renders the components of the header.
   * @return {Component}
   */
  render() {
    return (
      <div className="text-center">
        <h1>RISR</h1>
      </div>
    );
  }
}

export default Header;
