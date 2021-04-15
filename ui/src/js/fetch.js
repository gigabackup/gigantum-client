

function fetchQuery(apiURL) {
  const headers = {};
  headers.Accept = 'application/json';
  headers['Content-Type'] = 'application/json';
  headers['Access-Control-Allow-Origin'] = '*';
  headers['Cache-Control'] = 'no-cache';

  return fetch(apiURL, {
    method: 'GET',
    headers,
  }).then(response => response.json())
    .catch(error => error);
}

export default fetchQuery;
