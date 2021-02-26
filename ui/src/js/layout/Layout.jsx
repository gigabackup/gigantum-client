// @flow
// vendor
import React, { Node } from 'react';
// context
import ServerContext from 'Pages/ServerContext';
// component
import Footer from 'Components/footer/Footer';
import Prompt from 'Components/prompt/Prompt';
import Helper from 'Components/helper/Helper';
import Header from './header/Header';
import Sidebar from './sidebar/Sidebar';
// assets
import './Layout.scss';

type Props = {
  auth: Object,
  children: Node,
  showDiskLow: boolean,
}

const Layout = (props: Props) => {
  const { auth, children } = props;
  return (
    <ServerContext.Consumer>
      { value => (
        <div className="Layout">
          <Header {...props} />

          <Sidebar
            {...props}
            currentServer={value.currentServer}

          />

          <main className="Layout__main">
            {children}
          </main>

          <Footer />

          <Helper auth={auth} />

          <Prompt />
        </div>
      )}
    </ServerContext.Consumer>
  );
};


export default Layout;
