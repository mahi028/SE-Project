// apollo.js
import { ApolloClient, createHttpLink, InMemoryCache } from '@apollo/client/core';
import { setContext } from '@apollo/client/link/context';

// 🔗 GraphQL server endpoint
const httpLink = createHttpLink({
  uri: 'http://localhost:5000/graphql', // change to your actual Flask endpoint
});

// 🔐 Auth link to inject token
const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('token'); // or use Pinia/store if stored elsewhere
  return {
    headers: {
      ...headers,
      Authorization: token ? `Bearer ${token}` : "",
    },
  };
});

// 🔧 Apollo Client
export const apolloClient = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
});
