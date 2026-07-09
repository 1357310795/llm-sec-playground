import '@mantine/core/styles.css';

import React from 'react';
import ReactDOM from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import App from './App';

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <MantineProvider defaultColorScheme="light">
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </MantineProvider>
    </QueryClientProvider>
  </React.StrictMode>,
);
