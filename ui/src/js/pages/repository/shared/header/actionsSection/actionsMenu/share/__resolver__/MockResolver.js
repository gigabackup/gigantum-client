// index's for ids
let countDatasets = 0;
let countProjects = 0;
const countRepository = 0;

// mock data for accurate id names
const ownerRepositoryData = [
  {
    owner: 'gigantum-examples',
    name: 'scikit-learn-in-gigantum',
  },
  {
    owner: 'gigantum-examples',
    name: 'pytorch-in-gigantum',
  },
  {
    owner: 'gigantum-examples',
    name: 'exploring-nih-grant-data',
  },
  {
    owner: 'gigantum-examples',
    name: 'textgenrnn-in-gigantum',
  },
  {
    owner: 'tiny-dav',
    name: 'io-benchmarks',
  },
  {
    owner: 'dmk',
    name: 'gigaleaf-example',
  },
  {
    owner: 'jhupp',
    name: 'assignment-0-0-gigantum',
  },
  {
    owner: 'tiny-dav',
    name: 'covid19-demo-project',
  },
  {
    owner: 'tiny-dav',
    name: 'football-skin-tone',
  },
  {
    owner: 'gigantum',
    name: 'my-first-project',
  },
  {
    owner: 'gigantum-dev',
    name: 'dummy-project',
  },
  {
    owner: 'gigantum-dev',
    name: 'my-first-project',
  },
];

const targetProject = (generateId, index = 0) => {
  const { owner, name } = ownerRepositoryData[index];
  const id = btoa(`${owner}&${name}`);
  return ({
    __typename: 'Project',
    id,
    owner,
    name,
    description: 'this is and example',
    modifiedOnUtc: '2019-10-14T18:17:11.255Z',
    visibility: 'Public',
  });
};

const targetNode = (generateId, index = 0, typename = 'Project') => {
  const cursor = `MA1${index}`;
  const { owner, name } = ownerRepositoryData[index];
  const id = btoa(`${typename}&${owner}&${name}`);
  return (
    {
      node: {
        __typename: typename,
        id,
        owner,
        name,
        description: 'this is and example',
        modifiedOnUtc: '2019-10-14T18:17:11.255Z',
        visibility: 'Public',
        overview: (typename === 'Dataset')
          ? {
            fileTypeDistribution: ['0.2|.jpeg', '0.2|.png', '0.6|.csv'],
            id: `overview-${generateId()}`,
          }
          : undefined,
      },
      cursor,
    }
  );
};

const mockResolver = {
  ID(_, generateId) {
    // See, the second page IDs will be different
    return `node-${generateId()}`;
  },
  Labbook() {
    const index = countProjects % 12;
    const { owner, name } = ownerRepositoryData[index];
    const id = btoa(`projects&${owner}&${name}${countProjects}`);

    countProjects += 1;
    return (
      {
        labbook: {
          id,
          owner: 'ownername',
          name: 'projectname',
          description: 'this is a project',
          modifiedOnUtc: 'Fri, 02 Feb 1996 03:04:05 GMT',
          visibility: 'Public',
          code: {
            allFiles: {
              edges: [
                {
                  node: {
                    key: 'code/move-batch.ipynb',

                  },
                  cursor: 'MA01',
                },
                {
                  node: {
                    key: 'code/batch.ipynb',
                  },
                  cursor: 'MA02',
                },
                {
                  node: {
                    key: 'code/sync.ipynb',
                  },
                  cursor: 'MA02',
                },
              ],
            },
          },
          pageInfo: {
            hasNextPage: false,
            startCursor: 'MA01',
            endCursor: 'MA03',
            hasPreviousPage: false,
          },
        },
      }
    );
  },
  LabbookFileConnection(_, generateId) {
    return {
      edges: [
        {
          node: {
            sDir: false,
            id: `LabbookFileEdge-${generateId()}`,
            key: 'code/batch.ipynb',
            size: 450,
          },
        },
        {
          node: {
            isDir: false,
            id: `LabbookFileEdge-${generateId()}`,
            key: 'code/watch.ipynb',
            size: 450,
          },
        },
        {
          node: {
            isDir: false,
            id: `LabbookFileEdge-${generateId()}`,
            key: 'code/fun.ipynb',
            size: 450,

          },
        },
      ],
    };
  },
  LabbookSection() {
    return {
      code: {
        section: 'code',
        id: 'rand',
        allFiles: {
          edges: [
            {
              node: {
                key: 'code/move-batch.ipynb',

              },
              cursor: 'MA01',
            },
            {
              node: {
                key: 'code/batch.ipynb',
              },
              cursor: 'MA02',
            },
            {
              node: {
                key: 'code/sync.ipynb',
              },
              cursor: 'MA02',
            },
          ],
        },
        hasFiles: true,
      },
    };
  },
  // LabbookFile(_, generateId) {
  //   return {
  //     key: `code/${generateId()}batch.ipynb`,
  //   };
  // },
  Dataset() {
    const index = countDatasets % 12;
    const { owner, name } = ownerRepositoryData[index];
    const id = btoa(`datasets&${owner}&${name}${countDatasets}`);

    countDatasets += 1;
    return (
      {
        id,
        owner,
        name,
        description: 'this is a project',
        modifiedOnUtc: 'Fri, 02 Feb 1996 03:04:05 GMT',
        visibility: 'Public',
        overview: {
          fileTypeDistribution: ['0.2|.jpeg', '0.2|.png', '0.6|.csv'],
        },
      }
    );
  },
  PageInfo() {
    return (
      {
        hasNextPage: true,
      }
    );
  },
};

export default mockResolver;
