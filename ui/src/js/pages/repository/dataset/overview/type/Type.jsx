// @flow
// vendor
import React, { useContext } from 'react';
// context
import ServerContext from 'Pages/ServerContext';
// assets
import './Type.scss';


type Props = {
  type: {
    description: string,
    icon: string,
    name: string,
  },
};

const Type = ({
  type,
}: Props) => {
  const {
    description,
    icon,
    name,
  } = type;
  const { currentServer } = useContext(ServerContext);
  const isHub = currentServer.name === 'Gigantum Hub';
  const displayedName = isHub ? name : 'Gigantum';
  const displayedDescription = isHub ? description : 'Versioned Dataset storage supporting individual files up to 5GB in size';
  return (
    <div className="Type">
      <div className="Type__info grid">
        <div className="Type__card Card--auto Card--no-hover column-1-span-12">
          <div className="Type__imageContainer">
            <img
              alt={name}
              className="Type__image"
              height="50"
              width="50"
              src={`data:image/png;base64,${icon}`}
            />
          </div>

          <div className="Type__cardText">
            <div className="Type__title">
              <h6 className="Type__name">{displayedName}</h6>
            </div>
            <div>
              <p className="Type__paragraph">{displayedDescription}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};


export default Type;
