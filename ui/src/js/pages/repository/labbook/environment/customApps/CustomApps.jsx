// vendor
import React, { Component } from 'react';
import { createPaginationContainer, graphql } from 'react-relay';
import Tooltip from 'Components/tooltip/Tooltip';
// components
import CustomAppsCard from './card/CustomAppsCard';
// utils
import CustomAppsMutations from './utils/CustomAppsMutations';


type Props = {
  environmentId: string,
  customApps: Array,
  name: string,
  owner: string,
  isLocked: boolean,
}

class CustomApps extends Component<Props> {
  customAppsMutations = new CustomAppsMutations({
    name: this.props.name,
    owner: this.props.owner,
    environmentId: this.props.environmentId,
  });

  render() {
    const { customAppsMutations } = this;
    const {
      customApps,
      name,
      owner,
      isLocked,
    } = this.props;
    return (
      <div className="CustomApps">
        <div className="Environment__headerContainer">
          <h4>
            Custom Apps
            <Tooltip section="customApps" />
          </h4>
        </div>
        <div className="CustomApps__sub-header">
          Configure a Custom App to launch additional tools from this Project's environment.
          {' '}
          <a
            href="https://docs.gigantum.com/docs/custom-apps/"
            rel="noopener noreferrer"
            target="_blank"
          >
            Learn more here.
          </a>
        </div>
        <div className="grid">
          <CustomAppsCard
            name={name}
            owner={owner}
            customApps={customApps}
            customAppsMutations={customAppsMutations}
            isLocked={isLocked}
          />
        </div>
      </div>
    );
  }
}

export default CustomApps;
